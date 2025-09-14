from datetime import date
from flask import Blueprint, render_template, request
from app.models import Stakeholder, Company, Opportunity
from app.utils.routes import add_content_route
from collections import defaultdict

# Create blueprint and add DRY content route
stakeholders_bp = Blueprint("stakeholders", __name__)
add_content_route(stakeholders_bp, Stakeholder)


@stakeholders_bp.route("/")
def index():
    # Removed over-engineered helper
    
    # Get all stakeholders for stats
    stakeholders = Stakeholder.query.join(Company).all()

    # Generate stakeholder stats directly
    entity_stats = {
        'title': 'Stakeholders Overview', 
        'stats': [
            {
                'value': len(stakeholders),
                'label': 'Total Stakeholders'
            },
            {
                'value': len([s for s in stakeholders if s.phone]),
                'label': 'With Phone'
            },
            {
                'value': len([s for s in stakeholders if s.email]),
                'label': 'With Email'
            },
            {
                'value': len(set([s.company_id for s in stakeholders if s.company_id])),
                'label': 'Companies Represented'
            }
        ]
    }
    
    # Simple context with basic dropdown configs
    context = {
        "entity_config": {"entity_name": "Stakeholders", "entity_type": "stakeholder", "entity_endpoint": "stakeholders", "entity_buttons": ["stakeholders"]},
        "dropdown_configs": {"group_by": {"options": [{"value": "job_title", "label": "Job Title"}], "current_value": "job_title"}, "sort_by": {"options": [{"value": "name", "label": "Name"}], "current_value": "name"}},
        "entity_stats": entity_stats or {}
    }
    
    # Add custom filters for stakeholders (job titles and companies)
    # Get unique job titles for secondary filter
    job_title_options = []
    job_titles = Stakeholder.query.with_entities(Stakeholder.job_title).distinct().filter(Stakeholder.job_title.isnot(None)).all()
    for job_title_tuple in job_titles:
        job_title = job_title_tuple[0]
        if job_title:
            job_title_options.append({'value': job_title, 'label': job_title})

    # Get unique company names for tertiary filter  
    company_options = []
    companies = Company.query.with_entities(Company.name).distinct().all()
    for company_tuple in companies:
        company = company_tuple[0]
        if company:
            company_options.append({'value': company, 'label': company})
    
    # Add additional filters to context
    context['dropdown_configs']['secondary_filter'] = {
        'button_text': 'All Job Titles',
        'options': job_title_options,
        'current_values': context['primary_filter'] or [],
        'name': 'secondary_filter'
    }
    context['dropdown_configs']['tertiary_filter'] = {
        'button_text': 'All Companies',
        'options': company_options,
        'current_values': context['secondary_filter'] or [],
        'name': 'tertiary_filter'
    }

    return render_template("base/entity_index.html", **context)


def get_filtered_stakeholders_context():
    """Server-side filtering and sorting for stakeholders HTMX endpoints - DRY version"""
    return stakeholder_filter_manager.get_filtered_context(
        custom_filters=stakeholder_custom_filters,
        custom_sorting=stakeholder_custom_sorting,
        custom_grouper=stakeholder_custom_groupers,
        joins=[Company]
    )




# Content route now provided by DRY factory


@stakeholders_bp.route("/modals/create", methods=['GET'])
def create_modal():
    """HTMX endpoint to show stakeholder creation modal"""
    from app.templates.macros.modals.stakeholder.stakeholder_new import generic_new_modal
    from app.templates.macros.modals.configs import stakeholder_new_config
    
    return generic_new_modal('stakeholder', stakeholder_new_config)


@stakeholders_bp.route("/modals/<int:stakeholder_id>/edit", methods=['GET'])  
def edit_modal(stakeholder_id):
    """HTMX endpoint to show stakeholder edit modal"""
    stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
    from app.templates.macros.modals.stakeholder.stakeholder_detail import generic_detail_modal
    from app.templates.macros.modals.configs import stakeholder_detail_config
    
    return generic_detail_modal('stakeholder', stakeholder, stakeholder_detail_config)


