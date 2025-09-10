"""
Chatbot models - mirrors of CRM models for async database access.
These models use the same SQLAlchemy Base but are configured for async operations.
"""

import sys
from pathlib import Path

# Add parent directory to path to import CRM models
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import CRM models (they share the same database tables)
from app.models import (
    db,
    Company,
    Stakeholder,
    Note,
    Opportunity,
    Task,
    Meeting,
    ExtractedInsight,
    ChatHistory,
    Embedding,
)

# Re-export for chatbot use
__all__ = [
    "db",
    "Company",
    "Stakeholder",
    "Note",
    "Opportunity",
    "Task",
    "Meeting",
    "ExtractedInsight",
    "ChatHistory",
    "Embedding",
]
