from . import db
from datetime import datetime, date
from sqlalchemy import String, Text, Date, Numeric
from typing import Dict, Any, List, Callable


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
    def get_modal_config(cls):
        """Get modal configuration for this entity."""
        return {
            'size': cls.__modal_size__,
            'icon': cls.__modal_icon__ or cls.get_entity_type(),
            'title': cls.get_display_name()
        }

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

    def get_meta_data(self):
        """Return structured meta data for entity cards."""
        meta = {}
        if hasattr(self, 'created_at') and self.created_at:
            meta['created'] = self.created_at.strftime('%d/%m/%y')
        if hasattr(self, 'due_date') and self.due_date:
            meta['due'] = self.due_date.strftime('%d/%m/%y')
        return meta

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

    @classmethod
    def get_display_config(cls):
        """Extract display configuration from column metadata."""
        from sqlalchemy import Numeric, Float, Integer

        config = {
            'contact_fields': [],
            'badge_fields': [],
            'value_fields': [],
            'description_field': None
        }

        for column in cls.__table__.columns:
            col_info = column.info
            col_name = column.name

            # Skip ID fields
            if col_name.endswith('_id') or col_name == 'id':
                continue

            # Contact fields - get icon from column info
            if col_info.get('contact_field'):
                config['contact_fields'].append({
                    'name': col_name,
                    'icon': col_info.get('icon', 'info')  # Icon should be in column info
                })

            # Badge fields (fields with choices)
            elif col_info.get('choices'):
                config['badge_fields'].append(col_name)

            # Value fields (numeric)
            elif isinstance(column.type, (Numeric, Float, Integer)):
                config['value_fields'].append({
                    'name': col_name,
                    'currency': col_info.get('currency', col_name == 'value'),
                    'unit': col_info.get('unit', ''),
                    'format': col_info.get('format', '{:,.0f}')
                })

            # Description field (first Text field)
            elif column.type.__class__.__name__ == 'Text' and not config['description_field']:
                if col_name not in ['comments', 'notes', 'internal_notes']:
                    config['description_field'] = col_name

        return config

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
