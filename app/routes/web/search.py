from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import or_
from app.models import Task, Company, Stakeholder, Opportunity, User
from app.utils.core.model_introspection import get_model_by_name

search_bp = Blueprint("search", __name__)

# Get searchable entity types from model map  
def get_searchable_entity_types():
    """Get searchable entity types dynamically from model introspection"""
    # These are the models we want to include in search
    searchable_models = ['company', 'stakeholder', 'opportunity', 'task']
    
    entity_types = {}
    for model_name in searchable_models:
        model_class = get_model_by_name(model_name)
        if model_class:
            # Get friendly name and icon
            friendly_names = {
                'company': {'name': 'Companies', 'icon': '🏢'},
                'stakeholder': {'name': 'Contacts', 'icon': '👤'}, 
                'opportunity': {'name': 'Opportunities', 'icon': '💼'},
                'task': {'name': 'Tasks', 'icon': '✅'}
            }
            entity_types[model_name] = friendly_names.get(model_name, {'name': model_name.title(), 'icon': '📄'})
            
    return entity_types


@search_bp.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    entity_type = request.args.get("type", "all")
    limit = min(int(request.args.get("limit", 20)), 50)

    # Handle comma-separated entity types dynamically
    searchable_types = get_searchable_entity_types()
    if entity_type == "all":
        entity_types = list(searchable_types.keys())
    else:
        entity_types = [t.strip() for t in entity_type.split(",") if t.strip() in searchable_types]
        if not entity_types:
            entity_types = list(searchable_types.keys())

    results = []

    if "company" in entity_types:
        if query:
            companies = (
                Company.query.filter(
                    or_(
                        Company.name.ilike(f"%{query}%"),
                        Company.industry.ilike(f"%{query}%"),
                    )
                )
                .limit(limit)
                .all()
            )
        else:
            # Return all companies when no query
            companies = Company.query.limit(limit).all()

        for company in companies:
            results.append(
                {
                    "id": company.id,
                    "type": "company",
                    "title": company.name,
                    "subtitle": company.industry,
                    "url": f"/companies/{company.id}",
                }
            )

    if "stakeholder" in entity_types:
        if query:
            contacts = (
                Stakeholder.query.join(Company)
                .filter(
                    or_(
                        Stakeholder.name.ilike(f"%{query}%"),
                        Stakeholder.email.ilike(f"%{query}%"),
                        Stakeholder.job_title.ilike(f"%{query}%"),
                    )
                )
                .limit(limit)
                .all()
            )
        else:
            # Return all contacts when no query
            contacts = Stakeholder.query.join(Company).limit(limit).all()

        for contact in contacts:
            results.append(
                {
                    "id": contact.id,
                    "type": "contact",
                    "title": contact.name,
                    "subtitle": (
                        f"{contact.job_title} at {contact.company.name}"
                        if contact.job_title
                        else contact.company.name
                    ),
                    "url": f"/contacts/{contact.id}",
                }
            )

    if "opportunity" in entity_types:
        if query:
            opportunities = (
                Opportunity.query.join(Company)
                .filter(
                    or_(
                        Opportunity.name.ilike(f"%{query}%"),
                        Company.name.ilike(f"%{query}%"),
                    )
                )
                .limit(limit)
                .all()
            )
        else:
            # Return all opportunities when no query
            opportunities = Opportunity.query.join(Company).limit(limit).all()

        for opportunity in opportunities:
            results.append(
                {
                    "id": opportunity.id,
                    "type": "opportunity",
                    "title": opportunity.name,
                    "subtitle": (
                        f"{opportunity.company.name} • ${opportunity.value:,.0f}"
                        if opportunity.value
                        else opportunity.company.name
                    ),
                    "url": f"/opportunities/{opportunity.id}",
                }
            )

    if "task" in entity_types:
        if query:
            tasks = (
                Task.query.filter(Task.description.ilike(f"%{query}%"))
                .limit(limit)
                .all()
            )
        else:
            # Return all tasks when no query
            tasks = Task.query.limit(limit).all()

        for task in tasks:
            results.append(
                {
                    "id": task.id,
                    "type": "task",
                    "title": task.description,
                    "subtitle": (
                        f'Due: {task.due_date.strftime("%m/%d/%y")}'
                        if task.due_date
                        else "No due date"
                    ),
                    "url": f"/tasks/{task.id}",
                }
            )

    # Sort by relevance if there's a query, otherwise by type and title
    if query:
        results.sort(key=lambda x: query.lower() in x["title"].lower(), reverse=True)
    else:
        # Sort by type first, then by title
        type_order = {"company": 0, "contact": 1, "opportunity": 2, "task": 3}
        results.sort(key=lambda x: (type_order.get(x["type"], 4), x["title"].lower()))

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
                "type": "contact",
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

    if "company" in entity_types:
        if query:
            companies = (
                Company.query.filter(
                    or_(
                        Company.name.ilike(f"%{query}%"),
                        Company.industry.ilike(f"%{query}%"),
                    )
                )
                .limit(limit)
                .all()
            )
        else:
            companies = Company.query.limit(limit).all()

        for company in companies:
            results.append({
                "id": company.id,
                "type": "company",
                "title": company.name,
                "subtitle": f"{company.industry} • {company.location}" if company.industry else company.location,
                "url": f"/companies/{company.id}",
            })

    if "stakeholder" in entity_types:
        if query:
            contacts = (
                Stakeholder.query.join(Company)
                .filter(
                    or_(
                        Stakeholder.name.ilike(f"%{query}%"),
                        Stakeholder.email.ilike(f"%{query}%"),
                        Company.name.ilike(f"%{query}%"),
                    )
                )
                .limit(limit)
                .all()
            )
        else:
            contacts = Stakeholder.query.join(Company).limit(limit).all()

        for contact in contacts:
            results.append({
                "id": contact.id,
                "type": "contact",
                "title": contact.name,
                "subtitle": (
                    f"{contact.job_title} at {contact.company.name}"
                    if contact.job_title
                    else contact.company.name
                ),
                "url": f"/contacts/{contact.id}",
            })

    if "opportunity" in entity_types:
        if query:
            opportunities = (
                Opportunity.query.join(Company)
                .filter(
                    or_(
                        Opportunity.name.ilike(f"%{query}%"),
                        Company.name.ilike(f"%{query}%"),
                    )
                )
                .limit(limit)
                .all()
            )
        else:
            opportunities = Opportunity.query.join(Company).limit(limit).all()

        for opportunity in opportunities:
            results.append({
                "id": opportunity.id,
                "type": "opportunity",
                "title": opportunity.name,
                "subtitle": f"{opportunity.company.name} • ${opportunity.value:,.0f}" if opportunity.value else opportunity.company.name,
                "url": f"/opportunities/{opportunity.id}",
            })

    if "task" in entity_types:
        if query:
            tasks = (
                Task.query.join(Company, Task.company)
                .filter(
                    or_(
                        Task.description.ilike(f"%{query}%"),
                        Company.name.ilike(f"%{query}%"),
                    )
                )
                .limit(limit)
                .all()
            )
        else:
            tasks = Task.query.join(Company, Task.company).limit(limit).all()

        for task in tasks:
            results.append({
                "id": task.id,
                "type": "task",
                "title": task.description,
                "subtitle": f"{task.company.name} • {task.priority}" if task.priority else task.company.name,
                "url": f"/tasks/{task.id}",
            })

    # Sort results by type and title
    if results:
        type_order = {"company": 0, "contact": 1, "opportunity": 2, "task": 3}
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
