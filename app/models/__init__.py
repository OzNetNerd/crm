from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import base model first
from .base import BaseModel  # noqa: E402

# Import models after db initialization (required for SQLAlchemy)
from .company import Company as Company  # noqa: E402
from .stakeholder import Stakeholder  # noqa: E402
from .note import Note as Note  # noqa: E402
from .opportunity import Opportunity as Opportunity  # noqa: E402
from .task import Task as Task  # noqa: E402
from .user import User, CompanyAccountTeam, OpportunityAccountTeam  # noqa: E402

# LLM-related models
from .chat_history import ChatHistory as ChatHistory  # noqa: E402
from .embedding import Embedding as Embedding  # noqa: E402

# Single source of truth for model name-to-class mapping
MODEL_REGISTRY = {
    'company': Company,
    'stakeholder': Stakeholder,
    'opportunity': Opportunity,
    'task': Task,
    'user': User
}

__all__ = [
    "db",
    "BaseModel",
    "Company",
    "Stakeholder",
    "Note",
    "Opportunity",
    "Task",
    "User",
    "CompanyAccountTeam",
    "OpportunityAccountTeam",
    "ChatHistory",
    "Embedding",
    "MODEL_REGISTRY",
]
