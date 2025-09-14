from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import or_
from app.models import Task, Company, Stakeholder, Opportunity, User, MODEL_REGISTRY

search_bp = Blueprint("search", __name__)

# Use MODEL_REGISTRY from app.models - single source of truth

# DRY entity configuration for dynamic search results
ENTITY_CONFIGS = {
    'company': {
        'model': Company,
        'type_label': 'company',
        'search_fields': ['name', 'industry'],
        'title_field': 'name',
        'subtitle_fields': ['industry'],
        'icon': '🏢'
    },
    'stakeholder': {
        'model': Stakeholder,
        'type_label': 'stakeholder',
        'search_fields': ['name', 'email', 'job_title'],
        'title_field': 'name',
        'subtitle_fields': ['job_title', 'company.name'],
        'icon': '👤',
        'joins': [Company]
    },
    'opportunity': {
        'model': Opportunity,
        'type_label': 'opportunity',
        'search_fields': ['name', 'company.name'],
        'title_field': 'name',
        'subtitle_fields': ['company.name', 'value'],
        'icon': '💼',
        'joins': [Company]
    },
    'task': {
        'model': Task,
        'type_label': 'task',
        'search_fields': ['description'],
        'title_field': 'description',
        'subtitle_fields': ['due_date', 'priority'],
        'icon': '✅'
    }
}

def generate_entity_result(entity, entity_type, config):
    """Generate a standardized search result for any entity type"""
    title = getattr(entity, config['title_field'])

    # Build subtitle dynamically from configured fields
    subtitle_parts = []
    for field in config.get('subtitle_fields', []):
        if '.' in field:
            # Handle nested fields like 'company.name'
            obj = entity
            for part in field.split('.'):
                obj = getattr(obj, part, None)
                if obj is None:
                    break
            if obj:
                subtitle_parts.append(str(obj))
        else:
            value = getattr(entity, field, None)
            if value:
                # Special formatting for different field types
                if field == 'value' and hasattr(entity, 'value'):
                    subtitle_parts.append(f"${value:,.0f}")
                elif field == 'due_date' and hasattr(entity, 'due_date'):
                    subtitle_parts.append(f'Due: {value.strftime("%m/%d/%y")}')
                else:
                    subtitle_parts.append(str(value))

    return {
        "id": entity.id,
        "type": config['type_label'],
        "model_type": entity_type,  # Add model type for modal system
        "title": title,
        "subtitle": " • ".join(subtitle_parts) if subtitle_parts else "",
        "url": f"/modals/{entity_type}/{entity.id}/view",
        "icon": config.get('icon', '📄')
    }

def search_entities(entity_type, query, limit, config):
    """DRY search function for any entity type"""
    model = config['model']

    # Build base query
    base_query = model.query

    # Add joins if specified
    if 'joins' in config:
        for join_model in config['joins']:
            base_query = base_query.join(join_model)

    if query:
        # Build search conditions dynamically
        search_conditions = []
        for field in config['search_fields']:
            if '.' in field:
                # Handle nested fields like 'company.name'
                obj = model
                for part in field.split('.')[:-1]:
                    # Get the relationship
                    obj = getattr(obj, part).property.mapper.class_
                field_name = field.split('.')[-1]
                search_attr = getattr(obj, field_name)
            else:
                search_attr = getattr(model, field)

            search_conditions.append(search_attr.ilike(f"%{query}%"))

        entities = base_query.filter(or_(*search_conditions)).limit(limit).all()
    else:
        entities = base_query.limit(limit).all()

    return [generate_entity_result(entity, entity_type, config) for entity in entities]

# Get searchable entity types from model map
def get_searchable_entity_types():
    """Get searchable entity types dynamically from model introspection"""
    # These are the models we want to include in search
    searchable_models = ['company', 'stakeholder', 'opportunity', 'task']
    
    entity_types = {}
    for model_name in searchable_models:
        model_class = MODEL_REGISTRY.get(model_name.lower())
        if model_class:
            # Get friendly name and icon
            friendly_names = {
                'company': {'name': 'Companies', 'icon': 'company'},
                'stakeholder': {'name': 'Stakeholders', 'icon': 'stakeholder'},
                'opportunity': {'name': 'Opportunities', 'icon': 'opportunity'},
                'task': {'name': 'Tasks', 'icon': 'task'}
            }
            entity_types[model_name] = friendly_names.get(model_name, {'name': model_name.title(), 'icon': model_name})
            
    return entity_types


@search_bp.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    entity_type = request.args.get("type", "all")
    limit = min(int(request.args.get("limit", 20)), 50)

    results = _perform_search(query, entity_type, limit)
    return jsonify(results[:limit])


@search_bp.route("/api/search/entity-types")
def get_entity_types():
    """Get available entity types for search filters"""
    entity_types = get_searchable_entity_types()
    return jsonify(entity_types)


@search_bp.route("/api/autocomplete")
def autocomplete():
    query = request.args.get("q", "").strip()
    entity_type = request.args.get("type", "")
    limit = min(int(request.args.get("limit", 10)), 20)

    suggestions = []

    if entity_type == "company":
        if query:
            companies = (
                Company.query.filter(Company.name.ilike(f"%{query}%"))
                .limit(limit)
                .all()
            )
        else:
            # Return all companies when no query
            companies = Company.query.limit(limit).all()

        suggestions = [
            {"id": company.id, "name": company.name, "type": "company"}
            for company in companies
        ]

    elif entity_type == "stakeholder":
        if query:
            contacts = (
                Stakeholder.query.filter(Stakeholder.name.ilike(f"%{query}%"))
                .limit(limit)
                .all()
            )
        else:
            # Return all contacts when no query
            contacts = Stakeholder.query.limit(limit).all()

        suggestions = [
            {
                "id": contact.id,
                "name": contact.name,
                "type": "stakeholder",
                "company": contact.company.name if contact.company else "",
            }
            for contact in contacts
        ]

    elif entity_type == "opportunity":
        if query:
            opportunities = (
                Opportunity.query.filter(Opportunity.name.ilike(f"%{query}%"))
                .limit(limit)
                .all()
            )
        else:
            # Return all opportunities when no query
            opportunities = Opportunity.query.limit(limit).all()

        suggestions = [
            {
                "id": opportunity.id,
                "name": opportunity.name,
                "type": "opportunity",
                "company": opportunity.company.name if opportunity.company else "",
            }
            for opportunity in opportunities
        ]

    elif entity_type == "user":
        if query:
            users = (
                User.query.filter(
                    or_(
                        User.name.ilike(f"%{query}%"),
                        User.job_title.ilike(f"%{query}%"),
                    )
                )
                .limit(limit)
                .all()
            )
        else:
            # Return all users when no query
            users = User.query.limit(limit).all()

        suggestions = [
            {
                "id": user.id,
                "name": user.name,
                "type": "user",
                "company": user.job_title if user.job_title else "",
            }
            for user in users
        ]

    return jsonify(suggestions)


def _perform_search(query, entity_type, limit):
    """Common search logic used by both JSON and HTMX endpoints"""
    searchable_types = get_searchable_entity_types()
    if entity_type == "all":
        entity_types = list(searchable_types.keys())
    else:
        entity_types = [t.strip() for t in entity_type.split(",") if t.strip() in searchable_types]
        if not entity_types:
            entity_types = list(searchable_types.keys())

    results = []

    # Use DRY search for all configured entity types
    for entity_type in entity_types:
        if entity_type in ENTITY_CONFIGS:
            config = ENTITY_CONFIGS[entity_type]
            entity_results = search_entities(entity_type, query, limit, config)
            results.extend(entity_results)

    # Sort results by type and title
    if results:
        type_order = {"company": 0, "stakeholder": 1, "opportunity": 2, "task": 3}
        results.sort(key=lambda x: (type_order.get(x["type"], 4), x["title"].lower()))

    return results[:limit]


@search_bp.route("/htmx/search")
def htmx_search():
    """HTMX endpoint for live search - returns HTML instead of JSON"""
    query = request.args.get("q", "").strip()
    entity_type = request.args.get("type", "all")
    limit = min(int(request.args.get("limit", 10)), 20)

    results = _perform_search(query, entity_type, limit)
    return render_template('components/search_results.html', results=results, query=query)
