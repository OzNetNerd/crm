"""
DRY Search Routes - Using model search methods

Clean, maintainable search using BaseModel search capabilities.
"""

from flask import Blueprint, request, jsonify, render_template
import json
from app.models import MODEL_REGISTRY

search_bp = Blueprint("search", __name__)


@search_bp.route("/api/search")
def search():
    """Main search endpoint - searches all registered models."""
    query = request.args.get("q", "").strip()
    entity_type = request.args.get("type", "all")
    limit = min(int(request.args.get("limit", 20)), 50)

    # Determine which models to search
    if entity_type == "all":
        models_to_search = MODEL_REGISTRY.values()
    else:
        # Parse comma-separated types
        type_list = [t.strip() for t in entity_type.split(",")]
        models_to_search = [
            MODEL_REGISTRY.get(t) for t in type_list if t in MODEL_REGISTRY
        ]
        models_to_search = [m for m in models_to_search if m]  # Filter None

    # Collect results from all models
    results = []
    for model in models_to_search:
        try:
            entities = model.search(query, limit)
            results.extend([e.to_search_result() for e in entities])
        except Exception:
            # If a model doesn't support search, skip it
            continue

    # Sort by type order and title
    type_order = {name: i for i, name in enumerate(MODEL_REGISTRY.keys())}
    results.sort(
        key=lambda x: (type_order.get(x["type"], 99), x.get("title", "").lower())
    )

    return jsonify(results[:limit])


@search_bp.route("/api/search/entity-types")
def get_entity_types():
    """Get available entity types for search filters."""
    entity_types = {}

    # Use MODEL_REGISTRY as source of truth
    for model_name, model_class in MODEL_REGISTRY.items():
        entity_types[model_name] = {
            "name": model_class.get_display_name_plural(),
            "icon": model_name,  # Frontend will map to appropriate icon
        }

    return jsonify(entity_types)


@search_bp.route("/api/autocomplete")
def autocomplete():
    """Autocomplete endpoint for entity selection."""
    entity_type = request.args.get("type", "")
    query = request.args.get("q", "").strip()
    limit = min(int(request.args.get("limit", 10)), 20)

    # Get the model from registry
    model = MODEL_REGISTRY.get(entity_type)
    if not model:
        return jsonify([])

    # Search the model
    entities = model.search(query, limit)

    # Build autocomplete results
    suggestions = []
    for entity in entities:
        result = {
            "id": entity.id,
            "name": entity._get_search_title(),
            "type": entity_type,
        }

        # Add company name for entities that have it
        if hasattr(entity, "company") and entity.company:
            result["company"] = entity.company.name

        suggestions.append(result)

    return jsonify(suggestions)


def get_task_field_options(field_type, query=""):
    """Get task field options for dynamic search."""
    from app.models.task import Task

    # Define the available options for each field type
    field_options = {
        'task_type': [
            {'value': 'follow_up', 'label': 'Follow Up'},
            {'value': 'meeting', 'label': 'Meeting'},
            {'value': 'call', 'label': 'Phone Call'},
            {'value': 'email', 'label': 'Email'},
            {'value': 'proposal', 'label': 'Proposal'},
            {'value': 'demo', 'label': 'Demo'},
            {'value': 'review', 'label': 'Review'},
            {'value': 'other', 'label': 'Other'},
        ],
        'task_status': [
            {'value': 'pending', 'label': 'Pending'},
            {'value': 'in_progress', 'label': 'In Progress'},
            {'value': 'completed', 'label': 'Completed'},
            {'value': 'cancelled', 'label': 'Cancelled'},
        ],
        'task_priority': [
            {'value': 'low', 'label': 'Low'},
            {'value': 'medium', 'label': 'Medium'},
            {'value': 'high', 'label': 'High'},
            {'value': 'urgent', 'label': 'Urgent'},
        ]
    }

    options = field_options.get(field_type, [])

    # Filter options based on query
    if query:
        query_lower = query.lower()
        options = [opt for opt in options if query_lower in opt['label'].lower()]

    # Convert to search result format
    results = []
    for opt in options:
        results.append({
            'id': opt['value'],
            'title': opt['label'],
            'subtitle': '',
            'type': 'task_field',
            'icon': '📋',
            'model_type': 'task_field'
        })

    return results


def get_assignment_options(query=""):
    """Get assignment options including 'me', users, stakeholders, and account team."""
    from app.models.user import User
    from app.models.stakeholder import Stakeholder
    from flask import session

    results = []

    # Add "Me" option first
    if not query or 'me' in query.lower():
        results.append({
            'id': 'me',
            'title': 'Me (Current User)',
            'subtitle': 'Assign to yourself',
            'type': 'assignment',
            'icon': '👤',
            'model_type': 'assignment'
        })

    # Add users (team members)
    if query:
        users = User.query.filter(User.name.ilike(f'%{query}%')).limit(10).all()
    else:
        users = User.query.limit(10).all()

    for user in users:
        results.append({
            'id': f'user_{user.id}',
            'title': user.name,
            'subtitle': f'{user.job_title} - Team Member' if user.job_title else 'Team Member',
            'type': 'assignment',
            'icon': '👥',
            'model_type': 'assignment'
        })

    # Add stakeholders (external contacts)
    if query:
        stakeholders = Stakeholder.query.filter(Stakeholder.name.ilike(f'%{query}%')).limit(5).all()
    else:
        stakeholders = Stakeholder.query.limit(5).all()

    for stakeholder in stakeholders:
        results.append({
            'id': f'stakeholder_{stakeholder.id}',
            'title': stakeholder.name,
            'subtitle': f'{stakeholder.job_title} - Stakeholder' if stakeholder.job_title else 'Stakeholder',
            'type': 'assignment',
            'icon': '🤝',
            'model_type': 'assignment'
        })

    return results


@search_bp.route("/htmx/search")
def htmx_search():
    """HTMX endpoint for live search - returns HTML instead of JSON."""
    query = request.args.get("q", "").strip()
    # Support both 'type' and 'entity_type' for backward compatibility
    entity_type = request.args.get("type") or request.args.get("entity_type", "all")
    limit = min(int(request.args.get("limit", 10)), 20)
    mode = request.args.get("mode", "modal")  # 'modal' or 'select'
    field_id = request.args.get("field_id", "")
    field_name = request.args.get("field_name", "")

    # Handle choice fields as virtual entities
    if entity_type.startswith("choice:"):
        choice_field = entity_type.split(":", 1)[1]
        return _handle_choice_search(query, choice_field, mode, field_name)

    # Handle special task field searches
    if entity_type in ['task_type', 'task_status', 'task_priority']:
        results = get_task_field_options(entity_type, query)
    elif entity_type == 'assignment':
        results = get_assignment_options(query)
    else:
        # Reuse the main search logic for entity searches
        if entity_type == "all":
            models_to_search = MODEL_REGISTRY.values()
        else:
            type_list = [t.strip() for t in entity_type.split(",")]
            models_to_search = [
                MODEL_REGISTRY.get(t) for t in type_list if t in MODEL_REGISTRY
            ]
            models_to_search = [m for m in models_to_search if m]

        # Collect results
        results = []

        # Distribute results across entity types for better diversity
        items_per_type = (
            max(1, limit // len(models_to_search)) if models_to_search else limit
        )

        for model in models_to_search:
            try:
                entities = model.search(query, items_per_type)
                results.extend([e.to_search_result() for e in entities])
            except Exception:
                continue

        # Sort and limit
        type_order = {name: i for i, name in enumerate(MODEL_REGISTRY.keys())}
        results.sort(
            key=lambda x: (type_order.get(x["type"], 99), x.get("title", "").lower())
        )
        results = results[:limit]

    return render_template(
        "components/search/results.html",
        results=results,
        query=query,
        mode=mode,
        field_id=field_id,
        field_name=field_name,
    )


def _handle_choice_search(query, choice_field, mode, field_name):
    """Handle choice field search by converting choices to search results."""
    from app.forms import get_field_choices

    # Get choices for the field
    choices = get_field_choices(choice_field)
    if not choices:
        return render_template(
            "components/search/results.html",
            results=[],
            query=query,
            mode=mode,
            field_name=field_name,
        )

    # Convert choices to search results format
    results = []
    query_lower = query.lower()

    for key, choice_data in choices.items():
        label = choice_data.get("label", "")
        description = choice_data.get("description", "")

        # Filter based on query
        if not query or (query_lower in label.lower() or
                        query_lower in description.lower() or
                        query_lower in key.lower()):
            results.append({
                "id": key,
                "title": label,
                "description": description,
                "type": "choice",
                "url": "#"  # Not used for choices
            })

    # Sort by label, with custom ordering for stage field
    if choice_field == "stage":
        # Define custom order for pipeline stages
        stage_order = ["prospect", "qualified", "proposal", "negotiation", "closed-won", "closed-lost"]
        stage_order_map = {stage: i for i, stage in enumerate(stage_order)}
        results.sort(key=lambda x: stage_order_map.get(x["id"].lower(), 999))
    else:
        results.sort(key=lambda x: x["title"])

    return render_template(
        "components/search/results.html",
        results=results,
        query=query,
        mode=mode,
        field_name=field_name,
    )


