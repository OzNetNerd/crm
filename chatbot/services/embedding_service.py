"""
Embedding service using sentence transformers for semantic search.
Handles text embedding and similarity calculations for RAG pipeline.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
from sqlalchemy.orm import Session

# Note: sentence-transformers would be imported here when installed
# from sentence_transformers import SentenceTransformer

from ..models import Embedding

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing text embeddings"""
    
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model_name = model_name
        self.model = None  # Will be loaded when needed
        self.embedding_dimension = 768  # Dimension for all-mpnet-base-v2
    
    def _load_model(self):
        """Load the sentence transformer model (lazy loading)"""
        if self.model is None:
            try:
                # This would be uncommented when sentence-transformers is installed
                # from sentence_transformers import SentenceTransformer
                # self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
                
                # For now, mock the model
                logger.warning("Using mock embedding model - install sentence-transformers for real functionality")
                self.model = "mock"
                
            except ImportError:
                logger.error("sentence-transformers not installed")
                self.model = "mock"
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.model = "mock"
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        self._load_model()
        
        if self.model == "mock":
            # Generate a simple mock embedding (for testing)
            # In production, this would be: return self.model.encode(text).tolist()
            hash_val = hash(text) % 1000000
            np.random.seed(hash_val)  # Deterministic "embedding"
            mock_embedding = np.random.normal(0, 1, self.embedding_dimension).tolist()
            return mock_embedding
        else:
            # Real implementation would be:
            # return self.model.encode(text).tolist()
            pass
    
    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self.generate_embedding(text) for text in texts]
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            arr1 = np.array(embedding1)
            arr2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(arr1, arr2)
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_similar_embeddings(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[Dict[str, Any]],
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find the most similar embeddings to a query
        
        Args:
            query_embedding: The query embedding vector
            candidate_embeddings: List of dicts with 'embedding' and metadata
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar embeddings with similarity scores
        """
        
        similarities = []
        
        for candidate in candidate_embeddings:
            similarity = self.calculate_similarity(
                query_embedding, 
                candidate.get('embedding', [])
            )
            
            if similarity >= similarity_threshold:
                result = candidate.copy()
                result['similarity_score'] = similarity
                similarities.append(result)
        
        # Sort by similarity (descending) and return top k
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:top_k]
    
    def embed_and_store(
        self,
        text: str,
        content_type: str,
        content_id: int,
        db_session: Session,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Generate embedding and store in database
        
        Args:
            text: Text to embed
            content_type: Type of content (meeting, company, etc.)
            content_id: ID of the source content
            db_session: Database session
            metadata: Optional metadata about the embedding
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            # Generate embedding
            embedding_vector = self.generate_embedding(text)
            
            # Check if embedding already exists
            existing = db_session.query(Embedding).filter(
                Embedding.content_type == content_type,
                Embedding.content_id == content_id
            ).first()
            
            if existing:
                # Update existing embedding
                existing.embedding_vector = embedding_vector
                existing.text_content = text
                existing.embedding_metadata = metadata or {}
            else:
                # Create new embedding
                embedding = Embedding(
                    content_type=content_type,
                    content_id=content_id,
                    text_content=text,
                    embedding_vector=embedding_vector,
                    embedding_metadata=metadata or {
                        "model": self.model_name,
                        "created_at": datetime.utcnow().isoformat()
                    }
                )
                db_session.add(embedding)
            
            db_session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to embed and store text: {e}")
            db_session.rollback()
            return False
    
    def search_similar_content(
        self,
        query_text: str,
        db_session: Session,
        content_types: Optional[List[str]] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content using semantic similarity
        
        Args:
            query_text: Text to search for
            db_session: Database session
            content_types: Optional filter by content types
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar content with metadata
        """
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query_text)
        
        # Get candidate embeddings from database
        query = db_session.query(Embedding)
        
        if content_types:
            query = query.filter(Embedding.content_type.in_(content_types))
        
        embeddings = query.all()
        
        # Prepare candidates for similarity search
        candidates = []
        for emb in embeddings:
            candidates.append({
                'id': emb.id,
                'content_type': emb.content_type,
                'content_id': emb.content_id,
                'text_content': emb.text_content,
                'embedding': emb.embedding_vector,
                'metadata': emb.embedding_metadata,
                'created_at': emb.created_at
            })
        
        # Find similar embeddings
        similar = self.find_similar_embeddings(
            query_embedding, 
            candidates, 
            top_k, 
            similarity_threshold
        )
        
        return similar


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get the singleton embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service