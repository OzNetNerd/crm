"""
Base model class using services for single responsibility principle.

This refactored BaseModel delegates all complex logic to focused services,
following CLAUDE.md principles of single responsibility and modern Python patterns.
"""

from . import db
from typing import Dict, Any, List, Callable


class BaseModel(db.Model):
    """
    Lightweight base class for entity models.

    This class provides only core model configuration and delegates
    all complex logic to specialized services. Follows single responsibility
    principle by focusing only on model definition.
    """

    __abstract__ = True

    # Model configuration - models MUST override these
    __display_name__ = None  # REQUIRED: "Company"
    __display_name_plural__ = None  # Optional: defaults to __tablename__.title()
    __display_field__ = "name"  # Field to use for display title

    # Service configuration - override in models as needed
    __search_config__ = {}
    __include_properties__: List[str] = []  # Additional properties for serialization
    __relationship_transforms__: Dict[str, Callable] = {}  # Custom transforms

    # UI configuration
    __modal_size__ = "md"  # sm, md, lg, xl
    __modal_icon__ = None  # Override to use custom icon

    # Route exposure control
    __api_enabled__ = True  # Enable API endpoints
    __web_enabled__ = True  # Enable web pages

    # Service delegation methods - clean and simple
    @classmethod
    def get_display_name(cls) -> str:
        """Get singular display name via DisplayService."""
        from app.services import DisplayService

        return DisplayService.get_display_name(cls)

    @classmethod
    def get_display_name_plural(cls) -> str:
        """Get plural display name via DisplayService."""
        from app.services import DisplayService

        return DisplayService.get_display_name_plural(cls)

    @classmethod
    def get_field_metadata(cls) -> Dict[str, Any]:
        """Get field metadata via MetadataService."""
        from app.services import MetadataService

        return MetadataService.get_field_metadata(cls)

    @classmethod
    def get_field_choices(cls, field_name: str) -> List[tuple]:
        """Get field choices via MetadataService."""
        from app.services import MetadataService

        return MetadataService.get_field_choices(cls, field_name)

    @classmethod
    def get_default_sort_field(cls) -> str:
        """Get default sort field via MetadataService."""
        from app.services import MetadataService

        return MetadataService.get_default_sort_field(cls)

    @classmethod
    def search(cls, query: str, limit: int = 20) -> List[Any]:
        """Search entities via SearchService."""
        from app.services import SearchService

        return SearchService.search_entities(cls, query, limit)

    @classmethod
    def is_api_enabled(cls) -> bool:
        """Check if this model should have API endpoints."""
        return cls.__api_enabled__

    @classmethod
    def is_web_enabled(cls) -> bool:
        """Check if this model should have web entity pages."""
        return cls.__web_enabled__

    # Legacy compatibility methods (delegate to services)
    @classmethod
    def get_plural_name(cls) -> str:
        """Get plural name - table name is already plural."""
        return cls.__tablename__

    @classmethod
    def get_singular_name(cls) -> str:
        """Get singular name from MODEL_REGISTRY."""
        from app.services import DisplayService

        return DisplayService.get_entity_type_from_model(cls)

    @classmethod
    def get_recent(cls, limit: int = 5) -> List[Any]:
        """Get recent entities - uniform interface for all models."""
        if hasattr(cls, "created_at"):
            return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
        return cls.query.order_by(cls.id.desc()).limit(limit).all()

    @classmethod
    def get_overdue(cls, limit: int = 5) -> List[Any]:
        """Get overdue items - only for models with due_date."""
        if hasattr(cls, "due_date") and hasattr(cls, "status"):
            from datetime import date

            return (
                cls.query.filter(cls.due_date < date.today(), cls.status != "complete")
                .limit(limit)
                .all()
            )
        return []

    # Instance methods - delegate to services
    def to_search_result(self) -> Dict[str, Any]:
        """Convert to search result via SearchService."""
        from app.services import SearchService

        return SearchService.format_search_result(self)

    def get_display_title(self) -> str:
        """Get display title via DisplayService."""
        from app.services import DisplayService

        return DisplayService.get_display_title(self)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary via SerializationService."""
        from app.services import SerializationService

        return SerializationService.serialize_model(self)

    def get_meta_data(self) -> Dict[str, Any]:
        """Return structured meta data for entity cards."""
        from app.utils import format_date_with_relative, get_next_step_icon

        meta = {}

        # Created date with relative time
        if hasattr(self, "created_at") and self.created_at:
            from datetime import datetime

            created_date = (
                self.created_at.date()
                if isinstance(self.created_at, datetime)
                else self.created_at
            )
            meta["created"] = format_date_with_relative(created_date)

        # Due date with relative time
        if hasattr(self, "due_date") and self.due_date:
            meta["due"] = format_date_with_relative(self.due_date)

        # Next step for tasks
        if (
            hasattr(self, "next_step_type")
            and self.next_step_type
            and hasattr(self, "due_date")
            and self.due_date
        ):
            meta["next_step"] = {
                "type": self.next_step_type,
                "icon": get_next_step_icon(self.next_step_type),
                "date": format_date_with_relative(self.due_date),
                "type_display": self.next_step_type.replace("_", " ").title(),
            }

        return meta