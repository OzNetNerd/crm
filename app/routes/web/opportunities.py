"""
Opportunity web routes for the CRM application.
"""

from flask import Blueprint, jsonify
from app.models import Opportunity, Company, Note, db

# Create blueprint
opportunities_bp = Blueprint("opportunities", __name__)


@opportunities_bp.route("/")
def index():
    """Main opportunities index page."""
    return Opportunity.render_index()


@opportunities_bp.route("/content")
def content():
    """HTMX endpoint for filtered opportunity content."""
    return Opportunity.render_content(
        filter_fields=['company_id', 'stage', 'priority'],
        join_map={'company_name': [Company]}
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