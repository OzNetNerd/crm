from datetime import date
from flask import Blueprint, render_template, request
from app.models import Company, Stakeholder, Opportunity, db
from app.utils.route_helpers import BaseRouteHandler
from app.utils.model_introspection import ModelIntrospector
from collections import defaultdict

companies_bp = Blueprint("companies", __name__)
company_handler = BaseRouteHandler(Company, "companies")


def get_filtered_companies_context():
    """Server-side filtering and sorting for companies HTMX endpoints"""
    # Get filter parameters
    group_by = request.args.get("group_by", "industry")
    sort_by = request.args.get("sort_by", "name")
    sort_direction = request.args.get("sort_direction", "asc")
    
    # Parse filter arrays
    primary_filter = []
    if request.args.get("primary_filter"):
        primary_filter = [p.strip() for p in request.args.get("primary_filter").split(",") if p.strip()]

    # Start with base query
    query = Company.query
    
    # Apply filters
    if primary_filter:
        query = query.filter(Company.industry.in_(primary_filter))
    
    # Apply sorting
    if sort_by == "name":
        if sort_direction == "desc":
            query = query.order_by(Company.name.desc())
        else:
            query = query.order_by(Company.name.asc())
    elif sort_by == "industry":
        if sort_direction == "desc":
            query = query.order_by(Company.industry.desc())
        else:
            query = query.order_by(Company.industry.asc())
    else:
        # Default sort by name
        query = query.order_by(Company.name.asc())
    
    filtered_companies = query.all()
    
    # Group companies by the specified grouping
    grouped_companies = group_companies_by_field(filtered_companies, group_by)
    
    return {
        "grouped_companies": grouped_companies,
        "group_by": group_by,
        "total_count": len(filtered_companies),
        "sort_by": sort_by,
        "sort_direction": sort_direction,
        "primary_filter": primary_filter,
        "today": date.today(),
    }


def group_companies_by_field(companies, group_by):
    """Group companies by specified field"""
    grouped = defaultdict(list)
    
    if group_by == "industry":
        for company in companies:
            industry = company.industry or "Other"
            grouped[industry].append(company)
        
        # Return sorted by industry name
        result = []
        for industry in sorted(grouped.keys()):
            if grouped[industry]:
                result.append({
                    "key": industry,
                    "label": industry,
                    "entities": grouped[industry],
                    "count": len(grouped[industry])
                })
        return result
        
    elif group_by == "size":
        for company in companies:
            size = company.size_category or "Unknown"
            grouped[size].append(company)
        
        # Return in size order
        size_order = ["unknown", "small", "medium", "large", "Unknown"]
        result = []
        for size in size_order:
            if grouped[size]:
                result.append({
                    "key": size,
                    "label": size.title(),
                    "entities": grouped[size],
                    "count": len(grouped[size])
                })
        return result
    
    # Default: return all companies in one group
    return [{
        "key": "all",
        "label": "All Companies",
        "entities": companies,
        "count": len(companies)
    }]


@companies_bp.route("/content")
def content():
    """HTMX endpoint for filtered company content"""
    context = get_filtered_companies_context()
    
    # Universal template configuration using model introspection
    context.update({
        'grouped_entities': context["grouped_companies"],
        'entity_type': 'company',
        'entity_name_singular': 'company',
        'entity_name_plural': 'companies',
        'card_config': ModelIntrospector.get_card_config(Company),
        'model_class': Company
    })
    
    return render_template("shared/entity_content.html", **context)


@companies_bp.route("/")
def index():
    # Get filter parameters for initial state and URL persistence
    group_by = request.args.get("group_by", "industry")
    sort_by = request.args.get("sort_by", "name")
    sort_direction = request.args.get("sort_direction", "asc")
    show_completed = request.args.get("show_completed", "false").lower() == "true"
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
    entity_filter = (
        request.args.get("entity_filter", "").split(",")
        if request.args.get("entity_filter")
        else []
    )

    # Get all companies with relationships
    companies = Company.query.all()

    # Get all contacts and opportunities for global data
    contacts_objects = Stakeholder.query.all()
    opportunities_objects = Opportunity.query.all()

    # Convert to JSON-serializable format for JavaScript
    contacts_data = [
        {
            "id": contact.id,
            "name": contact.name,
            "email": contact.email,
            "phone": contact.phone,
            "role": contact.job_title,
            "company_id": contact.company_id,
        }
        for contact in contacts_objects
    ]

    opportunities_data = [
        {
            "id": opp.id,
            "name": opp.name,
            "value": float(opp.value) if opp.value else 0,
            "company_id": opp.company_id,
        }
        for opp in opportunities_objects
    ]

    companies_data = [
        {
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "website": company.website,
            "contacts": [c for c in contacts_data if c["company_id"] == company.id],
            "opportunities": [
                o for o in opportunities_data if o["company_id"] == company.id
            ],
            "created_at": (
                company.created_at.isoformat()
                if hasattr(company, "created_at") and company.created_at
                else None
            ),
        }
        for company in companies
    ]

    today = date.today()
    
    # Prepare filter options for the new HTMX controls (sorted alphabetically)
    group_options = sorted([
        {'value': 'industry', 'label': 'Industry'},
        {'value': 'size', 'label': 'Company Size'}
    ], key=lambda x: x['label'])
    
    sort_options = sorted([
        {'value': 'name', 'label': 'Name'},
        {'value': 'industry', 'label': 'Industry'}
    ], key=lambda x: x['label'])
    
    # Get unique industries from database for filter options (sorted alphabetically)
    industry_options = []
    industries = db.session.query(Company.industry).distinct().filter(Company.industry.isnot(None)).all()
    for industry_tuple in industries:
        industry = industry_tuple[0]
        if industry:
            industry_options.append({'value': industry, 'label': industry})
    industry_options = sorted(industry_options, key=lambda x: x['label'])

    # Create dropdown configurations for the new unified system
    dropdown_configs = {
        'group_by': {
            'button_text': 'Group by',
            'options': group_options,
            'current_value': group_by,
            'name': 'group_by',
            'hx_target': '#company-content',
            'hx_get': '/companies/content'
        },
        'sort_by': {
            'button_text': 'Sort by',
            'options': sort_options,
            'current_value': sort_by,
            'name': 'sort_by',
            'hx_target': '#company-content',
            'hx_get': '/companies/content'
        },
        'sort_direction': {
            'button_text': 'Order',
            'options': [
                {'value': 'asc', 'label': 'Ascending'},
                {'value': 'desc', 'label': 'Descending'}
            ],
            'current_value': sort_direction,
            'name': 'sort_direction',
            'hx_target': '#company-content',
            'hx_get': '/companies/content'
        },
        'industry_filter': {
            'button_text': 'All Industries',
            'options': industry_options,
            'current_values': primary_filter,
            'name': 'primary_filter'
        }
    }
    
    return render_template(
        "companies/index.html",
        companies=companies,
        contacts=contacts_data,
        opportunities=opportunities_data,
        companies_data=companies_data,
        today=today,
        # Filter states for URL persistence
        group_by=group_by,
        sort_by=sort_by,
        sort_direction=sort_direction,
        show_completed=show_completed,
        primary_filter=primary_filter,
        secondary_filter=secondary_filter,
        entity_filter=entity_filter,
        # New unified dropdown configurations
        dropdown_configs=dropdown_configs,
        # Legacy support - keep for backward compatibility during transition
        group_options=group_options,
        sort_options=sort_options,
        industry_options=industry_options,
    )




@companies_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        return company_handler.handle_create(
            name="name", industry="industry", website="website"
        )

    return render_template("companies/new.html")
