"""
Metadata Service - Handle field metadata and choices.

This service extracts metadata logic from BaseModel to follow single
responsibility principle. Handles field metadata, choices, and validation
rules without abusing LRU cache.
"""

from typing import Dict, Any, List, Tuple


class MetadataService:
    """
    Service for handling model field metadata.

    Centralizes metadata logic that was in BaseModel, providing clean
    separation of concerns for field configuration and choices.
    """

    # Class-level cache for metadata (better than LRU cache abuse)
    _metadata_cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_field_metadata(cls, model_class) -> Dict[str, Any]:
        """
        Get metadata for all fields from column info.

        Args:
            model_class: The model class

        Returns:
            Dictionary with field names as keys and metadata as values
        """
        cache_key = model_class.__name__

        # Use simple class-level cache instead of LRU cache abuse
        if cache_key not in cls._metadata_cache:
            cls._metadata_cache[cache_key] = cls._build_field_metadata(model_class)

        return cls._metadata_cache[cache_key]

    @classmethod
    def _build_field_metadata(cls, model_class) -> Dict[str, Any]:
        """
        Build field metadata from model columns.

        Args:
            model_class: The model class

        Returns:
            Dictionary with field metadata
        """
        metadata = {}

        for column in model_class.__table__.columns:
            name = column.name

            # Skip ID fields except for foreign keys we want to filter on
            if (name.endswith("_id") or name == "id") and name != "company_id":
                continue

            column_info = column.info
            metadata[name] = {
                "type": column.type.__class__.__name__,
                "label": column_info.get(
                    "display_label", name.replace("_", " ").title()
                ),
                "filterable": column_info.get("filterable", bool(column_info.get("choices"))),
                "sortable": column_info.get(
                    "sortable", True
                ),  # Make all fields sortable by default
                "groupable": column_info.get(
                    "groupable", bool(column_info.get("choices"))
                ),  # Groupable if has choices
                "choices": column_info.get("choices"),
                "choices_source": column_info.get("choices_source"),
                "required": column_info.get("required", False),
                "contact_field": column_info.get("contact_field", False),
                "icon": column_info.get("icon"),
            }

        # Add filterable relationships for specific models
        if model_class.__name__ == "Stakeholder":
            # Add relationship_owners as a filterable relationship field
            metadata["relationship_owners"] = {
                "type": "relationship",
                "label": "Relationship Owner",
                "filterable": True,
                "sortable": False,
                "groupable": False,
                "choices_source": "users",
                "relationship_field": True,  # Mark as relationship, not a column
                "required": False,
                "contact_field": False,
                "icon": None,
            }

        return metadata

    @classmethod
    def get_field_choices(cls, model_class, field_name: str) -> List[Tuple[str, str]]:
        """
        Get choices for a specific field.

        Args:
            model_class: The model class
            field_name: Name of the field to get choices for

        Returns:
            List of (value, label) tuples for the field choices.
            Returns empty list if field doesn't exist or has no choices.
        """
        metadata = cls.get_field_metadata(model_class)
        field_info = metadata.get(field_name, {})
        choices = field_info.get("choices", {})

        return [(value, data.get("label", value)) for value, data in choices.items()]

    @classmethod
    def get_default_sort_field(cls, model_class) -> str:
        """
        Get default sort field for a model.

        Args:
            model_class: The model class

        Returns:
            Default sort field name
        """
        # Priority order for default sort
        for field in ["due_date", "name", "created_at", "id"]:
            if hasattr(model_class, field):
                return field
        return "id"

    @classmethod
    def get_filterable_fields(cls, model_class) -> List[str]:
        """
        Get list of filterable field names.

        Args:
            model_class: The model class

        Returns:
            List of filterable field names
        """
        metadata = cls.get_field_metadata(model_class)
        return [
            field_name
            for field_name, field_info in metadata.items()
            if field_info.get("filterable")
        ]

    @classmethod
    def get_groupable_fields(cls, model_class) -> List[Dict[str, str]]:
        """
        Get list of groupable fields with labels.

        Args:
            model_class: The model class

        Returns:
            List of dictionaries with value and label keys
        """
        metadata = cls.get_field_metadata(model_class)
        return [
            {"value": field_name, "label": field_info["label"]}
            for field_name, field_info in metadata.items()
            if field_info.get("groupable")
        ]

    @classmethod
    def get_sortable_fields(cls, model_class) -> List[Dict[str, str]]:
        """
        Get list of sortable fields with labels.

        Args:
            model_class: The model class

        Returns:
            List of dictionaries with value and label keys
        """
        metadata = cls.get_field_metadata(model_class)
        sortable_fields = [
            {"value": field_name, "label": field_info["label"]}
            for field_name, field_info in metadata.items()
            if field_info.get("sortable")
        ]

        return sortable_fields

    @classmethod
    def clear_cache(cls, model_class=None):
        """
        Clear metadata cache for specific model or all models.

        Args:
            model_class: Specific model class to clear, or None for all
        """
        if model_class:
            cache_key = model_class.__name__
            cls._metadata_cache.pop(cache_key, None)
        else:
            cls._metadata_cache.clear()
