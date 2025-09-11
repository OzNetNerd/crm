from datetime import date
from flask import Blueprint, render_template, request
from app.models import Stakeholder, Company, Opportunity
from app.utils.route_helpers import BaseRouteHandler, EntityFilterManager, EntityGrouper
from app.utils.model_introspection import ModelIntrospector
from collections import defaultdict

stakeholders_bp = Blueprint("stakeholders", __name__)
stakeholder_handler = BaseRouteHandler(Stakeholder, "stakeholders")
stakeholder_filter_manager = EntityFilterManager(Stakeholder, "stakeholder")


def stakeholder_custom_filters(query, filters):
    """Stakeholder-specific filtering logic"""
    if filters['primary_filter']:
        query = query.filter(Stakeholder.job_title.in_(filters['primary_filter']))
    
    if filters['secondary_filter']:
        query = query.filter(Company.name.in_(filters['secondary_filter']))
    
    return query


def stakeholder_custom_sorting(query, sort_by, sort_direction):
    """Stakeholder-specific sorting logic"""
    if sort_by == "name":
        if sort_direction == "desc":
            return query.order_by(Stakeholder.name.desc())
        else:
            return query.order_by(Stakeholder.name.asc())
    elif sort_by == "company":
        if sort_direction == "desc":
            return query.order_by(Company.name.desc(), Stakeholder.name.asc())
        else:
            return query.order_by(Company.name.asc(), Stakeholder.name.asc())
    else:
        # Default sort by name
        return query.order_by(Stakeholder.name.asc())


def stakeholder_custom_groupers(entities, group_by):
    """Stakeholder-specific grouping logic"""
    grouped = defaultdict(list)
    
    if group_by == "company":
        for stakeholder in entities:
            company_name = stakeholder.company.name if stakeholder.company else "No Company"
            grouped[company_name].append(stakeholder)
        
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
        for stakeholder in entities:
            job_title = stakeholder.job_title or "Other"
            grouped[job_title].append(stakeholder)
        
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
    
    return None  # Use default grouping


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

    # Ultra-DRY dropdown generation using pure model introspection
    from app.utils.form_configs import DropdownConfigGenerator
    dropdown_configs = DropdownConfigGenerator.generate_entity_dropdown_configs('stakeholders', group_by, sort_by, sort_direction, primary_filter)
    
    # Since stakeholders have dynamic job titles and companies, add them as additional filters
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
    
    # Add additional filters to DRY config
    dropdown_configs['secondary_filter'] = {
        'button_text': 'All Job Titles',
        'options': job_title_options,
        'current_values': primary_filter or [],
        'name': 'secondary_filter' 
    }
    dropdown_configs['tertiary_filter'] = {
        'button_text': 'All Companies',
        'options': company_options,
        'current_values': secondary_filter or [],
        'name': 'tertiary_filter'
    }
    
    # Entity stats for summary cards
    entity_stats = {
        'title': 'Stakeholder Overview',
        'stats': [
            {
                'value': len(stakeholders),
                'label': 'Total Stakeholders',
                'color_class': 'text-blue-600'
            },
            {
                'value': len([s for s in stakeholders if s.phone]),
                'label': 'With Phone',
                'color_class': 'text-green-600'
            },
            {
                'value': len([s for s in stakeholders if s.email]),
                'label': 'With Email',
                'color_class': 'text-purple-600'
            },
            {
                'value': len(set([s.company_id for s in stakeholders if s.company_id])),
                'label': 'Companies Represented',
                'color_class': 'text-yellow-600'
            }
        ]
    }
    
    # Entity buttons for header
    entity_buttons = [
        {
            'label': 'New Stakeholder',
            'hx_get': '/modals/Stakeholder/create',
            'hx_target': 'body',
            'hx_swap': 'beforeend',
            'icon': '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>'
        }
    ]

    return render_template(
        "base/entity_index.html",
        entity_name="Stakeholders",
        entity_description="Manage your stakeholder relationships",
        entity_type="stakeholder",
        entity_endpoint="stakeholders",
        entity_stats=entity_stats,
        entity_buttons=entity_buttons,
        dropdown_configs=dropdown_configs,
        stakeholders=stakeholders,
    )


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


