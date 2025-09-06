from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db initialization (required for SQLAlchemy)
from .company import Company as Company  # noqa: E402
from .contact import Contact as Contact  # noqa: E402
from .note import Note as Note  # noqa: E402
from .opportunity import Opportunity as Opportunity  # noqa: E402
from .task import Task as Task  # noqa: E402

__all__ = ["db", "Company", "Contact", "Note", "Opportunity", "Task"]
