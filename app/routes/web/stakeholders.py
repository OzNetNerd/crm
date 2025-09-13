from datetime import date
from flask import Blueprint, render_template, request
from app.models import Stakeholder, Company, Opportunity
from app.utils.core.base_handlers import BaseRouteHandler, EntityFilterManager, EntityGrouper
from app.utils.core.model_introspection import ModelIntrospector
from app.utils.core.entity_handlers import StakeholderHandler, UniversalEntityManager
from collections import defaultdict

stakeholders_bp = Blueprint("stakeholders", __name__)
stakeholder_handler = BaseRouteHandler(Stakeholder, "stakeholders")

# Create metadata-driven universal entity manager
stakeholder_entity_manager = UniversalEntityManager(Stakeholder, StakeholderHandler())
stakeholder_filter_manager = EntityFilterManager(Stakeholder, "stakeholder")


# Use universal entity manager methods instead of duplicated functions
def stakeholder_custom_filters(query, filters):
    """Stakeholder-specific filtering using universal manager"""
    return stakeholder_entity_manager.apply_custom_filters(query, filters)


def stakeholder_custom_sorting(query, sort_by, sort_direction):
    """Stakeholder-specific sorting using universal manager"""
    return stakeholder_entity_manager.apply_custom_sorting(query, sort_by, sort_direction)


def stakeholder_custom_groupers(entities, group_by):
    """Stakeholder-specific grouping using universal manager"""
    return stakeholder_entity_manager.apply_custom_grouping(entities, group_by)


@stakeholders_bp.route("/")
def index():
    from app.utils.ui.index_helpers import UniversalIndexHelper
    
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
    
    context = UniversalIndexHelper.get_standardized_index_context(
        entity_name='stakeholders',
        default_group_by='company',
        default_sort_by='name',
        additional_context={
            'entity_stats': entity_stats,
            'stakeholders': stakeholders,
        }
    )
    
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




@stakeholders_bp.route("/content")
def content():
    """HTMX endpoint for filtered stakeholder content - DRY version"""
    context = stakeholder_filter_manager.get_content_context(
        custom_filters=stakeholder_custom_filters,
        custom_sorting=stakeholder_custom_sorting,
        custom_grouper=stakeholder_custom_groupers,
        joins=[Company]
    )
    
    return render_template("shared/entity_content.html", **context)


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


