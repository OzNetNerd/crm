from datetime import datetime
from . import db


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=True)  # Internal vs external-facing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Polymorphic relationship - can attach to any entity
    entity_type = db.Column(
        db.String(50)
    )  # 'company', 'contact', 'opportunity', 'task'
    entity_id = db.Column(db.Integer)

    @property
    def entity_name(self):
        if not self.entity_type or not self.entity_id:
            return None

        if self.entity_type == "company":
            from .company import Company

            entity = Company.query.get(self.entity_id)
        elif self.entity_type == "contact":
            from .contact import Contact

            entity = Contact.query.get(self.entity_id)
        elif self.entity_type == "opportunity":
            from .opportunity import Opportunity

            entity = Opportunity.query.get(self.entity_id)
        elif self.entity_type == "task":
            from .task import Task

            entity = Task.query.get(self.entity_id)
        else:
            return None

        return entity.name if hasattr(entity, "name") else str(entity)

    def __repr__(self):
        return f"<Note {self.content[:50]}>"
