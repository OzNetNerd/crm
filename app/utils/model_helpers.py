"""
Simple model utility functions extracted from the overengineered base.py
"""
from typing import Dict, Any
from datetime import datetime, date


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