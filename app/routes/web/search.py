"""
DRY Search Routes - Using model search methods

Clean, maintainable search using BaseModel search capabilities.
"""

from flask import Blueprint, request, jsonify, render_template
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


@search_bp.route("/htmx/search")
def htmx_search():
    """HTMX endpoint for live search - returns HTML instead of JSON."""
    query = request.args.get("q", "").strip()
    entity_type = request.args.get("type", "all")
    limit = min(int(request.args.get("limit", 10)), 20)
    mode = request.args.get("mode", "modal")  # 'modal' or 'select'
    field_id = request.args.get("field_id", "")

    # Reuse the main search logic
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
    )
