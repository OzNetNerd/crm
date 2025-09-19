"""Lightweight base model - pure data definition only."""

from . import db
from typing import Dict, Any, List, Callable
from sqlalchemy import event
from app.utils.logging_config import get_crm_logger, log_database_operation
import time


class BaseModel(db.Model):
    """
    Lightweight base model - pure data definition.

    Provides only essential model configuration and delegates
    all business logic to utility functions.
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

    # Delegation to services - simple pass-through methods
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

    # Simple configuration methods
    is_api_enabled = classmethod(lambda cls: cls.__api_enabled__)
    is_web_enabled = classmethod(lambda cls: cls.__web_enabled__)
    get_plural_name = classmethod(lambda cls: cls.__tablename__)

    @classmethod
    def get_singular_name(cls) -> str:
        """Get singular name from DisplayService."""
        from app.services import DisplayService

        return DisplayService.get_entity_type_from_model(cls)

    @classmethod
    def get_display_config(cls) -> Dict[str, Any]:
        """Get display configuration for the model."""
        return {
            "icon": getattr(cls, "__icon__", "📄"),
            "color": getattr(cls, "__color__", "blue"),
            "show_in_nav": getattr(cls, "__show_in_nav__", True),
        }

    # Business logic delegated to utils
    @classmethod
    def get_recent(cls, limit: int = 5):
        """Get recent entities via model utils."""
        from ..utils.model_utils import get_recent_items

        return get_recent_items(cls, limit)

    @classmethod
    def get_overdue(cls, limit: int = 5):
        """Get overdue items via model utils."""
        from ..utils.model_utils import get_overdue_items

        return get_overdue_items(cls, limit)

    # Instance methods delegated to services
    def to_search_result(self) -> Dict[str, Any]:
        """Convert to search result via SearchService."""
        from app.services import SearchService

        return SearchService.format_search_result(self)

    def get_display_title(self) -> str:
        """Get display title via DisplayService."""
        from app.services import DisplayService

        return DisplayService.get_display_title(self)

    def get_view_url(self) -> str:
        """Get URL for viewing this entity."""
        from app.services import DisplayService

        entity_type = DisplayService.get_entity_type_from_model(self.__class__)
        return f"/modals/{entity_type}/{self.id}/view"

    def get_edit_url(self) -> str:
        """Get URL for editing this entity."""
        from app.services import DisplayService

        entity_type = DisplayService.get_entity_type_from_model(self.__class__)
        return f"/modals/{entity_type}/{self.id}/edit"

    def get_delete_url(self) -> str:
        """Get URL for deleting this entity."""
        from app.services import DisplayService

        entity_type = DisplayService.get_entity_type_from_model(self.__class__)
        return f"/modals/{entity_type}/{self.id}/delete"

    def get_deletion_impact(self) -> Dict[str, Any]:
        """Get deletion impact analysis for this entity."""
        from app.utils.entity_crud import get_deletion_impact

        return get_deletion_impact(self.__class__, self.id)

    def can_be_deleted(self) -> bool:
        """Check if entity can be safely deleted."""
        impact = self.get_deletion_impact()
        return impact["safe_to_delete"]

    def delete_safely(self) -> Dict[str, Any]:
        """Delete entity with safety checks and impact analysis."""
        from app.utils.entity_crud import delete_entity_safe

        return delete_entity_safe(self.__class__, self.id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary via SerializationService."""
        from app.services import SerializationService

        return SerializationService.serialize_model(self)

    def get_meta_data(self) -> Dict[str, Any]:
        """Get meta data via model utils."""
        from ..utils.model_utils import get_model_meta_data

        return get_model_meta_data(self)


# Database operation logging setup
logger = get_crm_logger(__name__)

@event.listens_for(BaseModel, 'before_insert', propagate=True)
def log_before_insert(mapper, connection, target):
    """Log entity creation attempts."""
    entity_type = target.__class__.__name__.lower()
    logger.info(
        f"Creating new {entity_type}",
        extra={
            "custom_fields": {
                "operation": "create",
                "entity_type": entity_type,
                "table_name": target.__tablename__
            },
            "entity_type": entity_type,
            "database_operation": "insert"
        }
    )

@event.listens_for(BaseModel, 'after_insert', propagate=True)
def log_after_insert(mapper, connection, target):
    """Log successful entity creation."""
    entity_type = target.__class__.__name__.lower()
    log_database_operation(
        logger,
        operation="create",
        entity_type=entity_type,
        entity_id=target.id if hasattr(target, 'id') else None,
        success=True
    )

@event.listens_for(BaseModel, 'before_update', propagate=True)
def log_before_update(mapper, connection, target):
    """Log entity update attempts."""
    entity_type = target.__class__.__name__.lower()

    # Get changed fields
    changed_fields = {}
    for attr in mapper.attrs:
        if hasattr(attr, 'history'):
            history = attr.load_history()
            if history.has_changes():
                field_name = attr.key
                changed_fields[field_name] = {
                    'old_value': history.deleted[0] if history.deleted else None,
                    'new_value': history.added[0] if history.added else None
                }

    logger.info(
        f"Updating {entity_type}",
        extra={
            "custom_fields": {
                "operation": "update",
                "entity_type": entity_type,
                "entity_id": target.id if hasattr(target, 'id') else None,
                "changed_fields": list(changed_fields.keys()),
                "change_count": len(changed_fields)
            },
            "entity_type": entity_type,
            "entity_id": target.id if hasattr(target, 'id') else None,
            "database_operation": "update"
        }
    )

@event.listens_for(BaseModel, 'after_update', propagate=True)
def log_after_update(mapper, connection, target):
    """Log successful entity updates."""
    entity_type = target.__class__.__name__.lower()
    log_database_operation(
        logger,
        operation="update",
        entity_type=entity_type,
        entity_id=target.id if hasattr(target, 'id') else None,
        success=True
    )

@event.listens_for(BaseModel, 'before_delete', propagate=True)
def log_before_delete(mapper, connection, target):
    """Log entity deletion attempts."""
    entity_type = target.__class__.__name__.lower()
    logger.info(
        f"Deleting {entity_type}",
        extra={
            "custom_fields": {
                "operation": "delete",
                "entity_type": entity_type,
                "entity_id": target.id if hasattr(target, 'id') else None
            },
            "entity_type": entity_type,
            "entity_id": target.id if hasattr(target, 'id') else None,
            "database_operation": "delete"
        }
    )

@event.listens_for(BaseModel, 'after_delete', propagate=True)
def log_after_delete(mapper, connection, target):
    """Log successful entity deletions."""
    entity_type = target.__class__.__name__.lower()
    log_database_operation(
        logger,
        operation="delete",
        entity_type=entity_type,
        entity_id=target.id if hasattr(target, 'id') else None,
        success=True
    )

    # Business logic delegated to utils
    @classmethod
    def get_recent(cls, limit: int = 5):
        """Get recent entities via model utils."""
        from ..utils.model_utils import get_recent_items

        return get_recent_items(cls, limit)

    @classmethod
    def get_overdue(cls, limit: int = 5):
        """Get overdue items via model utils."""
        from ..utils.model_utils import get_overdue_items

        return get_overdue_items(cls, limit)

    # Instance methods delegated to services
    def to_search_result(self) -> Dict[str, Any]:
        """Convert to search result via SearchService."""
        from app.services import SearchService

        return SearchService.format_search_result(self)

    def get_display_title(self) -> str:
        """Get display title via DisplayService."""
        from app.services import DisplayService

        return DisplayService.get_display_title(self)

    def get_view_url(self) -> str:
        """Get URL for viewing this entity."""
        from app.services import DisplayService

        entity_type = DisplayService.get_entity_type_from_model(self.__class__)
        return f"/modals/{entity_type}/{self.id}/view"

    def get_edit_url(self) -> str:
        """Get URL for editing this entity."""
        from app.services import DisplayService

        entity_type = DisplayService.get_entity_type_from_model(self.__class__)
        return f"/modals/{entity_type}/{self.id}/edit"

    def get_delete_url(self) -> str:
        """Get URL for deleting this entity."""
        from app.services import DisplayService

        entity_type = DisplayService.get_entity_type_from_model(self.__class__)
        return f"/modals/{entity_type}/{self.id}/delete"

    def get_deletion_impact(self) -> Dict[str, Any]:
        """Get deletion impact analysis for this entity."""
        from app.utils.entity_crud import get_deletion_impact

        return get_deletion_impact(self.__class__, self.id)

    def can_be_deleted(self) -> bool:
        """Check if entity can be safely deleted."""
        impact = self.get_deletion_impact()
        return impact["safe_to_delete"]

    def delete_safely(self) -> Dict[str, Any]:
        """Delete entity with safety checks and impact analysis."""
        from app.utils.entity_crud import delete_entity_safe

        return delete_entity_safe(self.__class__, self.id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary via SerializationService."""
        from app.services import SerializationService

        return SerializationService.serialize_model(self)

    def get_meta_data(self) -> Dict[str, Any]:
        """Get meta data via model utils."""
        from ..utils.model_utils import get_model_meta_data

        return get_model_meta_data(self)
