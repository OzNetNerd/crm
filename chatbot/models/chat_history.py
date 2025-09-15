from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path to import CRM models
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.models import db
from app.models.base import BaseModel


class ChatHistory(BaseModel):
    """
    ChatHistory model for storing chatbot conversation history.
    
    This model records all interactions between users and the CRM chatbot,
    including the user messages, bot responses, context used for generation,
    and metadata about the response generation process.
    
    Attributes:
        id: Primary key identifier.
        session_id: Session identifier for grouping related messages.
        user_message: User's input message.
        bot_response: Chatbot's response message.
        context_used: Context data used to generate response (JSON).
        response_metadata: Metadata about response generation (JSON).
        created_at: Chat interaction timestamp.
    """
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

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert chat history to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the chat history record.
        """
        return super().to_dict()

    def __repr__(self) -> str:
        """Return string representation of the chat history."""
        return f"<ChatHistory {self.session_id} - {self.user_message[:50]}...>"
