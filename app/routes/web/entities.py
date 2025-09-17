"""
Web routes for CRM entities - Fully dynamic, zero hardcoding.
"""

from flask import Blueprint, render_template, request
from collections import defaultdict
from app.models import db, MODEL_REGISTRY

# Create blueprint
entities_web_bp = Blueprint("entities", __name__)


def build_filter_dropdowns(metadata, request_args):
    """Build filter dropdowns for fields with choices."""
    dropdowns = {}
    for field_name, field_info in metadata.items():
        if not (field_info.get("filterable") and field_info.get("choices")):
            continue

        options = [{"value": "", "label": f'All {field_info["label"]}'}]
        for choice_value, choice_data in field_info["choices"].items():
            options.append(
                {"value": choice_value, "label": choice_data.get("label", choice_value)}
            )

        dropdowns[f"filter_{field_name}"] = {
            "name": field_name,
            "options": options,
            "current_value": request_args.get(field_name, ""),
            "placeholder": f'All {field_info["label"]}',
            "multiple": False,
            "searchable": False,
        }
    return dropdowns


def build_group_dropdown(metadata, request_args):
    """Build group-by dropdown if groupable fields exist."""
    groupable_fields = [
        {"value": field_name, "label": field_info["label"]}
        for field_name, field_info in metadata.items()
        if field_info.get("groupable")
    ]

    if not groupable_fields:
        return None

    return {
        "options": groupable_fields,
        "current_value": request_args.get("group_by", ""),
        "placeholder": "Group by...",
        "multiple": False,
        "searchable": True,
    }


def build_sort_dropdown(metadata, request_args, default_sort):
    """Build sort-by dropdown with all sortable fields."""
    sortable_fields = [
        {"value": field_name, "label": field_info["label"]}
        for field_name, field_info in metadata.items()
        if field_info.get("sortable")
    ]

    # Ensure ID is always sortable
    has_id = any(field["value"] == "id" for field in sortable_fields)
    if not has_id:
        sortable_fields.append({"value": "id", "label": "ID"})

    return {
        "options": sortable_fields,
        "current_value": request_args.get("sort_by", default_sort),
        "placeholder": "Sort by...",
        "multiple": False,
        "searchable": True,
    }


def build_direction_dropdown(request_args):
    """Build sort direction dropdown."""
    return {
        "options": [
            {"value": "asc", "label": "Ascending"},
            {"value": "desc", "label": "Descending"},
        ],
        "current_value": request_args.get("sort_direction", "asc"),
        "placeholder": "Order",
        "multiple": False,
        "searchable": False,
    }


def build_dropdown_configs(model, request_args):
    """Build all dropdown configurations for entity UI using services."""
    from app.services import MetadataService

    metadata = MetadataService.get_field_metadata(model)
    dropdowns = {}

    # Add filter dropdowns
    dropdowns.update(build_filter_dropdowns(metadata, request_args))

    # Add group dropdown if applicable
    if group_dropdown := build_group_dropdown(metadata, request_args):
        dropdowns["group_by"] = group_dropdown

    # Add sort dropdowns
    dropdowns["sort_by"] = build_sort_dropdown(
        metadata, request_args, MetadataService.get_default_sort_field(model)
    )
    dropdowns["sort_direction"] = build_direction_dropdown(request_args)

    return dropdowns


def create_routes():
    """Dynamically create all routes based on MODEL_REGISTRY"""
    for entity_type, model in MODEL_REGISTRY.items():
        # Let models control their own exposure
        if not hasattr(model, "is_web_enabled") or not model.is_web_enabled():
            continue

        table_name = model.__tablename__

        # Create closures to capture the model
        def make_index(model, table_name):
            def handler():
                return entity_index(model, table_name)

            handler.__name__ = f"{table_name}_index"
            return handler

        def make_content(model, table_name):
            def handler():
                return entity_content(model, table_name)

            handler.__name__ = f"{table_name}_content"
            return handler

        # Register routes
        entities_web_bp.add_url_rule(
            f"/{table_name}", f"{table_name}_index", make_index(model, table_name)
        )

        entities_web_bp.add_url_rule(
            f"/{table_name}/content",
            f"{table_name}_content",
            make_content(model, table_name),
        )

        # Add alternate routes for users -> teams
        if entity_type == "user":
            entities_web_bp.add_url_rule(
                "/teams", "teams_index", make_index(model, "users")
            )
            entities_web_bp.add_url_rule(
                "/teams/content", "teams_content", make_content(model, "users")
            )


def entity_index(model, table_name):
    """
    Render the index page for an entity type with stats, filters, and controls.

    Generates comprehensive statistics based on entity type (companies, stakeholders, etc),
    builds dropdown configurations for filtering/sorting, and renders the entity list page.

    Args:
        model: SQLAlchemy model class for the entity
        table_name: Database table name for entity-specific stat generation

    Returns:
        Rendered template with entity stats, dropdowns, and configuration
    """
    dropdown_configs = build_dropdown_configs(model, request.args)

    # Import needed functions
    from sqlalchemy import func
    from datetime import datetime, timedelta

    # Get basic stats
    display_name_plural = model.get_display_name_plural()
    display_name = model.get_display_name()
    total = model.query.count()

    # Initialize stats list
    stats_list = []

    # Always add total count
    stats_list.append({"value": total, "label": f"Total {display_name_plural}"})

    # Add entity-specific stats
    if table_name == "companies":
        # Companies stats
        from app.models import Opportunity, Stakeholder

        # Active companies (with opportunities)
        active_companies = db.session.query(func.count(func.distinct(model.id)))\
            .join(Opportunity).scalar() or 0
        stats_list.append({"value": active_companies, "label": "Active Companies"})

        # Total opportunities
        total_opps = Opportunity.query.count()
        stats_list.append({"value": total_opps, "label": "Total Opportunities"})

        # Industry breakdown - get top industry
        top_industry = db.session.query(model.industry, func.count(model.id))\
            .filter(model.industry.isnot(None))\
            .group_by(model.industry)\
            .order_by(func.count(model.id).desc())\
            .first()
        if top_industry:
            stats_list.append({"value": top_industry[1], "label": f"In {top_industry[0].title()}"})

    elif table_name == "stakeholders":
        # Stakeholders stats
        from app.models import Company

        # Decision makers (based on job title)
        decision_makers = model.query.filter(
            db.or_(
                model.job_title.ilike('%CEO%'),
                model.job_title.ilike('%CTO%'),
                model.job_title.ilike('%CFO%'),
                model.job_title.ilike('%President%'),
                model.job_title.ilike('%VP%'),
                model.job_title.ilike('%Director%'),
                model.job_title.ilike('%Vice President%')
            )
        ).count()
        stats_list.append({"value": decision_makers, "label": "Decision Makers"})

        # With email
        with_email = model.query.filter(model.email.isnot(None)).count()
        stats_list.append({"value": with_email, "label": "With Email"})

        # Companies represented
        companies = db.session.query(func.count(func.distinct(model.company_id))).scalar() or 0
        stats_list.append({"value": companies, "label": "Companies"})

    elif table_name == "opportunities":
        # Opportunities stats
        from app.models import Opportunity

        # Pipeline value
        total_value = db.session.query(func.sum(model.value)).scalar() or 0
        if total_value > 1000000:
            value_str = f"${total_value/1000000:.1f}M"
        elif total_value > 1000:
            value_str = f"${total_value/1000:.0f}K"
        else:
            value_str = f"${total_value:.0f}"
        stats_list.append({"value": value_str, "label": "Pipeline Value"})

        # Average deal size
        avg_value = db.session.query(func.avg(model.value)).scalar() or 0
        if avg_value > 1000:
            avg_str = f"${avg_value/1000:.0f}K"
        else:
            avg_str = f"${avg_value:.0f}"
        stats_list.append({"value": avg_str, "label": "Avg Deal Size"})

        # Win rate (if closed won/lost)
        closed_won = model.query.filter_by(stage='closed_won').count()
        closed_lost = model.query.filter_by(stage='closed_lost').count()
        total_closed = closed_won + closed_lost
        if total_closed > 0:
            win_rate = int((closed_won / total_closed) * 100)
            stats_list.append({"value": f"{win_rate}%", "label": "Win Rate"})
        else:
            stats_list.append({"value": "N/A", "label": "Win Rate"})

    elif table_name == "tasks":
        # Tasks stats
        # Overdue tasks
        overdue = model.query.filter(
            model.due_date < datetime.now().date(),
            model.status != 'completed'
        ).count()
        stats_list.append({"value": overdue, "label": "Overdue"})

        # Due this week
        week_end = datetime.now().date() + timedelta(days=7)
        due_this_week = model.query.filter(
            model.due_date <= week_end,
            model.due_date >= datetime.now().date(),
            model.status != 'completed'
        ).count()
        stats_list.append({"value": due_this_week, "label": "Due This Week"})

        # Completed
        completed = model.query.filter_by(status='completed').count()
        stats_list.append({"value": completed, "label": "Completed"})

    elif table_name == "users":
        # Users/Account Teams stats
        from app.models import Task, Opportunity

        # Active users (with tasks)
        active_users = db.session.query(func.count(func.distinct(Task.assigned_to_id))).scalar() or 0
        stats_list.append({"value": active_users, "label": "Active Members"})

        # Opportunities owned
        opps_owned = db.session.query(func.count(Opportunity.id))\
            .filter(Opportunity.owner_id.isnot(None)).scalar() or 0
        stats_list.append({"value": opps_owned, "label": "Opportunities Owned"})

        # Open tasks
        open_tasks = Task.query.filter(Task.status != 'completed').count()
        stats_list.append({"value": open_tasks, "label": "Open Tasks"})

    # Add status breakdown for models with status field
    if hasattr(model, "status") and table_name not in ["tasks"]:  # Tasks already handled above
        status_counts = (
            db.session.query(model.status, func.count(model.id))
            .group_by(model.status)
            .all()
        )
        for status, count in status_counts:
            if status and len(stats_list) < 6:  # Limit to 6 stats cards
                stats_list.append(
                    {
                        "value": count,
                        "label": status.replace("-", " ").replace("_", " ").title(),
                    }
                )

    # Build stats dict
    stats = {
        "title": f"{display_name_plural} Overview",
        "stats": stats_list
    }

    # Build entity config for template using services
    from app.services import DisplayService

    entity_config = DisplayService.build_entity_config(model)

    return render_template(
        "base/entity_index.html",
        entity_config=entity_config,
        dropdown_configs=dropdown_configs,
        entity_stats=stats,
    )


def entity_content(model, table_name):
    """
    Render the HTMX content partial for entity lists with filtering, grouping, and sorting.

    Applies URL parameters for filtering, grouping, and sorting to the query,
    then renders grouped entity cards via HTMX for dynamic updates.

    Args:
        model: SQLAlchemy model class for the entity
        table_name: Database table name (used for model registry lookup)

    Returns:
        Rendered HTMX partial with grouped/sorted/filtered entities
    """
    # Get params
    group_by = request.args.get("group_by", "")
    sort_by = request.args.get("sort_by", model.get_default_sort_field())
    sort_direction = request.args.get("sort_direction", "asc")

    # Build query
    query = model.query

    # Detect and handle joins for _name fields
    if sort_by.endswith("_name"):
        # Try to find the related model
        base_field = sort_by.replace("_name", "")
        if hasattr(model, f"{base_field}_id"):
            # Find the relationship
            for rel in model.__mapper__.relationships:
                if rel.key == base_field:
                    related_model = rel.mapper.class_
                    query = query.join(related_model)
                    sort_field = related_model.name
                    break
            else:
                sort_field = (
                    getattr(model, sort_by) if hasattr(model, sort_by) else model.id
                )
        else:
            sort_field = (
                getattr(model, sort_by) if hasattr(model, sort_by) else model.id
            )
    else:
        sort_field = getattr(model, sort_by) if hasattr(model, sort_by) else model.id

    # Apply filters dynamically from request args using services
    from app.services import MetadataService

    metadata = MetadataService.get_field_metadata(model)
    for field_name, field_info in metadata.items():
        if field_info["filterable"]:
            filter_value = request.args.get(field_name)
            if filter_value and hasattr(model, field_name):
                query = query.filter(getattr(model, field_name) == filter_value)

    # Apply sorting
    query = query.order_by(
        sort_field.desc() if sort_direction == "desc" else sort_field.asc()
    )

    entities = query.all()

    # Group if needed
    grouped_entities = []
    if group_by and hasattr(model, group_by):
        grouped = defaultdict(list)
        for entity in entities:
            key = getattr(entity, group_by, "Other") or "Uncategorized"
            grouped[key].append(entity)

        grouped_entities = [
            {"key": k, "label": k, "count": len(v), "entities": v}
            for k, v in grouped.items()
        ]
    else:
        grouped_entities = [
            {
                "key": "all",
                "label": "All Results",
                "count": len(entities),
                "entities": entities,
            }
        ]

    # Build template context
    from app.models import MODEL_REGISTRY

    entity_type = next(
        (key for key, value in MODEL_REGISTRY.items() if value == model),
        model.__name__.lower(),
    )

    return render_template(
        "shared/entity_content.html",
        grouped_entities=grouped_entities,
        group_by=group_by,
        total_count=len(entities),
        entity_type=entity_type,
        entity_name=model.get_display_name_plural(),
        entity_name_singular=model.get_display_name(),
        entity_name_plural=model.get_display_name_plural(),
    )


# Create all routes dynamically
create_routes()
