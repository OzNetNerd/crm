"""
Stakeholder web routes for the CRM application.
"""

from flask import Blueprint
from app.models import Stakeholder, Company

# Create blueprint
stakeholders_bp = Blueprint("stakeholders", __name__)


@stakeholders_bp.route("/")
def index():
    """Main stakeholders index page."""
    return Stakeholder.render_index()


@stakeholders_bp.route("/content")
def content():
    """HTMX endpoint for filtered stakeholder content."""
    return Stakeholder.render_content(
        filter_fields=['company_id', 'job_title'],
        join_map={'company_name': [Company]}
    )


@stakeholders_bp.route("/modals/create", methods=['GET'])
def create_modal():
    """HTMX endpoint to show stakeholder creation modal."""
    from app.templates.macros.modals.stakeholder.stakeholder_new import generic_new_modal
    from app.templates.macros.modals.configs import stakeholder_new_config

    return generic_new_modal('stakeholder', stakeholder_new_config)


@stakeholders_bp.route("/modals/<int:stakeholder_id>/edit", methods=['GET'])
def edit_modal(stakeholder_id):
    """HTMX endpoint to show stakeholder edit modal."""
    stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
    from app.templates.macros.modals.stakeholder.stakeholder_detail import generic_detail_modal
    from app.templates.macros.modals.configs import stakeholder_detail_config

    return generic_detail_modal('stakeholder', stakeholder, stakeholder_detail_config)