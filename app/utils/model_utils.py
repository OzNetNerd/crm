"""Simple model utilities - business logic extracted from BaseModel."""

from typing import List, Dict, Any
from datetime import date
from app.utils.formatters import format_currency_short


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

    def get_relative_time_only(target_date: date, from_date: date = None) -> str:
        """Get only the relative time part (e.g., '5 days ago', '10 days to go')"""
        if not target_date:
            return ""

        if from_date is None:
            from_date = date.today()
        days_diff = (target_date - from_date).days

        if days_diff == 0:
            return "today"
        elif days_diff == 1:
            return "tomorrow"
        elif days_diff == -1:
            return "yesterday"
        elif days_diff > 1:
            return f"{days_diff} days to go"
        else:
            return f"{abs(days_diff)} days ago"

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
        meta["created"] = get_relative_time_only(created_date)

    # Last updated
    if hasattr(model_instance, "updated_at") and model_instance.updated_at:
        updated_date = (
            model_instance.updated_at.date()
            if isinstance(model_instance.updated_at, datetime)
            else model_instance.updated_at
        )
        meta["updated_date"] = updated_date.strftime("%B %d, %Y")
        meta["last_update"] = get_relative_time_only(updated_date)

    # Entity-specific metadata
    if entity_type == "company":
        # Pipeline value - sum of active opportunities
        if hasattr(model_instance, "opportunities"):
            active_opps = [opp for opp in model_instance.opportunities if opp.stage not in ["closed-won", "closed-lost"]]
            pipeline_value = sum(opp.value or 0 for opp in active_opps)
            if pipeline_value > 0:
                meta["pipeline_value"] = format_currency_short(pipeline_value)

            # Active opportunities count
            if active_opps:
                meta["active_opportunities"] = f"{len(active_opps)}"

        # Stakeholders count (previously team_size)
        if hasattr(model_instance, "stakeholders"):
            stakeholder_count = len(model_instance.stakeholders)
            if stakeholder_count > 0:
                meta["stakeholders"] = f"{stakeholder_count}"

        # Account team size
        if hasattr(model_instance, "account_team_assignments"):
            account_team_size = len(model_instance.account_team_assignments)
            if account_team_size > 0:
                meta["account_team"] = f"{account_team_size}"

    elif entity_type == "stakeholder":
        # Last contacted
        if hasattr(model_instance, "last_contacted") and model_instance.last_contacted:
            last_contacted_date = (
                model_instance.last_contacted.date()
                if isinstance(model_instance.last_contacted, datetime)
                else model_instance.last_contacted
            )
            meta["last_contacted_date"] = last_contacted_date.strftime("%B %d, %Y")
            meta["last_contacted"] = get_relative_time_only(last_contacted_date)

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
                meta["meddpicc_count"] = f"{len(roles)}"

    elif entity_type == "opportunity":
        # Deal size and stage
        if hasattr(model_instance, "value") and model_instance.value:
            meta["deal_size"] = format_currency_short(model_instance.value)

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
                meta["days_to_close"] = f"in {days_to_close} days"
            else:
                meta["days_overdue"] = f"{abs(days_to_close)} days overdue"

    elif entity_type == "user":
        # Company assignments count
        if hasattr(model_instance, "company_assignments"):
            company_count = len(model_instance.company_assignments)
            if company_count > 0:
                meta["assigned_companies"] = f"{company_count}"

        # Opportunity assignments count
        if hasattr(model_instance, "opportunity_assignments"):
            opportunity_count = len(model_instance.opportunity_assignments)
            if opportunity_count > 0:
                meta["assigned_opportunities"] = f"{opportunity_count}"

        # Total pipeline value for assigned opportunities
        if hasattr(model_instance, "opportunity_assignments"):
            total_pipeline = 0
            for assignment in model_instance.opportunity_assignments:
                opp = assignment.opportunity
                # Only count active opportunities (not closed)
                if opp and opp.stage not in ["closed-won", "closed-lost"] and opp.value:
                    total_pipeline += opp.value

            if total_pipeline > 0:
                meta["total_pipeline"] = format_currency_short(total_pipeline)

        # Total stakeholder relationships (through opportunities or direct)
        # Count unique stakeholders user is working with
        stakeholder_ids = set()

        # Through opportunity assignments
        if hasattr(model_instance, "opportunity_assignments"):
            for assignment in model_instance.opportunity_assignments:
                if assignment.opportunity and hasattr(assignment.opportunity, "stakeholder_id"):
                    if assignment.opportunity.stakeholder_id:
                        stakeholder_ids.add(assignment.opportunity.stakeholder_id)

        # Through company assignments
        if hasattr(model_instance, "company_assignments"):
            for assignment in model_instance.company_assignments:
                if assignment.company and hasattr(assignment.company, "stakeholders"):
                    for stakeholder in assignment.company.stakeholders:
                        stakeholder_ids.add(stakeholder.id)

        if stakeholder_ids:
            meta["stakeholder_relationships"] = f"{len(stakeholder_ids)}"

    elif entity_type == "task":
        # Task type and progress indicators
        if hasattr(model_instance, "task_type") and model_instance.task_type:
            if model_instance.task_type == "parent":
                # Multi-task with progress
                if hasattr(model_instance, "child_tasks"):
                    total_children = len(model_instance.child_tasks)
                    completed_children = sum(1 for child in model_instance.child_tasks if child.status == "complete")
                    meta["task_progress"] = f"{completed_children}/{total_children}"
                    meta["task_type_display"] = "multi"
                else:
                    meta["task_type_display"] = "multi"
                    meta["task_progress"] = "0/0"
            elif model_instance.task_type == "child":
                meta["task_type_display"] = "subtask"
            else:
                meta["task_type_display"] = "single"

    # Due date with relative time (for tasks, etc.)
    if hasattr(model_instance, "due_date") and model_instance.due_date:
        due_date = (
            model_instance.due_date.date()
            if isinstance(model_instance.due_date, datetime)
            else model_instance.due_date
        )
        meta["due_date"] = due_date.strftime("%B %d, %Y")
        meta["due"] = get_relative_time_only(due_date)

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
