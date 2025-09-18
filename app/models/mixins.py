"""Simple model mixins - common patterns extracted."""

from datetime import datetime
from . import db


class TimestampMixin:
    """Simple timestamp fields."""

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class SoftDeleteMixin:
    """Simple soft delete pattern."""

    deleted_at = db.Column(db.DateTime, nullable=True)

    @property
    def is_deleted(self):
        """Check if entity is soft deleted."""
        return self.deleted_at is not None

    def soft_delete(self):
        """Mark entity as deleted."""
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore soft deleted entity."""
        self.deleted_at = None


class AuditMixin:
    """Simple audit trail."""

    created_by = db.Column(db.String(255), nullable=True)
    updated_by = db.Column(db.String(255), nullable=True)
