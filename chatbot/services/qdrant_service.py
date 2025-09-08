"""
Qdrant service for vector similarity search.
Integrates with the CRM system to provide semantic search capabilities.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
import threading
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, OptimizersConfigDiff
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for managing vector embeddings in Qdrant"""
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6333,
        model_name: str = "all-mpnet-base-v2",
        collection_name: str = "crm_entities"
    ):
        self.host = host
        self.port = port
        self.model_name = model_name
        self.collection_name = collection_name
        self.client = None
        self.model = None
        self.embedding_dimension = 768  # Dimension for all-mpnet-base-v2
        self._model_lock = threading.Lock()  # Thread-safe model loading
        self._embedding_cache = {}  # Cache for embeddings
        
    def _connect(self):
        """Connect to Qdrant with connection pooling"""
        if self.client is None:
            try:
                # Configure client with connection pooling and timeout settings
                self.client = QdrantClient(
                    host=self.host, 
                    port=self.port,
                    timeout=30,  # 30 second timeout
                    prefer_grpc=False  # Use HTTP for better reliability in this setup
                )
                logger.info(f"Connected to Qdrant at {self.host}:{self.port} with optimized settings")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}")
                raise
    
    def _load_model(self):
        """Load the sentence transformer model with thread safety"""
        if self.model is None:
            with self._model_lock:
                # Double-check locking pattern
                if self.model is None:
                    try:
                        logger.info(f"Loading embedding model: {self.model_name}")
                        self.model = SentenceTransformer(self.model_name)
                        logger.info(f"Successfully loaded embedding model: {self.model_name}")
                    except Exception as e:
                        logger.error(f"Failed to load embedding model: {e}")
                        raise
    
    def ensure_collection(self):
        """Create collection if it doesn't exist"""
        self._connect()
        
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(
                collection.name == self.collection_name 
                for collection in collections.collections
            )
            
            if not collection_exists:
                # Create collection with optimized settings
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    ),
                    optimizers_config=OptimizersConfigDiff(
                        indexing_threshold=100,  # Build index after 100 vectors (was 10000)
                        max_segment_size=50000,  # Optimize for smaller datasets
                        memmap_threshold=10000   # Use memory mapping for larger segments
                    )
                )
                logger.info(f"Created optimized collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
                # Update existing collection with optimized settings
                try:
                    self.client.update_collection(
                        collection_name=self.collection_name,
                        optimizers_config=OptimizersConfigDiff(
                            indexing_threshold=100,
                            max_segment_size=50000,
                            memmap_threshold=10000
                        )
                    )
                    logger.info(f"Updated collection optimizer settings")
                except Exception as e:
                    logger.warning(f"Could not update collection settings: {e}")
                
        except Exception as e:
            logger.error(f"Failed to ensure collection: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text with caching"""
        # Check cache first
        text_hash = hash(text)
        if text_hash in self._embedding_cache:
            return self._embedding_cache[text_hash]
            
        self._load_model()
        
        try:
            embedding = self.model.encode(text)
            embedding_list = embedding.tolist()
            
            # Cache the result (limit cache size)
            if len(self._embedding_cache) < 1000:
                self._embedding_cache[text_hash] = embedding_list
                
            return embedding_list
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def index_document(
        self,
        doc_id: str,
        text: str,
        entity_type: str,
        entity_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Index a document in Qdrant
        
        Args:
            doc_id: Unique document ID
            text: Text to index
            entity_type: Type of CRM entity (company, contact, etc.)
            entity_id: ID of the CRM entity
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        self._connect()
        self.ensure_collection()
        
        try:
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Prepare payload
            payload = {
                "text": text,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "indexed_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            # Create point (use hash of doc_id as numeric ID)
            numeric_id = hash(doc_id) % (2**63 - 1)  # Keep within signed int64 range
            point = PointStruct(
                id=numeric_id,
                vector=embedding,
                payload={**payload, "doc_id": doc_id}  # Store original ID in payload
            )
            
            # Upsert point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Indexed document {doc_id} for {entity_type}:{entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")
            return False
    
    def search_similar(
        self,
        query_text: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query_text: Text to search for
            entity_types: Filter by entity types (optional)
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar documents with scores
        """
        self._connect()
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query_text)
            
            # Prepare filter
            query_filter = None
            if entity_types:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="entity_type",
                            match=MatchValue(value=entity_type)
                        ) for entity_type in entity_types
                    ]
                )
            
            # Perform search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.payload.get("doc_id", result.id),  # Use original doc_id if available
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "entity_type": result.payload.get("entity_type", ""),
                    "entity_id": result.payload.get("entity_id", 0),
                    "metadata": {k: v for k, v in result.payload.items() 
                               if k not in ["text", "entity_type", "entity_id", "indexed_at", "doc_id"]},
                    "indexed_at": result.payload.get("indexed_at", "")
                })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the collection"""
        self._connect()
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[doc_id]
            )
            logger.info(f"Deleted document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def delete_entity_documents(self, entity_type: str, entity_id: int) -> bool:
        """Delete all documents for a specific entity"""
        self._connect()
        
        try:
            # Search for documents of this entity
            search_filter = Filter(
                must=[
                    FieldCondition(key="entity_type", match=MatchValue(value=entity_type)),
                    FieldCondition(key="entity_id", match=MatchValue(value=entity_id))
                ]
            )
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=search_filter
            )
            
            logger.info(f"Deleted all documents for {entity_type}:{entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete entity documents {entity_type}:{entity_id}: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        self._connect()
        
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.name,
                "status": info.status.value,
                "points_count": info.points_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.value
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}


# Singleton instance
_qdrant_service: Optional[QdrantService] = None


def get_qdrant_service() -> QdrantService:
    """Get the singleton Qdrant service instance"""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service