from datetime import datetime
from . import db
from .base import BaseModel


class Embedding(BaseModel):
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

    def to_dict(self):
        """Convert embedding to dictionary for JSON serialization"""
        return super().to_dict()

    def __repr__(self):
        return f"<Embedding {self.content_type}:{self.content_id}>"
