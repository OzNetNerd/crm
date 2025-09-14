from datetime import date
from flask import Blueprint, render_template, request, jsonify
from app.models import Opportunity, Company, Stakeholder, Note, db
from app.utils.routes import add_content_route
from app.utils.route_helpers.helpers import build_dropdown_configs, calculate_entity_stats, build_entity_buttons
from app.utils.ui.formatters import DisplayFormatter

# Create blueprint and add DRY content route
opportunities_bp = Blueprint("opportunities", __name__)
add_content_route(opportunities_bp, Opportunity)


@opportunities_bp.route("/")
def index():
    """
    Opportunities index page with pipeline overview.
    """
    # Use DRY helpers instead of duplicated static strings
    entity_config = Opportunity.__entity_config__.copy()
    entity_config['entity_buttons'] = build_entity_buttons(Opportunity)

    # Map model field names to template expected names for compatibility
    entity_config['entity_endpoint'] = entity_config['endpoint_name']
    entity_config['entity_name'] = entity_config['display_name']
    entity_config['entity_name_singular'] = entity_config['display_name_singular']

    return render_template("base/entity_index.html",
        entity_config=entity_config,
        dropdown_configs=build_dropdown_configs(Opportunity),
        entity_stats=calculate_entity_stats(Opportunity)
    )


@opportunities_bp.route("/<int:opportunity_id>", methods=["DELETE"])
def delete_opportunity(opportunity_id):
    """Delete an opportunity and related notes."""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)

        # Delete related notes first
        Note.query.filter_by(
            entity_type="opportunity", entity_id=opportunity_id
        ).delete()

        # Delete the opportunity
        db.session.delete(opportunity)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Opportunity deleted successfully"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500