from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional
from services.database_service import DatabaseService
from services.llm_service import LLMService
from services.pinecone_service import PineconeService
from services.pdf_service import PDFService
from services.image_service import ImageService
from Routes.auth_routes import get_current_user
from models.user import User
import hashlib
import uuid

router = APIRouter(prefix="/api/symptoms", tags=["symptoms"])

# Initialize services lazily (in production, use dependency injection)
_db_service = None
_llm_service = None
_pinecone_service = None

def get_db_service():
    """Get or create database service instance"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service

def get_llm_service():
    """Get or create LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

def get_pinecone_service():
    """Get or create Pinecone service instance"""
    global _pinecone_service
    if _pinecone_service is None:
        _pinecone_service = PineconeService()
    return _pinecone_service

def get_pdf_service():
    """Get PDF service instance"""
    return PDFService()

def get_image_service():
    """Get image service instance"""
    return ImageService()


class SymptomRequest(BaseModel):
    """Request model for symptom analysis"""
    symptoms: str = Field(..., min_length=1, description="User input symptoms")
    user_id: Optional[str] = Field(None, description="Optional user identifier")


class SymptomResponse(BaseModel):
    """Response model for symptom analysis"""
    query_id: str
    symptoms: str
    conditions: List[str]
    recommendations: List[str]
    severity: Optional[str] = None
    disclaimer: str = "This information is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider."


class HistoryResponse(BaseModel):
    """Response model for query history"""
    queries: List[dict]


@router.post("/analyze", response_model=SymptomResponse)
async def analyze_symptoms(
    request: SymptomRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze symptoms and return probable conditions and recommendations (Requires Authentication)
    
    Args:
        request: SymptomRequest containing symptoms
        current_user: Authenticated user from JWT token
    
    Returns:
        SymptomResponse with analysis results
    """
    print(f"\n🏥 Symptom analysis request from: {current_user.email}")
    print(f"   Symptoms: {request.symptoms[:100]}...")
    
    try:
        # Get service instances
        db_service = get_db_service()
        llm_service = get_llm_service()
        pinecone_service = get_pinecone_service()
        
        # Generate embedding for RAG search
        embedding = pinecone_service.generate_embedding(request.symptoms)
        
        # Search for similar symptoms in Pinecone
        similar_contexts = pinecone_service.search_similar_symptoms(embedding, top_k=3)
        
        # Extract context from similar symptoms
        context = []
        if similar_contexts:
            for ctx in similar_contexts:
                context.append(f"Similar case: {ctx['symptoms']} - Conditions: {', '.join(ctx['conditions'])}")
        
        # Generate analysis using LLM
        analysis = llm_service.generate_symptom_analysis(request.symptoms, context if context else None)
        
        # Save to user's symptom history
        query_id = db_service.save_symptom_history(
            user_id=current_user.id,
            symptoms=request.symptoms,
            severity=analysis.get("severity", "Unknown"),
            conditions=analysis["conditions"],
            recommendations=analysis["recommendations"]
        )
        
        # Optionally add to Pinecone for future RAG
        if analysis["conditions"] and analysis["recommendations"]:
            try:
                pinecone_service.add_symptom_context(
                    symptoms=request.symptoms,
                    conditions=analysis["conditions"],
                    recommendations=analysis["recommendations"],
                    embedding=embedding
                )
            except Exception as e:
                print(f"Error adding to Pinecone: {e}")
        
        return SymptomResponse(
            query_id=query_id or "no-id",
            symptoms=request.symptoms,
            conditions=analysis["conditions"],
            recommendations=analysis["recommendations"],
            severity=analysis.get("severity")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing symptoms: {str(e)}")


@router.get("/history", response_model=HistoryResponse)
async def get_history(user_id: Optional[str] = None, limit: int = 10):
    """
    Get query history
    
    Args:
        user_id: Optional user identifier to filter queries
        limit: Maximum number of queries to return
    
    Returns:
        HistoryResponse with list of queries
    """
    try:
        db_service = get_db_service()
        queries = db_service.get_query_history(user_id=user_id, limit=limit)
        
        # Convert ObjectId to string for JSON serialization
        for query in queries:
            query["_id"] = str(query["_id"])
            if "timestamp" in query:
                query["timestamp"] = query["timestamp"].isoformat()
        
        return HistoryResponse(queries=queries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@router.get("/query/{query_id}")
async def get_query(query_id: str):
    """
    Get a specific query by ID
    
    Args:
        query_id: MongoDB document ID
    
    Returns:
        Query document
    """
    try:
        db_service = get_db_service()
        query = db_service.get_query_by_id(query_id)
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        
        query["_id"] = str(query["_id"])
        if "timestamp" in query:
            query["timestamp"] = query["timestamp"].isoformat()
        
        return query
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving query: {str(e)}")


@router.post("/analyze-image", response_model=SymptomResponse)
async def analyze_image_symptoms(
    image: UploadFile = File(..., description="Image file (JPEG, PNG, etc.)"),
    symptoms: Optional[str] = Form(None, description="Optional text description of symptoms"),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze symptoms from an image (Requires Authentication)
    
    Args:
        image: Image file upload
        symptoms: Optional text description to accompany the image
        current_user: Authenticated user from JWT token
    
    Returns:
        SymptomResponse with analysis results
    """
    print(f"\n📸 Image analysis request from: {current_user.email}")
    print(f"   Image: {image.filename}")
    print(f"   Description: {symptoms or 'None'}")
    try:
        # Read image bytes
        image_bytes = await image.read()
        
        # Validate image
        image_service = get_image_service()
        if not image_service.validate_image(image_bytes):
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Get service instances
        db_service = get_db_service()
        llm_service = get_llm_service()
        pinecone_service = get_pinecone_service()
        
        # Convert image to base64 for LLM
        image_base64 = image_service.image_to_base64(image_bytes)
        
        # Prepare prompt with image
        image_prompt = f"Analyze this medical image and provide possible conditions and recommendations."
        if symptoms:
            image_prompt += f"\n\nUser also provided this description: {symptoms}"
        
        # For now, we'll use text analysis with image description
        # In production, use Gemini Vision API for actual image analysis
        analysis_text = symptoms or "Medical image analysis requested"
        
        # Generate embedding for RAG search
        embedding = pinecone_service.generate_embedding(analysis_text)
        
        # Search for similar symptoms in Pinecone
        similar_contexts = pinecone_service.search_similar_symptoms(embedding, top_k=3)
        
        # Extract context
        context = []
        if similar_contexts:
            for ctx in similar_contexts:
                context.append(f"Similar case: {ctx['symptoms']} - Conditions: {', '.join(ctx['conditions'])}")
        
        # Generate analysis using LLM
        analysis = llm_service.generate_symptom_analysis(
            f"Image analysis: {image_prompt}",
            context if context else None
        )
        
        # Save to user's symptom history with image info
        symptom_text = symptoms or f"Image analysis of {image.filename}"
        query_id = db_service.save_symptom_history(
            user_id=current_user.id,
            symptoms=symptom_text,
            severity=analysis.get("severity", "Unknown"),
            conditions=analysis["conditions"],
            recommendations=analysis["recommendations"],
            image_analysis=f"Analyzed image: {image.filename}",
            image_filename=image.filename
        )
        
        return SymptomResponse(
            query_id=query_id,
            symptoms=f"Image: {image.filename}" + (f" - {symptoms}" if symptoms else ""),
            conditions=analysis["conditions"],
            recommendations=analysis["recommendations"],
            severity=analysis.get("severity")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")


@router.post("/upload-pdf")
async def upload_pdf(
    pdf: UploadFile = File(..., description="PDF file to upload and process"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process PDF for RAG storage (Requires Authentication)
    
    Args:
        pdf: PDF file upload
        current_user: Authenticated user from JWT token
    
    Returns:
        Success message with number of chunks processed
    """
    print(f"\n📄 PDF upload request from: {current_user.email}")
    print(f"   PDF: {pdf.filename}")
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[PDF UPLOAD] Starting PDF upload process")
        logger.info(f"[PDF UPLOAD] Filename: {pdf.filename}")
        logger.info(f"[PDF UPLOAD] Content type: {pdf.content_type}")
        
        # Validate file type
        if not pdf.filename:
            logger.error("[PDF UPLOAD] ERROR: No filename provided")
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not pdf.filename.lower().endswith('.pdf'):
            logger.error(f"[PDF UPLOAD] ERROR: Invalid file type. Received: {pdf.filename}")
            raise HTTPException(status_code=400, detail=f"File must be a PDF. Received: {pdf.filename}")
        
        # Check content type
        if pdf.content_type and pdf.content_type != 'application/pdf':
            logger.warning(f"[PDF UPLOAD] Warning: Content type is {pdf.content_type}, expected application/pdf")
        
        # Read PDF bytes
        logger.info("[PDF UPLOAD] Reading PDF bytes...")
        pdf_bytes = await pdf.read()
        logger.info(f"[PDF UPLOAD] PDF bytes read: {len(pdf_bytes)} bytes")
        
        if len(pdf_bytes) == 0:
            logger.error("[PDF UPLOAD] ERROR: PDF file is empty")
            raise HTTPException(status_code=400, detail="PDF file is empty")
        
        # Extract text from PDF
        logger.info("[PDF UPLOAD] Extracting text from PDF...")
        pdf_service = get_pdf_service()
        try:
            pdf_text = pdf_service.extract_text_from_pdf(pdf_bytes)
            logger.info(f"[PDF UPLOAD] Text extracted. Length: {len(pdf_text)} characters")
            if pdf_text:
                logger.info(f"[PDF UPLOAD] Text preview (first 300 chars): {pdf_text[:300]}")
        except ValueError as e:
            # ValueError means no text could be extracted
            logger.error(f"[PDF UPLOAD] ERROR extracting text: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=str(e) + " Please ensure the PDF contains selectable text, not just images."
            )
        except Exception as e:
            logger.error(f"[PDF UPLOAD] ERROR extracting text: {str(e)}")
            logger.error(f"[PDF UPLOAD] Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Error extracting text from PDF: {str(e)}")
        
        if not pdf_text or not pdf_text.strip():
            logger.error("[PDF UPLOAD] ERROR: PDF contains no extractable text after extraction")
            raise HTTPException(
                status_code=400, 
                detail="PDF contains no extractable text. The PDF might be image-based (scanned), encrypted, or corrupted. For scanned PDFs, OCR would be required."
            )
        
        logger.info(f"[PDF UPLOAD] Extracted text preview (first 200 chars): {pdf_text[:200]}")
        
        # Chunk the text
        logger.info("[PDF UPLOAD] Chunking text...")
        chunks = pdf_service.chunk_text(pdf_text, chunk_size=1000, overlap=200)
        logger.info(f"[PDF UPLOAD] Text chunked into {len(chunks)} chunks")
        
        # Get services
        logger.info("[PDF UPLOAD] Getting services...")
        pinecone_service = get_pinecone_service()
        db_service = get_db_service()
        logger.info("[PDF UPLOAD] Services retrieved")
        
        # Process and store each chunk
        stored_chunks = 0
        pdf_id = str(uuid.uuid4())
        logger.info(f"[PDF UPLOAD] Processing {len(chunks)} chunks with PDF ID: {pdf_id}")
        
        for i, chunk in enumerate(chunks):
            try:
                logger.info(f"[PDF UPLOAD] Processing chunk {i+1}/{len(chunks)}")
                # Generate embedding for chunk
                logger.info(f"[PDF UPLOAD] Generating embedding for chunk {i+1}...")
                embedding = pinecone_service.generate_embedding(chunk)
                logger.info(f"[PDF UPLOAD] Embedding generated. Dimension: {len(embedding)}")
                
                # Create unique chunk ID
                chunk_id = f"{pdf_id}_chunk_{i}"
                
                # Store in Pinecone
                logger.info(f"[PDF UPLOAD] Storing chunk {i+1} in Pinecone...")
                pinecone_service.add_pdf_chunk(
                    chunk_text=chunk,
                    chunk_id=chunk_id,
                    pdf_name=pdf.filename,
                    embedding=embedding
                )
                stored_chunks += 1
                logger.info(f"[PDF UPLOAD] Chunk {i+1} stored successfully")
            except Exception as e:
                logger.error(f"[PDF UPLOAD] ERROR storing chunk {i+1}: {str(e)}")
                logger.error(f"[PDF UPLOAD] Traceback: {traceback.format_exc()}")
        
        logger.info(f"[PDF UPLOAD] Successfully stored {stored_chunks}/{len(chunks)} chunks")
        
        # Save PDF upload to user's symptom history
        logger.info("[PDF UPLOAD] Saving PDF metadata to user history...")
        try:
            db_service.save_symptom_history(
                user_id=current_user.id,
                symptoms=f"Uploaded medical document: {pdf.filename}",
                severity="Information",
                conditions=[f"Processed {stored_chunks} text chunks"],
                recommendations=["PDF content is now available for symptom analysis"],
                pdf_name=pdf.filename
            )
            logger.info("[PDF UPLOAD] Metadata saved to user history")
        except Exception as e:
            logger.warning(f"[PDF UPLOAD] Warning: Could not save metadata to history: {str(e)}")
        
        logger.info(f"[PDF UPLOAD] SUCCESS: PDF processed. {stored_chunks} chunks stored")
        
        return {
            "message": "PDF processed and stored successfully",
            "filename": pdf.filename,
            "chunks_processed": stored_chunks,
            "total_text_length": len(pdf_text)
        }
    
    except HTTPException as e:
        logger.error(f"[PDF UPLOAD] HTTPException: {e.status_code} - {e.detail}")
        raise
    except ValueError as e:
        logger.error(f"[PDF UPLOAD] ValueError: {str(e)}")
        logger.error(f"[PDF UPLOAD] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[PDF UPLOAD] Unexpected error: {str(e)}")
        logger.error(f"[PDF UPLOAD] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.post("/analyze-with-pdf", response_model=SymptomResponse)
async def analyze_symptoms_with_pdf_rag(
    request: SymptomRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze symptoms using PDF content from Pinecone RAG (Requires Authentication)
    
    Args:
        request: SymptomRequest containing symptoms
        current_user: Authenticated user from JWT token
    
    Returns:
        SymptomResponse with analysis results enhanced by PDF content
    """
    print(f"\n📚 PDF-enhanced analysis request from: {current_user.email}")
    print(f"   Symptoms: {request.symptoms[:100]}...")
    try:
        # Get service instances
        db_service = get_db_service()
        llm_service = get_llm_service()
        pinecone_service = get_pinecone_service()
        
        # Generate embedding for query
        query_embedding = pinecone_service.generate_embedding(request.symptoms)
        
        # Search PDF content in Pinecone
        pdf_contexts = pinecone_service.search_pdf_content(query_embedding, top_k=5)
        
        # Search similar symptoms
        symptom_contexts = pinecone_service.search_similar_symptoms(query_embedding, top_k=3)
        
        # Combine contexts
        context = []
        
        # Add PDF contexts
        if pdf_contexts:
            context.append("Relevant information from medical documents:")
            for pdf_ctx in pdf_contexts:
                context.append(f"- {pdf_ctx['text']} (from {pdf_ctx['pdf_name']})")
        
        # Add symptom contexts
        if symptom_contexts:
            context.append("\nSimilar cases:")
            for ctx in symptom_contexts:
                context.append(f"- {ctx['symptoms']} - Conditions: {', '.join(ctx['conditions'])}")
        
        # Generate analysis using LLM with PDF context
        analysis = llm_service.generate_symptom_analysis(
            request.symptoms,
            context if context else None
        )
        
        # Save to user's symptom history
        query_id = db_service.save_symptom_history(
            user_id=current_user.id,
            symptoms=request.symptoms,
            severity=analysis.get("severity", "Unknown"),
            conditions=analysis["conditions"],
            recommendations=analysis["recommendations"],
            image_analysis="Enhanced with PDF content from knowledge base"
        )
        
        return SymptomResponse(
            query_id=query_id,
            symptoms=request.symptoms,
            conditions=analysis["conditions"],
            recommendations=analysis["recommendations"],
            severity=analysis.get("severity")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing symptoms with PDF RAG: {str(e)}")

