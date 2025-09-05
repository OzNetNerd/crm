from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .company import Company
from .contact import Contact
from .opportunity import Opportunity
from .task import Task
from .note import Note