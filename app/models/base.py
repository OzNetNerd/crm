from . import db
from datetime import datetime, date
from sqlalchemy import String, Text, Date, Numeric
from typing import Dict, Any, List, Callable
from functools import lru_cache


class BaseModel(db.Model):
    """Lightweight base class for entity metadata and search."""
    __abstract__ = True

    # Name-mangled attributes - singular is REQUIRED
    __display_name__ = None  # REQUIRED: "Company"
    __display_name_plural__ = None  # Optional: defaults to __tablename__.title()

    # Search configuration - override in models as needed
    __search_config__ = {}

    # Serialization configuration - override in models as needed
    __include_properties__: List[str] = []  # Additional properties to include
    __relationship_transforms__: Dict[str, Callable] = {}  # Custom relationship serializers

    # Modal configuration - override in models as needed
    __modal_size__ = 'md'  # sm, md, lg, xl
    __modal_icon__ = None   # Override to use custom icon
    __display_field__ = 'name'  # Field to use for display title

    # Route configuration - models control their own exposure
    __api_enabled__ = True   # Default: all models have API endpoints
    __web_enabled__ = True   # Default: all models have web pages

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
    def get_plural_name(cls):
        """Get plural name - just use the table name, it's already plural!"""
        return cls.__tablename__

    @classmethod
    def get_singular_name(cls):
        """Get singular name from MODEL_REGISTRY."""
        from app.models import MODEL_REGISTRY
        return next((k for k, v in MODEL_REGISTRY.items() if v == cls), cls.__name__.lower())

    @classmethod
    def is_api_enabled(cls):
        """Check if this model should have API endpoints."""
        return cls.__api_enabled__

    @classmethod
    def is_web_enabled(cls):
        """Check if this model should have web entity pages."""
        return cls.__web_enabled__

    @classmethod
    @lru_cache(maxsize=None)
    def get_field_metadata(cls):
        """Get metadata for all fields from column info.

        Returns dict with field names as keys and metadata as values.
        Cached per model class for performance.
        """
        metadata = {}
        for column in cls.__table__.columns:
            name = column.name
            # Skip ID fields
            if name.endswith('_id') or name == 'id':
                continue

            column_info = column.info
            metadata[name] = {
                'type': column.type.__class__.__name__,
                'label': column_info.get('display_label', name.replace('_', ' ').title()),
                'filterable': bool(column_info.get('choices')),
                'sortable': column_info.get('sortable', name in ['created_at', 'name']),
                'groupable': column_info.get('groupable', False),
                'choices': column_info.get('choices'),
                'required': column_info.get('required', False),
                'contact_field': column_info.get('contact_field', False),
                'icon': column_info.get('icon'),
            }
        return metadata

    @classmethod
    def get_default_sort_field(cls):
        """Get default sort field for this model."""
        # Priority order for default sort
        for field in ['due_date', 'name', 'created_at', 'id']:
            if hasattr(cls, field):
                return field
        return 'id'

    @classmethod
    def get_field_choices(cls, field_name: str):
        """Get choices for a specific field.

        Args:
            field_name: Name of the field to get choices for

        Returns:
            List of (value, label) tuples for the field choices.
            Returns empty list if field doesn't exist or has no choices.
        """
        metadata = cls.get_field_metadata()
        field_info = metadata.get(field_name, {})
        choices = field_info.get('choices', {})
        return [(value, data.get('label', value)) for value, data in choices.items()]

    @classmethod
    def search(cls, query, limit=20):
        """Search all text fields automatically."""
        if not query:
            # Return most recent items when no query
            return cls.query.order_by(cls.id.desc()).limit(limit).all()

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

        from app.models import MODEL_REGISTRY
        entity_type = next((key for key, model in MODEL_REGISTRY.items() if model == self.__class__), self.__class__.__name__.lower())

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

    def get_meta_data(self):
        """Return structured meta data for entity cards."""
        from app.utils import format_date_with_relative, get_next_step_icon

        meta = {}

        # Created date with relative time
        if hasattr(self, 'created_at') and self.created_at:
            created_date = self.created_at.date() if isinstance(self.created_at, datetime) else self.created_at
            meta['created'] = format_date_with_relative(created_date)

        # Due date with relative time
        if hasattr(self, 'due_date') and self.due_date:
            meta['due'] = format_date_with_relative(self.due_date)

        # Next step for tasks
        if (hasattr(self, 'next_step_type') and self.next_step_type and
            hasattr(self, 'due_date') and self.due_date):
            meta['next_step'] = {
                'type': self.next_step_type,
                'icon': get_next_step_icon(self.next_step_type),
                'date': format_date_with_relative(self.due_date),
                'type_display': self.next_step_type.replace('_', ' ').title()
            }

        return meta


    def get_display_title(self):
        """Get display title using model's configured display field."""
        # Use the field specified by the model
        field_name = self.__class__.__display_field__
        if hasattr(self, field_name):
            return getattr(self, field_name) or f'Empty {self.get_display_name()}'
        return f'{self.get_display_name()} #{self.id}'

    @classmethod
    def get_recent(cls, limit=5):
        """Get recent entities - uniform interface for all models."""
        # Use created_at if available, otherwise id for ordering
        if hasattr(cls, 'created_at'):
            return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
        return cls.query.order_by(cls.id.desc()).limit(limit).all()

    @classmethod
    def get_overdue(cls, limit=5):
        """Get overdue items - only for models with due_date."""
        if hasattr(cls, 'due_date') and hasattr(cls, 'status'):
            from datetime import date
            return cls.query.filter(
                cls.due_date < date.today(),
                cls.status != 'complete'
            ).limit(limit).all()
        return []


    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for JSON serialization.

        This base implementation:
        1. Serializes all database columns
        2. Converts datetime/date objects to ISO format
        3. Includes properties specified in __include_properties__
        4. Applies relationship transforms from __relationship_transforms__

        Models can override this method to add custom logic while calling super().to_dict()

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        result = {}

        # Serialize all columns
        for column in self.__table__.columns:
            column_name = column.name
            value = getattr(self, column_name, None)
            # Handle datetime/date serialization
            if isinstance(value, (datetime, date)):
                result[column_name] = value.isoformat() if value else None
            else:
                result[column_name] = value

        # Add configured properties
        for prop in self.__include_properties__:
            if hasattr(self, prop):
                result[prop] = getattr(self, prop)

        # Apply relationship transforms
        for field, transform in self.__relationship_transforms__.items():
            result[field] = transform(self)

        return result
