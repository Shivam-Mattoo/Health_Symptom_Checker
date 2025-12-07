from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langgraph.graph import StateGraph, END
from typing import List, Dict, Optional, TypedDict
from pydantic import BaseModel, Field
from config import Config
import logging
import json
import re

logger = logging.getLogger(__name__)

# Define structured output models
class SymptomAnalysis(BaseModel):
    """Structured output for symptom analysis"""
    conditions: List[str] = Field(
        description="List of 3-5 possible conditions in order of likelihood"
    )
    recommendations: List[str] = Field(
        description="List of recommended next steps"
    )
    severity_assessment: str = Field(
        description="Brief assessment of symptom severity (mild, moderate, severe)"
    )


# Define state for LangGraph
class SymptomAnalysisState(TypedDict):
    """State for symptom analysis workflow"""
    symptoms: str
    context: Optional[List[str]]
    analysis: Optional[SymptomAnalysis]
    error: Optional[str]


class LLMService:
    """Service class for Gemini LLM operations using LangChain and LangGraph"""
    
    def __init__(self):
        """Initialize LangChain with Gemini LLM"""
        if not Config.GEMINI_KEY:
            raise ValueError("GEMINI_KEY is not set in environment variables. Please check your .env file.")
        
        # Use gemini-2.0-flash-exp (tested working model)
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=Config.GEMINI_KEY,
                temperature=0.7,
            )
            logger.info("[LLM SERVICE] ✅ Initialized with gemini-2.0-flash-exp")
            print("✅ Gemini LLM initialized: gemini-2.0-flash-exp")
        except Exception as e:
            logger.warning(f"[LLM SERVICE] Failed to initialize with gemini-2.0-flash-exp: {e}, trying gemini-1.5-flash")
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=Config.GEMINI_KEY,
                    temperature=0.7,
                )
                logger.info("[LLM SERVICE] ✅ Initialized with gemini-1.5-flash")
                print("✅ Gemini LLM initialized: gemini-1.5-flash")
            except Exception as e2:
                logger.error(f"[LLM SERVICE] Failed to initialize any Gemini model: {e2}")
                raise ValueError(f"Could not initialize Gemini. Check API key and model availability.")
        self.output_parser = PydanticOutputParser(pydantic_object=SymptomAnalysis)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for symptom analysis"""
        
        # Create the graph
        workflow = StateGraph(SymptomAnalysisState)
        
        # Add nodes
        workflow.add_node("analyze_symptoms", self._analyze_symptoms_node)
        workflow.add_node("format_response", self._format_response_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_symptoms")
        
        # Add edges
        workflow.add_edge("analyze_symptoms", "format_response")
        workflow.add_edge("format_response", END)
        
        # Compile the graph
        return workflow.compile()
    
    def _analyze_symptoms_node(self, state: SymptomAnalysisState) -> SymptomAnalysisState:
        """Node to analyze symptoms using LLM"""
        try:
            logger.info("[LLM SERVICE] Starting symptom analysis")
            logger.info(f"[LLM SERVICE] Symptoms: {state['symptoms'][:200]}...")
            
            # Format context
            context_text = ""
            if state.get("context"):
                context_text = "\n\nRelevant medical information from similar cases:\n" + "\n".join(state["context"])
                logger.info(f"[LLM SERVICE] Using context from {len(state['context'])} similar cases")
            
            # Simplified prompt - direct text response
            prompt_text = f"""ANALYZE THE FOLLOWING SYMPTOMS NOW:

Symptoms: {state['symptoms']}
{context_text}

IMPORTANT: This is for educational purposes only. Not medical advice.

Provide your analysis in EXACTLY this format:

CONDITIONS:
1. [Specific condition name]
2. [Specific condition name]
3. [Specific condition name]
4. [Specific condition name]
5. [Specific condition name]

RECOMMENDATIONS:
1. [Specific actionable step]
2. [Specific actionable step]
3. [Specific actionable step]
4. [Specific actionable step]
5. [Specific actionable step]

SEVERITY: [mild OR moderate OR severe]

Start your response with "CONDITIONS:" immediately. Do not explain or acknowledge - just analyze."""

            logger.info("[LLM SERVICE] Invoking LLM with simplified prompt...")
            
            # Use simple text chain - more reliable
            try:
                # Create a simple prompt chain
                from langchain_core.messages import HumanMessage, SystemMessage
                
                system_msg = SystemMessage(content="You are a medical AI that analyzes symptoms. You MUST respond in the exact format requested. Never acknowledge, explain, or ask questions - just provide the analysis immediately in the specified format. Start every response with 'CONDITIONS:'")
                human_msg = HumanMessage(content=prompt_text)
                
                logger.info("[LLM SERVICE] Invoking LLM with messages...")
                response = self.llm.invoke([system_msg, human_msg])
                logger.info(f"[LLM SERVICE] Received LLM response, type: {type(response)}")
                
                # Extract text from response
                if hasattr(response, 'content'):
                    response_text = response.content
                elif isinstance(response, str):
                    response_text = response
                elif hasattr(response, 'text'):
                    response_text = response.text
                else:
                    response_text = str(response)
                
                logger.info(f"[LLM SERVICE] Response text length: {len(response_text)}")
                logger.info(f"[LLM SERVICE] Response preview: {response_text[:500]}...")
                
                if not response_text or len(response_text.strip()) < 10:
                    raise ValueError("LLM returned empty or very short response")
                
                # Check if LLM is just acknowledging instead of analyzing
                acknowledgment_phrases = ["okay, i understand", "i will analyze", "i can help", "let me analyze", "i'll provide"]
                if any(phrase in response_text.lower()[:200] for phrase in acknowledgment_phrases) and "CONDITIONS:" not in response_text.upper():
                    logger.warning("[LLM SERVICE] LLM acknowledged but didn't analyze. Retrying with stronger prompt...")
                    
                    # Retry with direct command
                    retry_msg = HumanMessage(content=f"STOP. Do NOT acknowledge. ANALYZE THESE SYMPTOMS NOW: {state['symptoms']}\n\nStart your response with 'CONDITIONS:' followed by numbered list. Then 'RECOMMENDATIONS:' followed by numbered list. Then 'SEVERITY:' with one word.")
                    response = self.llm.invoke([system_msg, retry_msg])
                    response_text = response.content if hasattr(response, 'content') else str(response)
                    logger.info(f"[LLM SERVICE] Retry response: {response_text[:300]}...")
                
                # Parse the response
                analysis = self._parse_text_response(response_text)
                logger.info(f"[LLM SERVICE] Parsed analysis - Conditions: {len(analysis.conditions)}, Recommendations: {len(analysis.recommendations)}")
                state["analysis"] = analysis
                state["error"] = None
                
            except Exception as llm_error:
                logger.error(f"[LLM SERVICE] LLM invocation failed: {str(llm_error)}")
                import traceback
                logger.error(f"[LLM SERVICE] LLM Error Traceback: {traceback.format_exc()}")
                # Try to get more details about the error
                if "api" in str(llm_error).lower() or "key" in str(llm_error).lower() or "auth" in str(llm_error).lower():
                    logger.error("[LLM SERVICE] This appears to be an API key or authentication error. Please check your GEMINI_KEY in the .env file.")
                raise
            
        except Exception as e:
            logger.error(f"[LLM SERVICE] Error in analyze_symptoms_node: {str(e)}")
            import traceback
            logger.error(f"[LLM SERVICE] Full Traceback: {traceback.format_exc()}")
            state["error"] = str(e)
            # Provide fallback analysis
            state["analysis"] = SymptomAnalysis(
                conditions=["Unable to analyze symptoms. Please consult a healthcare professional."],
                recommendations=["Seek immediate medical attention if symptoms are severe."],
                severity_assessment="Unable to assess"
            )
        
        return state
    
    def _parse_text_response(self, response_text: str) -> SymptomAnalysis:
        """Parse text response into structured format"""
        logger.info("[LLM SERVICE] Parsing text response...")
        logger.info(f"[LLM SERVICE] Full response: {response_text}")
        
        # Try to extract JSON from response first
        try:
            # Look for JSON in the response (more flexible pattern)
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*"conditions"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_match = re.search(json_pattern, response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # Try to fix common JSON issues
                json_str = json_str.replace("'", '"')
                data = json.loads(json_str)
                logger.info("[LLM SERVICE] Successfully parsed JSON response")
                return SymptomAnalysis(
                    conditions=data.get("conditions", []),
                    recommendations=data.get("recommendations", []),
                    severity_assessment=data.get("severity_assessment", "moderate")
                )
        except Exception as e:
            logger.warning(f"[LLM SERVICE] JSON extraction failed: {e}, trying text parsing")
        
        # Parse from structured text format
        conditions = []
        recommendations = []
        severity = "moderate"
        
        lines = response_text.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers (case insensitive)
            line_lower = line.lower()
            if 'condition' in line_lower and (':' in line or line_lower.startswith('condition')):
                current_section = 'conditions'
                logger.info(f"[LLM SERVICE] Found CONDITIONS section at line {i}")
                continue
            elif ('recommendation' in line_lower or 'next step' in line_lower) and (':' in line or line_lower.startswith('recommendation')):
                current_section = 'recommendations'
                logger.info(f"[LLM SERVICE] Found RECOMMENDATIONS section at line {i}")
                continue
            elif 'severity' in line_lower:
                if 'mild' in line_lower:
                    severity = "mild"
                elif 'severe' in line_lower:
                    severity = "severe"
                elif 'moderate' in line_lower:
                    severity = "moderate"
                logger.info(f"[LLM SERVICE] Found SEVERITY: {severity}")
                continue
            
            # Extract numbered items (1., 2., etc.)
            if re.match(r'^\d+[\.\)]\s+', line):
                content = re.sub(r'^\d+[\.\)]\s+', '', line).strip()
                if content and len(content) > 5:
                    if current_section == 'conditions' and len(conditions) < 5:
                        conditions.append(content)
                        logger.info(f"[LLM SERVICE] Extracted condition: {content[:50]}...")
                    elif current_section == 'recommendations' and len(recommendations) < 5:
                        recommendations.append(content)
                        logger.info(f"[LLM SERVICE] Extracted recommendation: {content[:50]}...")
            # Extract bullet points or dashes
            elif re.match(r'^[-•*]\s+', line):
                content = re.sub(r'^[-•*]\s+', '', line).strip()
                if content and len(content) > 5:
                    if current_section == 'conditions' and len(conditions) < 5:
                        conditions.append(content)
                    elif current_section == 'recommendations' and len(recommendations) < 5:
                        recommendations.append(content)
            # Extract lines that look like content (not headers)
            elif current_section and len(line) > 10 and not line.isupper():
                if current_section == 'conditions' and len(conditions) < 5 and line[0].isupper():
                    conditions.append(line)
                elif current_section == 'recommendations' and len(recommendations) < 5 and line[0].isupper():
                    recommendations.append(line)
        
        # If we didn't find structured format, try pattern matching
        if not conditions:
            logger.warning("[LLM SERVICE] No conditions found in structured format, trying pattern matching")
            conditions = self._extract_conditions_from_text(response_text)
        if not recommendations:
            logger.warning("[LLM SERVICE] No recommendations found in structured format, trying pattern matching")
            recommendations = self._extract_recommendations_from_text(response_text)
        
        # Final fallback - ensure we have something
        if not conditions:
            logger.error("[LLM SERVICE] No conditions extracted, using fallback")
            conditions = ["Consult a healthcare professional for proper diagnosis"]
        if not recommendations:
            logger.error("[LLM SERVICE] No recommendations extracted, using fallback")
            recommendations = ["Seek professional medical advice from a qualified healthcare provider"]
        
        logger.info(f"[LLM SERVICE] Final parsed result - Conditions: {len(conditions)}, Recommendations: {len(recommendations)}, Severity: {severity}")
        
        return SymptomAnalysis(
            conditions=conditions[:5],
            recommendations=recommendations[:5],
            severity_assessment=severity
        )
    
    def _extract_conditions_from_text(self, text: str) -> List[str]:
        """Extract conditions from text using pattern matching"""
        conditions = []
        # Look for common medical condition patterns
        patterns = [
            r'(?:possible|likely|probable|potential)\s+(?:condition|diagnosis|disease|illness)[s]?[:\s]+([^\.\n]+)',
            r'(?:could be|might be|may be)\s+([A-Z][^\.\n]+)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            conditions.extend([m.strip() for m in matches if len(m.strip()) > 5])
        return conditions[:5]
    
    def _extract_recommendations_from_text(self, text: str) -> List[str]:
        """Extract recommendations from text"""
        recommendations = []
        # Look for action items
        patterns = [
            r'(?:recommend|suggest|advise|should|next step)[s]?[:\s]+([^\.\n]+)',
            r'(?:see|consult|visit|contact)\s+([^\.\n]+)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            recommendations.extend([m.strip() for m in matches if len(m.strip()) > 5])
        return recommendations[:5] if recommendations else ["Consult a healthcare professional"]
    
    def _format_response_node(self, state: SymptomAnalysisState) -> SymptomAnalysisState:
        """Node to format the final response"""
        # Response is already formatted in the analysis object
        # This node can be used for additional formatting if needed
        return state
    
    def generate_symptom_analysis(self, symptoms: str, context: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Generate probable conditions and recommendations based on symptoms using LangGraph
        
        Args:
            symptoms: User input symptoms
            context: Optional context from RAG (Pinecone)
        
        Returns:
            Dictionary with 'conditions' and 'recommendations' lists
        """
        try:
            # Initialize state
            initial_state: SymptomAnalysisState = {
                "symptoms": symptoms,
                "context": context,
                "analysis": None,
                "error": None
            }
            
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Extract analysis
            if final_state.get("analysis"):
                analysis = final_state["analysis"]
                return {
                    "conditions": analysis.conditions,
                    "recommendations": analysis.recommendations,
                    "severity": analysis.severity_assessment
                }
            else:
                # Fallback if analysis failed
                return {
                    "conditions": ["Unable to analyze symptoms. Please consult a healthcare professional."],
                    "recommendations": ["Seek immediate medical attention if symptoms are severe."],
                    "severity": "Unable to assess"
                }
        
        except Exception as e:
            logger.error(f"[LLM SERVICE] Error generating LLM response: {str(e)}")
            import traceback
            logger.error(f"[LLM SERVICE] Traceback: {traceback.format_exc()}")
            return {
                "conditions": ["Unable to analyze symptoms. Please consult a healthcare professional."],
                "recommendations": ["Seek immediate medical attention if symptoms are severe."],
                "severity": "Unable to assess"
            }
