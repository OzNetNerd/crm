from datetime import date
from flask import Blueprint, render_template, request
from app.models import Stakeholder, Company, Opportunity
from app.utils.routes import add_content_route
from app.utils.route_helpers.helpers import build_dropdown_configs, calculate_entity_stats, build_entity_buttons
from collections import defaultdict

# Create blueprint and add DRY content route
stakeholders_bp = Blueprint("stakeholders", __name__)
add_content_route(stakeholders_bp, Stakeholder)


@stakeholders_bp.route("/")
def index():
    # Use DRY helpers instead of duplicated static strings
    entity_config = Stakeholder.__entity_config__.copy()
    entity_config['entity_buttons'] = build_entity_buttons(Stakeholder)

    # Map model field names to template expected names for compatibility
    entity_config['entity_endpoint'] = entity_config['endpoint_name']
    entity_config['entity_name'] = entity_config['display_name']
    entity_config['entity_name_singular'] = entity_config['display_name_singular']

    return render_template("base/entity_index.html",
        entity_config=entity_config,
        dropdown_configs=build_dropdown_configs(Stakeholder),
        entity_stats=calculate_entity_stats(Stakeholder)
    )


# Content route provided by DRY factory


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


