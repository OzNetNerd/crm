"""
Company web routes for the CRM application.

This module provides web endpoints for managing companies including
listing, filtering, grouping, and CRUD operations. Companies represent
business organizations that the CRM system manages relationships with.
"""

from datetime import date
from typing import List, Dict, Any
from flask import Blueprint, render_template, request
from app.models import Company, Stakeholder, Opportunity, db
from app.utils.core.base_handlers import BaseRouteHandler, EntityFilterManager, EntityGrouper
from app.utils.core.model_introspection import ModelIntrospector
from app.utils.core.entity_handlers import CompanyHandler, UniversalEntityManager
from collections import defaultdict

companies_bp = Blueprint("companies", __name__)
company_handler = BaseRouteHandler(Company, "companies")

# Create metadata-driven universal entity manager
company_entity_manager = UniversalEntityManager(Company, CompanyHandler())
company_filter_manager = EntityFilterManager(Company, "company")


# Use universal entity manager methods instead of duplicated functions
def company_custom_filters(query, filters: Dict[str, Any]):
    """Company-specific filtering using universal manager"""
    return company_entity_manager.apply_custom_filters(query, filters)


def company_custom_groupers(entities: List[Company], group_by: str) -> List[Dict[str, Any]]:
    """Company-specific grouping using universal manager"""
    return company_entity_manager.apply_custom_grouping(entities, group_by)


def get_filtered_companies_context() -> Dict[str, Any]:
    """
    Get filtered and sorted companies context for HTMX endpoints.
    
    Provides server-side filtering and sorting functionality for companies
    with custom filtering and grouping logic applied.
    
    Returns:
        Dictionary containing filtered companies and related context data.
    """
    return company_filter_manager.get_filtered_context(
        custom_filters=company_custom_filters,
        custom_grouper=company_custom_groupers
    )


@companies_bp.route("/content")
def content():
    """
    HTMX endpoint for dynamically filtered company content.
    
    Returns partial HTML content for companies list with applied filters,
    sorting, and grouping. Used for dynamic updates without full page refresh.
    
    Returns:
        Rendered HTML template with filtered company data.
    """
    context = company_filter_manager.get_content_context(
        custom_filters=company_custom_filters,
        custom_grouper=company_custom_groupers
    )
    
    return render_template("shared/entity_content.html", **context)


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




