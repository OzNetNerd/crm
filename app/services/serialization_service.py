"""
Serialization Service - Handle model serialization and transformations.

This service extracts serialization logic from BaseModel to follow single
responsibility principle. Handles to_dict conversion, property inclusion,
and relationship transformations.
"""

from typing import Dict, Any, List, Callable
from datetime import datetime, date


class SerializationService:
    """
    Service for handling model serialization and transformations.

    Centralizes serialization logic that was in BaseModel, providing
    clean separation of concerns for data transformation operations.
    """

    @classmethod
    def serialize_model(cls, instance) -> Dict[str, Any]:
        """
        Convert model instance to dictionary for JSON serialization.

        Args:
            instance: Model instance to serialize

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        result = {}

        # Serialize all database columns
        for column in instance.__table__.columns:
            column_name = column.name
            value = getattr(instance, column_name, None)
            result[column_name] = cls._serialize_value(value)

        # Add configured properties
        include_properties = getattr(instance.__class__, "__include_properties__", [])
        for prop in include_properties:
            if hasattr(instance, prop):
                value = getattr(instance, prop)
                result[prop] = cls._serialize_value(value)

        # Apply relationship transforms
        relationship_transforms = getattr(
            instance.__class__, "__relationship_transforms__", {}
        )
        for field, transform in relationship_transforms.items():
            try:
                result[field] = transform(instance)
            except Exception:
                # If transform fails, skip it rather than breaking serialization
                result[field] = None

        return result

    @classmethod
    def _serialize_value(cls, value: Any) -> Any:
        """
        Serialize individual value for JSON compatibility.

        Args:
            value: Value to serialize

        Returns:
            JSON-compatible value
        """
        if isinstance(value, (datetime, date)):
            return value.isoformat() if value else None
        return value

    @classmethod
    def serialize_with_display_fields(cls, instance) -> Dict[str, Any]:
        """
        Serialize model with additional display-friendly fields.

        Args:
            instance: Model instance to serialize

        Returns:
            Dictionary with both raw and display-formatted fields
        """
        # Get base serialization
        result = cls.serialize_model(instance)

        # Add display-friendly versions of choice fields
        choice_fields = ["status", "priority", "stage", "next_step_type", "task_type", "dependency_type"]

        for field in choice_fields:
            if hasattr(instance, field):
                raw_value = getattr(instance, field)
                if raw_value:
                    display_key = f"{field}_display"
                    result[display_key] = cls._format_choice_for_display(raw_value)

        return result

    @classmethod
    def _format_choice_for_display(cls, value: str) -> str:
        """
        Format choice values for display.

        Args:
            value: Raw choice value

        Returns:
            Formatted display string
        """
        if not value:
            return ""
        return value.replace("-", " ").replace("_", " ").title()

    @classmethod
    def serialize_relationship(cls, related_instances: List[Any], fields: List[str]) -> List[Dict[str, Any]]:
        """
        Serialize related model instances with specific fields.

        Args:
            related_instances: List of related model instances
            fields: List of field names to include

        Returns:
            List of dictionaries with specified fields
        """
        result = []
        for instance in related_instances:
            item = {}
            for field in fields:
                if hasattr(instance, field):
                    value = getattr(instance, field)
                    item[field] = cls._serialize_value(value)
            result.append(item)
        return result

    @classmethod
    def get_serialization_config(cls, model_class) -> Dict[str, Any]:
        """
        Get serialization configuration for a model.

        Args:
            model_class: The model class

        Returns:
            Serialization configuration dictionary
        """
        return {
            "include_properties": getattr(model_class, "__include_properties__", []),
            "relationship_transforms": getattr(model_class, "__relationship_transforms__", {}),
        }