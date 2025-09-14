"""
Company web routes for the CRM application.

This module provides web endpoints for managing companies including
listing, filtering, grouping, and CRUD operations. Companies represent
business organizations that the CRM system manages relationships with.
"""

from flask import Blueprint, render_template, request
from app.models import Company, Stakeholder, Opportunity
from app.utils.routes import add_content_route

# Create blueprint and add DRY content route
companies_bp = Blueprint("companies", __name__)
add_content_route(companies_bp, Company)


@companies_bp.route("/")
def index():
    """
    Main companies index page displaying all companies with statistics.

    Provides a comprehensive view of all companies in the system including
    associated stakeholders and opportunities. Includes statistical overview
    and supports filtering, sorting, and grouping operations.

    Returns:
        Rendered HTML template with companies data, statistics, and UI controls.
    """
    
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
    

    # Simple context building - no over-engineered helpers
    context = {
        'entity_config': {
            'entity_name': 'Companies',
            'entity_name_singular': 'Company',
            'entity_description': 'Manage your companies',
            'entity_type': 'company',
            'entity_endpoint': 'companies',
            'entity_buttons': ['companies']
        },
        'entity_stats': entity_stats,
        'companies': companies,
        'companies_data': companies_data,
        'dropdown_configs': {
            'group_by': {
                'options': [
                    {'value': 'industry', 'label': 'Industry'},
                    {'value': 'name', 'label': 'Name'}
                ],
                'current_value': request.args.get('group_by', 'industry'),
                'placeholder': 'Group by...'
            },
            'sort_by': {
                'options': [
                    {'value': 'name', 'label': 'Name'},
                    {'value': 'industry', 'label': 'Industry'},
                    {'value': 'created_at', 'label': 'Created Date'}
                ],
                'current_value': request.args.get('sort_by', 'name'),
                'placeholder': 'Sort by...'
            }
        }
    }

    return render_template("base/entity_index.html", **context)




