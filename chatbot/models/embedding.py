from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path to import CRM models
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.models import db
from app.models.base import BaseModel


class Embedding(BaseModel):
    """
    Embedding model for storing vector embeddings of CRM content.
    
    This model stores vector embeddings generated from various types of
    content in the CRM system for use in AI/ML features like semantic
    search and content recommendations.
    
    Attributes:
        id: Primary key identifier.
        content_type: Type of content embedded (meeting, company, etc.).
        content_id: ID of the source content.
        text_content: Original text that was embedded.
        embedding_vector: Vector embedding as JSON array.
        embedding_metadata: Metadata about embedding generation.
        created_at: Embedding creation timestamp.
    """
    __tablename__ = "embeddings"

    id = db.Column(db.Integer, primary_key=True)

    # What type of content this embedding represents
    content_type = db.Column(
        db.String(50), nullable=False
    )  # meeting, company, contact, etc.
    content_id = db.Column(db.Integer, nullable=False)  # ID of the source content

    # The text content that was embedded
    text_content = db.Column(db.Text, nullable=False)

    # Vector embedding (stored as JSON array)
    embedding_vector = db.Column(db.JSON, nullable=False)

    # Metadata about the embedding
    embedding_metadata = db.Column(db.JSON)  # Model used, chunk size, etc.

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Index for faster lookups
    __table_args__ = (db.Index("idx_content_type_id", "content_type", "content_id"),)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert embedding to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the embedding model.
        """
        return super().to_dict()

    def __repr__(self) -> str:
        """Return string representation of the embedding."""
        return f"<Embedding {self.content_type}:{self.content_id}>"
