from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db initialization (required for SQLAlchemy)
from .company import Company as Company  # noqa: E402
from .stakeholder import Stakeholder  # noqa: E402
from .note import Note as Note  # noqa: E402
from .opportunity import Opportunity as Opportunity  # noqa: E402
from .task import Task as Task  # noqa: E402
from .user import User, CompanyAccountTeam, OpportunityAccountTeam  # noqa: E402

# Single source of truth for model name-to-class mapping
MODEL_REGISTRY = {
    "company": Company,
    "stakeholder": Stakeholder,
    "opportunity": Opportunity,
    "task": Task,
    "user": User,
    "note": Note,
}

__all__ = [
    "db",
    "Company",
    "Stakeholder",
    "Note",
    "Opportunity",
    "Task",
    "User",
    "CompanyAccountTeam",
    "OpportunityAccountTeam",
    "MODEL_REGISTRY",
]
