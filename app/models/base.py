from . import db
from datetime import datetime, date
from sqlalchemy import String, Text, Date, Numeric


class BaseModel(db.Model):
    """Lightweight base class for entity metadata and search."""
    __abstract__ = True

    # Name-mangled attributes - singular is REQUIRED
    __display_name__ = None  # REQUIRED: "Company"
    __display_name_plural__ = None  # Optional: defaults to __tablename__.title()

    # Search configuration - override in models as needed
    __search_config__ = {}

    @classmethod
    def get_display_name(cls):
        """Get singular display name."""
        if not cls.__display_name__:
            raise NotImplementedError(
                f"{cls.__name__} must define __display_name__"
            )
        return cls.__display_name__

    @classmethod
    def get_display_name_plural(cls):
        """Get plural display name."""
        if cls.__display_name_plural__:
            return cls.__display_name_plural__
        # Default to titleized table name (tables are already plural)
        return cls.__tablename__.title()

    @classmethod
    def get_entity_type(cls):
        """Get entity type from MODEL_REGISTRY."""
        from app.models import MODEL_REGISTRY
        for key, model_class in MODEL_REGISTRY.items():
            if model_class == cls:
                return key
        return cls.__name__.lower()

    @classmethod
    def get_field_choices(cls, field_name: str):
        """
        Get choices for a field from column info metadata.

        Args:
            field_name: Name of the field to get choices for

        Returns:
            List of (value, label) tuples for the field choices.
            Returns empty list if field doesn't exist or has no choices.
        """
        if not hasattr(cls, field_name):
            return []

        column = getattr(cls, field_name)
        if not hasattr(column, 'info') or 'choices' not in column.info:
            return []

        choices = column.info['choices']
        return [(value, data.get('label', value)) for value, data in choices.items()]

    @classmethod
    def get_metadata(cls):
        """Get entity metadata dict for template **kwargs."""
        return {
            'entity_type': cls.__name__.lower(),
            'entity_name_singular': cls.get_display_name(),
            'entity_name_plural': cls.get_display_name_plural(),
            'entity_name': cls.get_display_name_plural()
        }

    @classmethod
    def search(cls, query, limit=20):
        """Search all text fields automatically."""
        if not query:
            return cls.query.limit(limit).all()

        from sqlalchemy import or_

        # Get searchable text columns
        text_columns = [
            col for col in cls.__table__.columns
            if isinstance(col.type, (String, Text))
            and col.name not in {'password', 'hash', 'token', 'secret'}
        ]

        if not text_columns:
            return []

        # Build search conditions
        conditions = [
            getattr(cls, col.name).ilike(f"%{query}%")
            for col in text_columns
        ]

        return cls.query.filter(or_(*conditions)).limit(limit).all()

    def to_search_result(self):
        """Convert to search result for API responses."""
        # Icon mapping for each entity type
        icon_map = {
            'company': '🏢',
            'stakeholder': '👤',
            'opportunity': '💼',
            'task': '📋',
            'user': '👥',
            'note': '📝'
        }

        entity_type = self.get_entity_type()

        return {
            "id": self.id,
            "type": entity_type,
            "title": self._get_search_title(),
            "subtitle": self._build_search_subtitle(),
            "url": f"/modals/{entity_type}/{self.id}/view",
            "icon": icon_map.get(entity_type, '📄')
        }

    def _get_search_title(self):
        """Get title for search results."""
        # Use configured title field or common fields
        config = self.__search_config__
        if title_field := config.get('title_field'):
            if hasattr(self, title_field):
                return str(getattr(self, title_field, ''))[:100]

        # Try common title fields
        for field in ['name', 'title', 'description', 'email']:
            if hasattr(self, field) and (value := getattr(self, field)):
                return str(value)[:100]

        return f"{self.get_display_name()} #{self.id}"

    def _build_search_subtitle(self):
        """Build subtitle for search results."""
        parts = []
        config = self.__search_config__

        # Use configured subtitle fields
        subtitle_fields = config.get('subtitle_fields', [])

        for field_name in subtitle_fields:
            if hasattr(self, field_name) and (value := getattr(self, field_name)):
                # Simple formatting for common field types
                if isinstance(value, (date, datetime)):
                    parts.append(value.strftime('%d/%m/%y'))
                elif field_name in {'status', 'stage', 'priority'}:
                    parts.append(str(value).replace('_', ' ').title())
                else:
                    parts.append(str(value))

        return " • ".join(parts[:3])

    def get_view_url(self):
        """Get the view URL for this entity"""
        from flask import url_for
        return url_for('modals.view_modal', model_name=self.get_entity_type(), entity_id=self.id)

    def get_edit_url(self):
        """Get the edit URL for this entity"""
        from flask import url_for
        return url_for('modals.edit_modal', model_name=self.get_entity_type(), entity_id=self.id)

    def get_display_title(self):
        """Get display title using model's configured display field."""
        # Use the field specified by the model
        field_name = getattr(self, '__display_field__', 'name')
        if hasattr(self, field_name):
            return getattr(self, field_name) or f'Empty {self.get_display_name()}'
        return f'{self.get_display_name()} #{self.id}'
