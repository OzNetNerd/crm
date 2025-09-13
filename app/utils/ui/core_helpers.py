"""
Essential Server-Side Helpers

Minimal replacement for index_helpers.py - keeps only essential data aggregation
that must happen server-side. UI logic moved to Alpine.js.
"""

from sqlalchemy import func, distinct
from app.models import db


class CoreHelper:
    """Essential server-side helpers for data aggregation."""

    @staticmethod
    def get_entity_count(model_class, filters=None):
        """Get total count for an entity type with optional filters."""
        query = db.session.query(model_class)

        if filters:
            for field, value in filters.items():
                if hasattr(model_class, field) and value is not None:
                    query = query.filter(getattr(model_class, field) == value)

        return query.count()

    @staticmethod
    def get_entity_stats(model_class, group_by_field=None):
        """Get basic stats for an entity type."""
        total_count = db.session.query(model_class).count()

        if not group_by_field or not hasattr(model_class, group_by_field):
            return {'total': total_count}

        # Group by field stats
        field = getattr(model_class, group_by_field)
        grouped_counts = (
            db.session.query(field, func.count())
            .filter(field.isnot(None))
            .group_by(field)
            .all()
        )

        return {
            'total': total_count,
            'grouped': [{'value': value, 'count': count} for value, count in grouped_counts]
        }

    @staticmethod
    def get_recent_entities(model_class, limit=5):
        """Get recently created entities."""
        return (
            db.session.query(model_class)
            .order_by(model_class.created_at.desc())
            .limit(limit)
            .all()
        )


# Template functions for Jinja2
def entity_count(model_class, **filters):
    """Jinja2 function: Get entity count with filters."""
    return CoreHelper.get_entity_count(model_class, filters)


def entity_stats(model_class, group_by=None):
    """Jinja2 function: Get entity statistics."""
    return CoreHelper.get_entity_stats(model_class, group_by)


def recent_entities(model_class, limit=5):
    """Jinja2 function: Get recent entities."""
    return CoreHelper.get_recent_entities(model_class, limit)