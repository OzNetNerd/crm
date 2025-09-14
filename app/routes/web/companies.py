"""
Company web routes for the CRM application.

This module provides web endpoints for managing companies including
listing, filtering, grouping, and CRUD operations. Companies represent
business organizations that the CRM system manages relationships with.
"""

from flask import Blueprint, render_template, request
from app.models import Company, Stakeholder, Opportunity
from app.utils.routes import add_content_route
from app.utils.route_helpers.helpers import build_dropdown_configs, calculate_entity_stats, build_entity_buttons

# Create blueprint and add DRY content route
companies_bp = Blueprint("companies", __name__)
add_content_route(companies_bp, Company)


@companies_bp.route("/")
def index():
    """
    Main companies index page displaying all companies with statistics.
    """
    # Get company data for templates that need it
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

    return render_template("base/entity_index.html",
        entity_config={
            **Company.get_entity_config(),
            'entity_buttons': build_entity_buttons(Company)
        },
        dropdown_configs=build_dropdown_configs(Company),
        entity_stats=calculate_entity_stats(Company),
        companies=companies,
        companies_data=companies_data
    )




