from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app.models import Task, Company, Stakeholder, Opportunity

search_bp = Blueprint("search", __name__)


@search_bp.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    entity_type = request.args.get("type", "all")
    limit = min(int(request.args.get("limit", 20)), 50)

    results = []

    if entity_type in ["all", "companies"]:
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

    if entity_type in ["all", "contacts"]:
        if query:
            contacts = (
                Stakeholder.query.join(Company)
                .filter(
                    or_(
                        Stakeholder.name.ilike(f"%{query}%"),
                        Stakeholder.email.ilike(f"%{query}%"),
                        Stakeholder.role.ilike(f"%{query}%"),
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
                        f"{contact.role} at {contact.company.name}"
                        if contact.role
                        else contact.company.name
                    ),
                    "url": f"/contacts/{contact.id}",
                }
            )

    if entity_type in ["all", "opportunities"]:
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

    if entity_type in ["all", "tasks"]:
        if query:
            tasks = (
                Task.query.filter(Task.description.ilike(f"%{query}%")).limit(limit).all()
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


@search_bp.route("/api/autocomplete")
def autocomplete():
    query = request.args.get("q", "").strip()
    entity_type = request.args.get("type", "")
    limit = min(int(request.args.get("limit", 10)), 20)

    suggestions = []

    if entity_type == "company":
        if query:
            companies = (
                Company.query.filter(Company.name.ilike(f"%{query}%")).limit(limit).all()
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
                Stakeholder.query.filter(Stakeholder.name.ilike(f"%{query}%")).limit(limit).all()
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

    return jsonify(suggestions)
