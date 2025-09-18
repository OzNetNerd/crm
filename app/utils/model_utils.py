"""Simple model utilities - business logic extracted from BaseModel."""

from typing import List, Dict, Any
from datetime import date


def get_recent_items(model_class, limit: int = 5) -> List:
    """Get recent entities - uniform interface for all models."""
    if hasattr(model_class, "created_at"):
        return (
            model_class.query.order_by(model_class.created_at.desc()).limit(limit).all()
        )
    return model_class.query.order_by(model_class.id.desc()).limit(limit).all()


def get_overdue_items(model_class, limit: int = 5) -> List:
    """Get overdue items - only for models with due_date."""
    if hasattr(model_class, "due_date") and hasattr(model_class, "status"):
        return (
            model_class.query.filter(
                model_class.due_date < date.today(), model_class.status != "complete"
            )
            .limit(limit)
            .all()
        )
    return []


def get_model_meta_data(model_instance) -> Dict[str, Any]:
    """Return structured meta data for entity cards."""
    # Import from the utils package
    from app.utils import format_date_with_relative, get_next_step_icon
    from datetime import datetime

    meta = {}

    # Created date with relative time
    if hasattr(model_instance, "created_at") and model_instance.created_at:
        created_date = (
            model_instance.created_at.date()
            if isinstance(model_instance.created_at, datetime)
            else model_instance.created_at
        )
        meta["created"] = format_date_with_relative(created_date)

    # Due date with relative time
    if hasattr(model_instance, "due_date") and model_instance.due_date:
        meta["due"] = format_date_with_relative(model_instance.due_date)

    # Next step for tasks
    if (
        hasattr(model_instance, "next_step_type")
        and model_instance.next_step_type
        and hasattr(model_instance, "due_date")
        and model_instance.due_date
    ):
        meta["next_step"] = {
            "type": model_instance.next_step_type,
            "icon": get_next_step_icon(model_instance.next_step_type),
            "date": format_date_with_relative(model_instance.due_date),
            "type_display": model_instance.next_step_type.replace("_", " ").title(),
        }

    return meta
