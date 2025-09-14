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
        # Fallback for models not in registry
        return cls.__name__.lower()

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
        return {
            "id": self.id,
            "type": self.get_entity_type(),
            "model_type": self.get_entity_type(),  # For backward compatibility
            "title": self._get_search_title(),
            "subtitle": self._build_search_subtitle(),
            "url": f"/modals/{self.get_entity_type()}/{self.id}/view"
        }

    def _get_search_title(self):
        """Get title for search results."""
        config = self.__search_config__

        # Check explicit title field in config
        if title_field := config.get('title_field'):
            if hasattr(self, title_field):
                return str(getattr(self, title_field, ''))[:100]

        # Auto-detect from common title fields
        for field in ['name', 'title', 'description', 'email']:
            if hasattr(self, field) and (value := getattr(self, field)):
                return str(value)[:100]

        # Fallback
        return f"{self.get_display_name()} #{self.id}"

    def _build_search_subtitle(self):
        """Build subtitle for search results."""
        parts = []
        config = self.__search_config__

        # Get configured subtitle fields or auto-detect
        subtitle_fields = config.get('subtitle_fields', [])

        if not subtitle_fields:
            # Auto-detect interesting fields for subtitle
            subtitle_fields = self._auto_detect_subtitle_fields()

        # Format each field value
        for field_name in subtitle_fields:
            if not hasattr(self, field_name):
                continue

            value = getattr(self, field_name)
            if not value:
                continue

            # Format the field value appropriately
            formatted = self._format_search_field(field_name, value)
            if formatted:
                parts.append(formatted)

        # Add relationship data if configured
        for rel_name, field_name in config.get('relationships', []):
            if rel := getattr(self, rel_name, None):
                if rel_value := getattr(rel, field_name, None):
                    parts.append(str(rel_value))

        return " • ".join(parts[:3])  # Limit to 3 parts

    def _auto_detect_subtitle_fields(self):
        """Auto-detect fields for subtitle."""
        fields = []
        skip = {'id', 'name', 'title', 'description', 'created_at', 'updated_at',
                'password', 'hash', 'token', 'comments', 'content'}

        for col in self.__table__.columns:
            if col.name in skip:
                continue

            # Include fields with display_label or common important fields
            if col.info.get('display_label') or col.name in {
                'industry', 'job_title', 'email', 'status',
                'priority', 'stage', 'due_date', 'value', 'size'
            }:
                fields.append(col.name)

        return fields[:3]

    def _format_search_field(self, field_name, value):
        """Format a field value for search display."""
        if not value:
            return None

        # Get column for type checking
        column = self.__table__.columns.get(field_name)
        if column is None:
            return str(value)

        # Date fields
        if isinstance(column.type, Date) or isinstance(value, (date, datetime)):
            if isinstance(value, datetime):
                value = value.date()
            formatted = value.strftime('%d/%m/%y')
            if field_name == 'due_date':
                return f"Due: {formatted}"
            return formatted

        # Currency fields
        if isinstance(column.type, Numeric) or field_name in {'value', 'price', 'amount'}:
            return f"${value:,.0f}"

        # Status/priority/stage fields - title case
        if field_name in {'status', 'stage', 'priority'}:
            return str(value).replace('_', ' ').replace('-', ' ').title()

        # Percentage
        if field_name == 'probability':
            return f"{value}%"

        # Default - just string
        return str(value)