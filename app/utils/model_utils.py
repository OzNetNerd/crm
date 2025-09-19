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
    from datetime import datetime, date

    meta = {}
    entity_type = model_instance.__class__.__name__.lower()

    # Universal fields - return both actual date and relative for display flexibility
    # Created date
    if hasattr(model_instance, "created_at") and model_instance.created_at:
        created_date = (
            model_instance.created_at.date()
            if isinstance(model_instance.created_at, datetime)
            else model_instance.created_at
        )
        meta["created_date"] = created_date.strftime("%B %d, %Y")
        meta["created"] = format_date_with_relative(created_date)

    # Last updated
    if hasattr(model_instance, "updated_at") and model_instance.updated_at:
        updated_date = (
            model_instance.updated_at.date()
            if isinstance(model_instance.updated_at, datetime)
            else model_instance.updated_at
        )
        meta["updated_date"] = updated_date.strftime("%B %d, %Y")
        meta["last_update"] = format_date_with_relative(updated_date)

    # Entity-specific metadata
    if entity_type == "company":
        # Pipeline value - sum of active opportunities
        if hasattr(model_instance, "opportunities"):
            active_opps = [opp for opp in model_instance.opportunities if opp.stage not in ["closed-won", "closed-lost"]]
            pipeline_value = sum(opp.value or 0 for opp in active_opps)
            if pipeline_value > 0:
                meta["pipeline_value"] = f"${pipeline_value:,}"

        # Team size - number of stakeholders
        if hasattr(model_instance, "stakeholders"):
            team_size = len(model_instance.stakeholders)
            if team_size > 0:
                meta["team_size"] = f"{team_size} stakeholder{'s' if team_size != 1 else ''}"

    elif entity_type == "stakeholder":
        # Last contacted
        if hasattr(model_instance, "last_contacted") and model_instance.last_contacted:
            last_contacted_date = (
                model_instance.last_contacted.date()
                if isinstance(model_instance.last_contacted, datetime)
                else model_instance.last_contacted
            )
            meta["last_contacted_date"] = last_contacted_date.strftime("%B %d, %Y")
            meta["last_contacted"] = format_date_with_relative(last_contacted_date)

        # Active opportunities count
        if hasattr(model_instance, "opportunities"):
            active_opps = [opp for opp in model_instance.opportunities if opp.stage not in ["closed-won", "closed-lost"]]
            if active_opps:
                meta["active_opportunities"] = f"{len(active_opps)} active opp{'s' if len(active_opps) != 1 else ''}"

        # MEDDPICC roles
        if hasattr(model_instance, "get_meddpicc_role_names"):
            roles = model_instance.get_meddpicc_role_names()
            if roles:
                # Format roles nicely - capitalize and join with commas
                formatted_roles = [role.replace("_", " ").title() for role in roles]
                meta["meddpicc_roles"] = f"MEDDPICC: {', '.join(formatted_roles)}"

    elif entity_type == "opportunity":
        # Deal size and stage
        if hasattr(model_instance, "value") and model_instance.value:
            meta["deal_size"] = f"${model_instance.value:,}"

        if hasattr(model_instance, "stage") and model_instance.stage:
            stage_display = model_instance.stage.replace("-", " ").replace("_", " ").title()
            meta["stage"] = stage_display

        # Days to close
        if hasattr(model_instance, "expected_close_date") and model_instance.expected_close_date:
            if isinstance(model_instance.expected_close_date, datetime):
                close_date = model_instance.expected_close_date.date()
            else:
                close_date = model_instance.expected_close_date

            days_to_close = (close_date - date.today()).days
            meta["close_date"] = close_date.strftime("%B %d, %Y")
            if days_to_close >= 0:
                meta["days_to_close"] = f"{days_to_close} days to close"
            else:
                meta["days_overdue"] = f"{abs(days_to_close)} days overdue"

    # Due date with relative time (for tasks, etc.)
    if hasattr(model_instance, "due_date") and model_instance.due_date:
        due_date = (
            model_instance.due_date.date()
            if isinstance(model_instance.due_date, datetime)
            else model_instance.due_date
        )
        meta["due_date"] = due_date.strftime("%B %d, %Y")
        meta["due"] = format_date_with_relative(due_date)

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
