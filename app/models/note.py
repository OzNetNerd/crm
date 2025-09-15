from datetime import datetime
from typing import Dict, Any, Optional
from . import db
from .base import BaseModel


class Note(BaseModel):
    """
    Note model for attaching text notes to any entity in the CRM system.

    This model provides a flexible note-taking system that can be attached
    to any entity (companies, stakeholders, opportunities, tasks) using
    polymorphic relationships. Notes can be marked as internal or external-facing.

    Attributes:
        id: Primary key identifier.
        content: Note text content (required).
        is_internal: Whether note is internal-only or customer-facing.
        created_at: Note creation timestamp.
        entity_type: Type of entity this note is attached to.
        entity_id: ID of the entity this note is attached to.
    """
    __tablename__ = "notes"
    __display_name__ = "Note"
    __display_field__ = 'content'

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
    def company_name(self) -> Optional[str]:
        """Get company name from the entity this note is attached to."""
        if not self.entity_type or not self.entity_id:
            return None

        if self.entity_type == "company":
            from .company import Company
            entity = Company.query.get(self.entity_id)
            return entity.name if entity else None
        elif self.entity_type == "stakeholder":
            from .stakeholder import Stakeholder
            entity = Stakeholder.query.get(self.entity_id)
            return entity.company.name if entity and entity.company else None
        elif self.entity_type == "opportunity":
            from .opportunity import Opportunity
            entity = Opportunity.query.get(self.entity_id)
            return entity.company.name if entity and entity.company else None

        return None

    @property
    def entity_name(self) -> Optional[str]:
        """
        Get the name of the entity this note is attached to.
        
        Returns:
            Name of the attached entity, or None if no entity attached
            or entity not found.
            
        Example:
            >>> note = Note(entity_type="company", entity_id=1)
            >>> note.entity_name
            'Acme Corp'
        """
        if not self.entity_type or not self.entity_id:
            return None

        if self.entity_type == "company":
            from .company import Company

            entity = Company.query.get(self.entity_id)
        elif self.entity_type == "stakeholder":
            from .stakeholder import Stakeholder

            entity = Stakeholder.query.get(self.entity_id)
        elif self.entity_type == "opportunity":
            from .opportunity import Opportunity

            entity = Opportunity.query.get(self.entity_id)
        elif self.entity_type == "task":
            from .task import Task

            entity = Task.query.get(self.entity_id)
        else:
            return None

        return entity.name if hasattr(entity, "name") else str(entity)

    @property
    def created_at_display(self) -> str:
        """Format creation time for display with relative time information."""
        if not self.created_at:
            return ""

        from datetime import datetime
        now = datetime.utcnow()
        diff = now - self.created_at
        formatted_date = self.created_at.strftime('%d/%m/%y %H:%M')

        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                if minutes == 0:
                    return f"{formatted_date} (Just now)"
                return f"{formatted_date} ({minutes} minute{'s' if minutes != 1 else ''} ago)"
            return f"{formatted_date} ({hours} hour{'s' if hours != 1 else ''} ago)"
        elif diff.days == 1:
            return f"{formatted_date} (Yesterday)"
        elif diff.days < 7:
            return f"{formatted_date} ({diff.days} days ago)"
        else:
            return formatted_date  # Just show date/time for older notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary."""
        return {
            'id': self.id,
            'content': self.content,
            'is_internal': self.is_internal,
            'created_at': self.created_at,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id
        }

    def to_display_dict(self) -> Dict[str, Any]:
        """
        Convert note to dictionary with pre-formatted display fields.

        Returns:
            Dictionary with formatted fields including entity name and
            content preview for UI display.

        Example:
            >>> note = Note(content="Long content here...")
            >>> display_data = note.to_display_dict()
            >>> print(display_data['content_preview'])
            'Long content here...'
        """
        # Get base dictionary
        result = self.to_dict()

        # Add note-specific computed fields
        result['entity_name'] = self.entity_name
        result['company_name'] = self.company_name
        result['content_preview'] = self.content[:100] + '...' if len(self.content) > 100 else self.content
        result['created_at_display'] = self.created_at_display

        return result

    def __repr__(self) -> str:
        """Return string representation of the note."""
        return f"<Note {self.content[:50]}>"
