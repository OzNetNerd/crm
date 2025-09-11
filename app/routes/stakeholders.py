from datetime import date
from flask import Blueprint, render_template, request
from app.models import Stakeholder, Company, Opportunity
from app.utils.route_helpers import BaseRouteHandler
from app.utils.model_introspection import ModelIntrospector
from collections import defaultdict

stakeholders_bp = Blueprint("stakeholders", __name__)
stakeholder_handler = BaseRouteHandler(Stakeholder, "stakeholders")


@stakeholders_bp.route("/")
def index():
    # Get filter parameters for initial state and URL persistence
    group_by = request.args.get("group_by", "company")
    sort_by = request.args.get("sort_by", "name")
    sort_direction = request.args.get("sort_direction", "asc")
    show_incomplete = request.args.get("show_incomplete", "false").lower() == "true"
    primary_filter = (
        request.args.get("primary_filter", "").split(",")
        if request.args.get("primary_filter")
        else []
    )
    secondary_filter = (
        request.args.get("secondary_filter", "").split(",")
        if request.args.get("secondary_filter")
        else []
    )

    # Get all stakeholders for stats
    stakeholders = Stakeholder.query.join(Company).all()
    today = date.today()

    # Filter options for dropdowns
    group_options = [
        {'value': 'company', 'label': 'Company'},
        {'value': 'job_title', 'label': 'Job Title'}
    ]
    
    sort_options = [
        {'value': 'name', 'label': 'Name'},
        {'value': 'company', 'label': 'Company'}
    ]
    
    # Get unique job titles for primary filter
    job_title_options = []
    job_titles = Stakeholder.query.with_entities(Stakeholder.job_title).distinct().filter(Stakeholder.job_title.isnot(None)).all()
    for job_title_tuple in job_titles:
        job_title = job_title_tuple[0]
        if job_title:
            job_title_options.append({'value': job_title, 'label': job_title})

    # Get unique company names for secondary filter
    company_options = []
    companies = Company.query.with_entities(Company.name).distinct().all()
    for company_tuple in companies:
        company = company_tuple[0]
        if company:
            company_options.append({'value': company, 'label': company})

    return render_template(
        "stakeholders/index.html",
        stakeholders=stakeholders,
        today=today,
        # Filter states for URL persistence
        group_by=group_by,
        sort_by=sort_by,
        sort_direction=sort_direction,
        show_incomplete=show_incomplete,
        primary_filter=primary_filter,
        secondary_filter=secondary_filter,
        # Filter options for dropdowns
        group_options=group_options,
        sort_options=sort_options,
        job_title_options=job_title_options,
        company_options=company_options,
    )


def get_filtered_stakeholders_context():
    """Server-side filtering and sorting for stakeholders HTMX endpoints"""
    # Get filter parameters
    group_by = request.args.get("group_by", "company")
    sort_by = request.args.get("sort_by", "name")
    sort_direction = request.args.get("sort_direction", "asc")
    
    # Parse filter arrays
    primary_filter = []
    if request.args.get("primary_filter"):
        primary_filter = [p.strip() for p in request.args.get("primary_filter").split(",") if p.strip()]
    
    secondary_filter = []
    if request.args.get("secondary_filter"):
        secondary_filter = [p.strip() for p in request.args.get("secondary_filter").split(",") if p.strip()]

    # Start with base query
    query = Stakeholder.query.join(Company)
    
    # Apply filters
    if primary_filter:
        query = query.filter(Stakeholder.job_title.in_(primary_filter))
    
    if secondary_filter:
        query = query.filter(Company.name.in_(secondary_filter))
    
    # Apply sorting
    if sort_by == "name":
        if sort_direction == "desc":
            query = query.order_by(Stakeholder.name.desc())
        else:
            query = query.order_by(Stakeholder.name.asc())
    elif sort_by == "company":
        if sort_direction == "desc":
            query = query.order_by(Company.name.desc(), Stakeholder.name.asc())
        else:
            query = query.order_by(Company.name.asc(), Stakeholder.name.asc())
    else:
        # Default sort by name
        query = query.order_by(Stakeholder.name.asc())
    
    filtered_stakeholders = query.all()
    
    # Group stakeholders by the specified grouping
    grouped_stakeholders = group_stakeholders_by_field(filtered_stakeholders, group_by)
    
    return {
        "grouped_stakeholders": grouped_stakeholders,
        "group_by": group_by,
        "total_count": len(filtered_stakeholders),
        "sort_by": sort_by,
        "sort_direction": sort_direction,
        "primary_filter": primary_filter,
        "secondary_filter": secondary_filter,
        "today": date.today(),
    }


def group_stakeholders_by_field(stakeholders, group_by):
    """Group stakeholders by specified field"""
    grouped = defaultdict(list)
    
    if group_by == "company":
        for stakeholder in stakeholders:
            company_name = stakeholder.company.name if stakeholder.company else "No Company"
            grouped[company_name].append(stakeholder)
        
        # Return sorted by company name
        result = []
        for company_name in sorted(grouped.keys()):
            if grouped[company_name]:
                result.append({
                    "key": company_name,
                    "label": company_name,
                    "entities": grouped[company_name],
                    "count": len(grouped[company_name])
                })
        return result
        
    elif group_by == "job_title":
        for stakeholder in stakeholders:
            job_title = stakeholder.job_title or "Other"
            grouped[job_title].append(stakeholder)
        
        # Return sorted by job title
        result = []
        for job_title in sorted(grouped.keys()):
            if grouped[job_title]:
                result.append({
                    "key": job_title,
                    "label": job_title,
                    "entities": grouped[job_title],
                    "count": len(grouped[job_title])
                })
        return result
    
    else:
        # Default: no grouping, return all in one group
        return [{
            "key": "all",
            "label": "All Stakeholders",
            "entities": stakeholders,
            "count": len(stakeholders)
        }]


@stakeholders_bp.route("/content")
def content():
    """HTMX endpoint for filtered stakeholder content"""
    context = get_filtered_stakeholders_context()
    
    # Universal template configuration
    # Universal template configuration using model introspection
    context.update({
        'grouped_entities': context["grouped_stakeholders"],
        'entity_type': 'stakeholder',
        'entity_name_singular': 'stakeholder',
        'entity_name_plural': 'stakeholders',
        'card_config': ModelIntrospector.get_card_config(Stakeholder),
        'model_class': Stakeholder
    })
    
    return render_template("shared/entity_content.html", **context)


