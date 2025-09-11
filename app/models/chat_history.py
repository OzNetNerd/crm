from datetime import datetime
from . import db


class ChatHistory(db.Model):
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True)

    # Session identifier for grouping related chat messages
    session_id = db.Column(db.String(100), nullable=False, index=True)

    # User message and bot response
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)

    # Context used to generate the response (stored as JSON)
    context_used = db.Column(db.JSON)  # Database queries, retrieved documents, etc.

    # Response metadata
    response_metadata = db.Column(
        db.JSON
    )  # Model used, processing time, confidence, etc.

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert chat history to dictionary for JSON serialization"""
        from app.utils.model_helpers import auto_serialize
        return auto_serialize(self)

    def __repr__(self):
        return f"<ChatHistory {self.session_id} - {self.user_message[:50]}...>"
