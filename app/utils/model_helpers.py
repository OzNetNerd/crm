"""
Simple model utility functions extracted from the overengineered base.py
"""
from typing import List, Dict, Any
from datetime import datetime, date


def get_field_choices(model_class, field_name: str) -> List[tuple]:
    """
    Get choices for a field from column info metadata.

    Args:
        model_class: SQLAlchemy model class
        field_name: Name of the field to get choices for

    Returns:
        List of (value, label) tuples for the field choices.
        Returns empty list if field doesn't exist or has no choices.

    Example:
        >>> get_field_choices(Task, 'priority')
        [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    """
    if not hasattr(model_class, field_name):
        return []

    column = getattr(model_class, field_name)
    if not hasattr(column, 'info') or 'choices' not in column.info:
        return []

    choices = column.info['choices']
    choice_list = []

    for choice_value, choice_data in choices.items():
        choice_label = choice_data.get('label', choice_value)
        choice_list.append((choice_value, choice_label))

    return choice_list


def model_to_dict(model_instance) -> Dict[str, Any]:
    """
    Convert model instance to dictionary for JSON serialization.

    This is the simple to_dict functionality extracted from BaseModel,
    without all the inheritance complexity.

    Args:
        model_instance: SQLAlchemy model instance

    Returns:
        Dictionary representation of the model instance
    """
    result = {}

    # Serialize all columns
    for column in model_instance.__table__.columns:
        column_name = column.name
        value = getattr(model_instance, column_name, None)

        # Handle datetime/date serialization
        if isinstance(value, (datetime, date)):
            result[column_name] = value.isoformat() if value else None
        else:
            result[column_name] = value

    return result