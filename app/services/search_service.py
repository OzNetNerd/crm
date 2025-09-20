"""
Search Service - Handle all search-related functionality.

This service extracts search logic from BaseModel to follow single
responsibility principle. Handles search queries, result formatting,
and search configuration.
"""

from typing import Dict, Any, List
from datetime import datetime, date
from sqlalchemy import String, Text, or_


class SearchService:
    """
    Service for handling all search-related functionality.

    Centralizes search logic that was in BaseModel, providing clean
    separation of concerns for search operations and result formatting.
    """

    @classmethod
    def search_entities(cls, model_class, query: str, limit: int = 20) -> List[Any]:
        """
        Search entities by text query across all searchable fields.

        Args:
            model_class: The model class to search
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching entities
        """
        if not query:
            # Return most recent items when no query
            return model_class.query.order_by(model_class.id.desc()).limit(limit).all()

        # Get searchable text columns
        text_columns = cls._get_searchable_columns(model_class)

        if not text_columns:
            return []

        # Build search conditions
        conditions = [
            getattr(model_class, col.name).ilike(f"%{query}%") for col in text_columns
        ]

        return model_class.query.filter(or_(*conditions)).limit(limit).all()

    @classmethod
    def _get_searchable_columns(cls, model_class):
        """
        Get searchable text columns for a model.

        Args:
            model_class: The model class

        Returns:
            List of searchable columns
        """
        return [
            col
            for col in model_class.__table__.columns
            if isinstance(col.type, (String, Text))
            and col.name not in {"password", "hash", "token", "secret"}
        ]

    @classmethod
    def format_search_result(cls, instance) -> Dict[str, Any]:
        """
        Format model instance as search result.

        Args:
            instance: Model instance to format

        Returns:
            Dictionary with search result data
        """
        from .display_service import DisplayService

        model_class = instance.__class__
        entity_type = DisplayService.get_entity_type_from_model(model_class)

        return {
            "id": instance.id,
            "type": entity_type,
            "title": DisplayService.format_search_title(instance),
            "subtitle": cls._build_search_subtitle(instance),
            "url": f"/modals/{entity_type}/{instance.id}/view",
            "icon": DisplayService.get_entity_icon(entity_type),
        }

    @classmethod
    def _build_search_subtitle(cls, instance) -> str:
        """
        Build subtitle for search results from configured fields.

        Args:
            instance: Model instance

        Returns:
            Formatted subtitle string
        """
        model_class = instance.__class__
        search_config = getattr(model_class, "__search_config__", {})
        subtitle_fields = search_config.get("subtitle_fields", [])

        parts = []
        for field_name in subtitle_fields:
            if hasattr(instance, field_name):
                value = getattr(instance, field_name)
                if value:
                    formatted_value = cls._format_subtitle_value(field_name, value)
                    if formatted_value:
                        parts.append(formatted_value)

        return " • ".join(parts[:3])  # Limit to 3 parts

    @classmethod
    def _format_subtitle_value(cls, field_name: str, value: Any) -> str:
        """
        Format individual subtitle value based on field type.

        Args:
            field_name: Name of the field
            value: Value to format

        Returns:
            Formatted value string
        """
        # Handle date/datetime formatting
        if isinstance(value, (date, datetime)):
            return value.strftime("%d/%m/%y")

        # Handle currency fields (any field containing 'value', 'price', 'cost', 'amount')
        if (isinstance(value, (int, float)) and
            any(currency_term in field_name.lower() for currency_term in ['value', 'price', 'cost', 'amount', 'pipeline'])):
            from app.utils.formatters import format_currency_short
            return format_currency_short(value)

        # Handle large numbers that might need comma formatting
        elif isinstance(value, (int, float)) and value >= 1000:
            from app.utils.formatters import format_number
            return format_number(value)

        # Handle status/stage/priority fields
        elif field_name in {"status", "stage", "priority"}:
            return str(value).replace("_", " ").title()

        # Default string conversion
        return str(value)

    @classmethod
    def get_search_config(cls, model_class) -> Dict[str, Any]:
        """
        Get search configuration for a model.

        Args:
            model_class: The model class

        Returns:
            Search configuration dictionary
        """
        return getattr(model_class, "__search_config__", {})
