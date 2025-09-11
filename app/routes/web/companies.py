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
    
    # Ultra-DRY one-line dropdown generation using pure model introspection
    from app.utils.form_configs import DropdownConfigGenerator
    dropdown_configs = DropdownConfigGenerator.generate_entity_dropdown_configs('companies', group_by, sort_by, sort_direction, primary_filter)
    
    # Entity stats for summary cards
    entity_stats = {
        'title': 'Company Overview',
        'stats': [
            {
                'value': len(companies),
                'label': 'Total Companies',
                'color_class': 'text-blue-600'
            },
            {
                'value': len([c for c in companies if c.industry]),
                'label': 'With Industry',
                'color_class': 'text-green-600'
            },
            {
                'value': sum(len(c.stakeholders or []) for c in companies),
                'label': 'Total Stakeholders',
                'color_class': 'text-purple-600'
            },
            {
                'value': sum(len(c.opportunities or []) for c in companies),
                'label': 'Total Opportunities',
                'color_class': 'text-yellow-600'
            }
        ]
    }
    
    # Entity buttons for header
    entity_buttons = [
        {
            'label': 'New Company',
            'hx_get': '/modals/Company/create',
            'hx_target': 'body',
            'hx_swap': 'beforeend',
            'icon': '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>'
        }
    ]

    return render_template(
        "base/entity_index.html",
        entity_name="Companies",
        entity_description="Manage your company relationships",
        entity_type="company",
        entity_endpoint="companies",
        entity_stats=entity_stats,
        entity_buttons=entity_buttons,
        dropdown_configs=dropdown_configs,
        companies=companies,
        companies_data=companies_data,
    )




