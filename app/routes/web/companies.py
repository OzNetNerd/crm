from datetime import date
from flask import Blueprint, render_template, request
from app.models import Company, Stakeholder, Opportunity, db
from app.utils.core.base_handlers import BaseRouteHandler, EntityFilterManager, EntityGrouper
from app.utils.core.model_introspection import ModelIntrospector
from collections import defaultdict

companies_bp = Blueprint("companies", __name__)
company_handler = BaseRouteHandler(Company, "companies")
company_filter_manager = EntityFilterManager(Company, "company")


def company_custom_filters(query, filters):
    """Company-specific filtering logic"""
    if filters['primary_filter']:
        query = query.filter(Company.industry.in_(filters['primary_filter']))
    return query


def company_custom_groupers(entities, group_by):
    """Company-specific grouping logic"""
    grouped = defaultdict(list)
    
    if group_by == "industry":
        for company in entities:
            industry = company.industry or "Other"
            grouped[industry].append(company)
        
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
        for company in entities:
            size = company.size_category or "Unknown"
            grouped[size].append(company)
        
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
    
    return None  # Use default grouping


def get_filtered_companies_context():
    """Server-side filtering and sorting for companies HTMX endpoints - DRY version"""
    return company_filter_manager.get_filtered_context(
        custom_filters=company_custom_filters,
        custom_grouper=company_custom_groupers
    )


@companies_bp.route("/content")
def content():
    """HTMX endpoint for filtered company content - DRY version"""
    context = company_filter_manager.get_content_context(
        custom_filters=company_custom_filters,
        custom_grouper=company_custom_groupers
    )
    
    return render_template("shared/entity_content.html", **context)


@companies_bp.route("/")
def index():
    from app.utils.ui.index_helpers import UniversalIndexHelper
    
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

    # Generate company stats directly
    entity_stats = {
        'title': 'Companies Overview',
        'stats': [
            {
                'value': len(companies),
                'label': 'Total Companies'
            },
            {
                'value': len([c for c in companies if c.industry]),
                'label': 'With Industry'
            },
            {
                'value': sum(len(c.stakeholders or []) for c in companies),
                'label': 'Total Stakeholders'
            },
            {
                'value': sum(len(c.opportunities or []) for c in companies),
                'label': 'Total Opportunities'
            }
        ]
    }
    
    # Get standardized context using universal helper
    context = UniversalIndexHelper.get_standardized_index_context(
        entity_name='companies',
        default_group_by='industry',
        default_sort_by='name',
        additional_context={
            'entity_stats': entity_stats,
            'companies': companies,
            'companies_data': companies_data,
        }
    )

    return render_template("base/entity_index.html", **context)




