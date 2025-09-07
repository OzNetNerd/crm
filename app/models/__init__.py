from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db initialization (required for SQLAlchemy)
from .company import Company as Company  # noqa: E402
from .contact import Contact as Contact  # noqa: E402
from .note import Note as Note  # noqa: E402
from .opportunity import Opportunity as Opportunity  # noqa: E402
from .task import Task as Task  # noqa: E402
# LLM-related models
from .meeting import Meeting as Meeting  # noqa: E402
from .extracted_insight import ExtractedInsight as ExtractedInsight  # noqa: E402
from .chat_history import ChatHistory as ChatHistory  # noqa: E402
from .embedding import Embedding as Embedding  # noqa: E402

__all__ = ["db", "Company", "Contact", "Note", "Opportunity", "Task", "Meeting", "ExtractedInsight", "ChatHistory", "Embedding"]
