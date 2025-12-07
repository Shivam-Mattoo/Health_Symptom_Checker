from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional
from config import Config
import hashlib
import logging

logger = logging.getLogger(__name__)

class PineconeService:
    """Service class for Pinecone vector database operations (RAG)"""
    
    def __init__(self):
        """Initialize Pinecone client"""
        self.pc = Pinecone(api_key=Config.PINECONE_API)
        self.index_name = Config.PINECONE_INDEX
        self.index = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or connect to Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name in existing_indexes:
                # Check if we need to recreate due to dimension mismatch
                try:
                    temp_index = self.pc.Index(self.index_name)
                    stats = temp_index.describe_index_stats()
                    index_dimension = stats.get('dimension', 1024)
                    
                    if index_dimension != 384:
                        logger.warning(f"[PINECONE SERVICE] Index dimension mismatch: {index_dimension} != 384. Recreating index...")
                        print(f"⚠️ Deleting old Pinecone index with wrong dimension ({index_dimension})...")
                        self.pc.delete_index(self.index_name)
                        print("✅ Old index deleted. Creating new index with correct dimension...")
                        
                        # Create new index with correct dimension
                        self.pc.create_index(
                            name=self.index_name,
                            dimension=384,  # all-MiniLM-L6-v2 produces 384-dim embeddings
                            metric="cosine",
                            spec=ServerlessSpec(
                                cloud="aws",
                                region="us-east-1"
                            )
                        )
                        print("✅ New index created with dimension 384")
                except Exception as check_error:
                    logger.error(f"[PINECONE SERVICE] Error checking index: {check_error}")
                    # If check fails, try to use existing index anyway
                    pass
            else:
                # Create index if it doesn't exist
                print("📦 Creating new Pinecone index...")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # all-MiniLM-L6-v2 produces 384-dim embeddings
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print("✅ Pinecone index created with dimension 384")
            
            self.index = self.pc.Index(self.index_name)
            print(f"Successfully connected to Pinecone index: {self.index_name}")
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            self.index = None
    
    def add_symptom_context(self, symptoms: str, conditions: List[str], 
                           recommendations: List[str], embedding: List[float]):
        """
        Add symptom context to Pinecone for RAG
        
        Args:
            symptoms: User symptoms
            conditions: Associated conditions
            recommendations: Recommendations
            embedding: Vector embedding of the symptom text
        """
        if not self.index:
            return
        
        try:
            # Create unique ID from symptoms
            symptom_id = hashlib.md5(symptoms.encode()).hexdigest()
            
            metadata = {
                "symptoms": symptoms,
                "conditions": ",".join(conditions),
                "recommendations": ",".join(recommendations),
                "type": "symptom"
            }
            
            self.index.upsert(vectors=[{
                "id": symptom_id,
                "values": embedding,
                "metadata": metadata
            }])
        except Exception as e:
            print(f"Error adding to Pinecone: {e}")
    
    def add_pdf_chunk(self, chunk_text: str, chunk_id: str, pdf_name: str, embedding: List[float]):
        """
        Add PDF chunk to Pinecone for RAG
        
        Args:
            chunk_text: Text chunk from PDF
            chunk_id: Unique identifier for the chunk
            pdf_name: Name of the PDF file
            embedding: Vector embedding of the chunk
        """
        if not self.index:
            logger.warning("[PINECONE SERVICE] Index not available, skipping chunk storage")
            return
        
        try:
            logger.info(f"[PINECONE SERVICE] Adding PDF chunk to Pinecone: {chunk_id}")
            metadata = {
                "text": chunk_text[:500],  # Store first 500 chars in metadata
                "pdf_name": pdf_name,
                "type": "pdf",
                "chunk_id": chunk_id
            }
            
            logger.info(f"[PINECONE SERVICE] Embedding dimension: {len(embedding)}")
            self.index.upsert(vectors=[{
                "id": chunk_id,
                "values": embedding,
                "metadata": metadata
            }])
            logger.info(f"[PINECONE SERVICE] Chunk {chunk_id} added successfully")
        except Exception as e:
            logger.error(f"[PINECONE SERVICE] Error adding PDF chunk to Pinecone: {str(e)}")
            import traceback
            logger.error(f"[PINECONE SERVICE] Traceback: {traceback.format_exc()}")
            raise
    
    def search_pdf_content(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for relevant PDF content in Pinecone
        
        Args:
            query_embedding: Vector embedding of the query
            top_k: Number of results to return
        
        Returns:
            List of relevant PDF chunks
        """
        if not self.index:
            return []
        
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            contexts = []
            for match in results.matches:
                if match.metadata and match.metadata.get("type") == "pdf":
                    contexts.append({
                        "text": match.metadata.get("text", ""),
                        "pdf_name": match.metadata.get("pdf_name", ""),
                        "score": match.score
                    })
                # Also include symptom contexts if no PDF contexts found
                elif match.metadata and match.metadata.get("type") != "pdf" and not contexts:
                    # Fallback to symptom contexts if no PDF content
                    pass
            
            return contexts
        except Exception as e:
            print(f"Error searching PDF content: {e}")
            return []
    
    def search_similar_symptoms(self, embedding: List[float], top_k: int = 3) -> List[Dict]:
        """
        Search for similar symptoms in Pinecone
        
        Args:
            embedding: Vector embedding of query symptoms
            top_k: Number of similar results to return
        
        Returns:
            List of similar symptom contexts
        """
        if not self.index:
            return []
        
        try:
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            contexts = []
            for match in results.matches:
                if match.metadata:
                    contexts.append({
                        "symptoms": match.metadata.get("symptoms", ""),
                        "conditions": match.metadata.get("conditions", "").split(","),
                        "recommendations": match.metadata.get("recommendations", "").split(","),
                        "score": match.score
                    })
            
            return contexts
        except Exception as e:
            print(f"Error searching Pinecone: {e}")
            return []
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using sentence-transformers
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector (1024 dimensions)
        """
        logger.info(f"[PINECONE SERVICE] Generating embedding for text (length: {len(text)} chars)")
        try:
            from sentence_transformers import SentenceTransformer
            
            # Lazy load the model
            if not hasattr(self, '_embedding_model'):
                logger.info("[PINECONE SERVICE] Loading sentence-transformers model...")
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("[PINECONE SERVICE] Model loaded successfully")
            
            # Generate embedding
            logger.info("[PINECONE SERVICE] Encoding text...")
            embedding = self._embedding_model.encode(text, convert_to_numpy=True).tolist()
            logger.info(f"[PINECONE SERVICE] Embedding generated. Dimension: {len(embedding)}")
            return embedding
        except ImportError as e:
            logger.warning(f"[PINECONE SERVICE] sentence-transformers not available, using fallback: {e}")
            # Fallback to simple hash-based embedding if sentence-transformers not available
            import hashlib
            hash_obj = hashlib.sha256(text.encode())
            hash_hex = hash_obj.hexdigest()
            
            # Convert to 1024-dim vector
            embedding = [int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, min(1024*2, len(hash_hex)), 2)]
            if len(embedding) < 1024:
                embedding.extend([0.0] * (1024 - len(embedding)))
            
            logger.info(f"[PINECONE SERVICE] Fallback embedding generated. Dimension: {len(embedding)}")
            return embedding[:1024]
        except Exception as e:
            logger.error(f"[PINECONE SERVICE] Error generating embedding: {str(e)}")
            raise

