"""Web routes for CRM entities - Ultra DRY, zero duplication."""

from flask import Blueprint, render_template, request
from collections import defaultdict
from app.models import MODEL_REGISTRY
from app.core.stats import StatsGenerator
from app.core.dropdowns import DropdownBuilder
from app.services import QueryService


entities_web_bp = Blueprint("entities", __name__)


def create_routes() -> None:
    """Dynamically create all routes based on MODEL_REGISTRY."""
    for entity_type, model in MODEL_REGISTRY.items():
        if not hasattr(model, "is_web_enabled") or not model.is_web_enabled():
            continue

        table_name = model.__tablename__

        # Create closures to capture model and table_name
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
            f"/{table_name}",
            f"{table_name}_index",
            make_index(model, table_name)
        )

        entities_web_bp.add_url_rule(
            f"/{table_name}/content",
            f"{table_name}_content",
            make_content(model, table_name)
        )

        # Add alternate routes for users -> teams
        if entity_type == "user":
            entities_web_bp.add_url_rule(
                "/teams",
                "teams_index",
                make_index(model, "users")
            )
            entities_web_bp.add_url_rule(
                "/teams/content",
                "teams_content",
                make_content(model, "users")
            )


def entity_index(model: type, table_name: str) -> str:
    """Render the index page for an entity type.

    Args:
        model: SQLAlchemy model class for the entity.
        table_name: Database table name for entity-specific stat generation.

    Returns:
        Rendered template with entity stats, dropdowns, and configuration.
    """
    # Generate dropdowns
    dropdown_configs = DropdownBuilder.build_all(model, request.args)

    # Generate stats
    stats_generator = StatsGenerator(model, table_name)
    stats_list = stats_generator.generate()

    # Build context
    context = {
        "entity_config": {
            "entity_name": model.get_display_name_plural(),
            "entity_description": f"Manage your {model.get_display_name_plural().lower()}",
            "entity_buttons": [
                {
                    "title": f"Add {model.get_display_name()}",
                    "url": f"/modals/{model.__name__.lower()}/create",
                    "variant": "primary"
                }
            ],
            "content_endpoint": f"entities.{table_name}_content",
        },
        "entity_stats": stats_list,
        "dropdown_configs": dropdown_configs,
        "model": model,
        "table_name": table_name,
    }

    return render_template("base/entity_index.html", **context)


def entity_content(model: type, table_name: str) -> str:
    """Render entity content with data based on filters, grouping, and sorting.

    Args:
        model: SQLAlchemy model class for the entity.
        table_name: Database table name (for context).

    Returns:
        Rendered template with filtered and grouped entity data.
    """
    # Parse request parameters
    group_by = request.args.get("group_by")
    sort_by = request.args.get("sort_by", "id")
    sort_direction = request.args.get("sort_direction", "asc")
    filters = {k: v for k, v in request.args.items()
               if not k.startswith(("group_by", "sort_"))}

    # Build and execute query
    query = QueryService.build_filtered_query(model, filters)
    query = QueryService.apply_sorting(query, model, sort_by, sort_direction)

    if group_by and hasattr(model, group_by):
        # Group entities
        grouped_entities = defaultdict(list)
        for entity in query.all():
            group_key = getattr(entity, group_by) or "No Group"
            if hasattr(group_key, "label"):
                group_key = group_key.label
            grouped_entities[str(group_key)].append(entity)

        context = {
            "grouped_entities": dict(grouped_entities),
            "entity_type": model.__name__.lower(),
            "is_grouped": True,
        }
        return render_template("shared/entity_content.html", **context)

    # Regular list view
    entities = query.all()
    context = {
        "entities": entities,
        "entity_type": model.__name__.lower(),
        "is_grouped": False,
    }
    return render_template("entity_cards.html", **context)


# Initialize routes on import
create_routes()