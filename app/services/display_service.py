"""
Display Service - Handle all display-related logic for models.

This service extracts display logic from BaseModel to follow single
responsibility principle. Handles display names, icons, and UI metadata.
"""

from typing import Dict, Any
from enum import Enum


class EntityIcon(Enum):
    """Standard icons for each entity type."""

    COMPANY = "🏢"
    STAKEHOLDER = "👤"
    OPPORTUNITY = "💼"
    TASK = "📋"
    USER = "👥"
    NOTE = "📝"
    DEFAULT = "📄"


class DisplayService:
    """
    Service for handling all display-related functionality.

    Centralizes display logic that was scattered across BaseModel,
    providing a single place for display names, icons, and UI formatting.
    """

    @classmethod
    def get_display_name(cls, model_class) -> str:
        """
        Get singular display name for a model.

        Args:
            model_class: The model class to get display name for

        Returns:
            Singular display name string

        Raises:
            NotImplementedError: If model doesn't define __display_name__
        """
        if not hasattr(model_class, "__display_name__") or not model_class.__display_name__:
            raise NotImplementedError(
                f"{model_class.__name__} must define __display_name__"
            )
        return model_class.__display_name__

    @classmethod
    def get_display_name_plural(cls, model_class) -> str:
        """
        Get plural display name for a model.

        Args:
            model_class: The model class to get plural display name for

        Returns:
            Plural display name string
        """
        if hasattr(model_class, "__display_name_plural__") and model_class.__display_name_plural__:
            return model_class.__display_name_plural__

        # Default to titleized table name (tables are already plural)
        return model_class.__tablename__.title()

    @classmethod
    def get_entity_icon(cls, entity_type: str) -> str:
        """
        Get icon for entity type.

        Args:
            entity_type: The entity type string

        Returns:
            Icon emoji string
        """
        entity_type_upper = entity_type.upper()
        try:
            return EntityIcon[entity_type_upper].value
        except KeyError:
            return EntityIcon.DEFAULT.value

    @classmethod
    def get_entity_type_from_model(cls, model_class) -> str:
        """
        Get entity type string from model class.

        Args:
            model_class: The model class

        Returns:
            Entity type string for registry lookup
        """
        # Import here to avoid circular imports
        from app.models import MODEL_REGISTRY

        return next(
            (key for key, model in MODEL_REGISTRY.items() if model == model_class),
            model_class.__name__.lower(),
        )

    @classmethod
    def get_display_title(cls, instance) -> str:
        """
        Get display title for a model instance.

        Args:
            instance: Model instance

        Returns:
            Display title string
        """
        model_class = instance.__class__
        field_name = getattr(model_class, "__display_field__", "name")

        if hasattr(instance, field_name):
            value = getattr(instance, field_name)
            if value:
                return str(value)
            return f"Empty {cls.get_display_name(model_class)}"

        return f"{cls.get_display_name(model_class)} #{instance.id}"

    @classmethod
    def format_search_title(cls, instance, max_length: int = 100) -> str:
        """
        Format title for search results with length limit.

        Args:
            instance: Model instance
            max_length: Maximum title length

        Returns:
            Formatted search title
        """
        model_class = instance.__class__
        search_config = getattr(model_class, "__search_config__", {})

        # Use configured title field if available
        if title_field := search_config.get("title_field"):
            if hasattr(instance, title_field):
                value = getattr(instance, title_field)
                if value:
                    return str(value)[:max_length]

        # Try common title fields
        for field in ["name", "title", "description", "email"]:
            if hasattr(instance, field):
                value = getattr(instance, field)
                if value:
                    return str(value)[:max_length]

        # Fallback to display name with ID
        return f"{cls.get_display_name(model_class)} #{instance.id}"

    @classmethod
    def format_choice_display(cls, value: str) -> str:
        """
        Format choice values for display (replace underscores/hyphens).

        Args:
            value: Raw choice value

        Returns:
            Formatted display string
        """
        if not value:
            return ""
        return value.replace("-", " ").replace("_", " ").title()

    @classmethod
    def build_entity_config(cls, model_class) -> Dict[str, Any]:
        """
        Build entity configuration for templates.

        Args:
            model_class: The model class

        Returns:
            Dictionary with entity configuration
        """
        entity_type = cls.get_entity_type_from_model(model_class)
        table_name = model_class.__tablename__

        return {
            "entity_type": entity_type,
            "entity_name": cls.get_display_name_plural(model_class),
            "entity_name_singular": cls.get_display_name(model_class),
            "content_endpoint": f"entities.{table_name}_content",
            "entity_buttons": [
                {
                    "title": f"New {cls.get_display_name(model_class)}",
                    "url": f"/modals/{entity_type}/create",
                }
            ],
        }