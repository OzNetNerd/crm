from datetime import date
from flask import Blueprint, render_template, request, jsonify
from app.models import Opportunity, Company, Stakeholder, Note, db
from app.utils.routes import add_content_route
from app.utils.ui.formatters import DisplayFormatter

# Create blueprint and add DRY content route
opportunities_bp = Blueprint("opportunities", __name__)
add_content_route(opportunities_bp, Opportunity)


@opportunities_bp.route("/")
def index():
    """
    Opportunities index page with pipeline overview.

    Uses model methods for cleaner aggregation logic.
    """
    # Get filter parameters for initial state and URL persistence
    group_by = request.args.get("group_by", "stage")
    sort_by = request.args.get("sort_by", "value")
    sort_direction = request.args.get("sort_direction", "desc")
    show_completed = request.args.get("show_completed", "false").lower() == "true"
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

    # Get all opportunities for display
    opportunities = Opportunity.query.join(Company).all()

    # Use model method for total value calculation
    total_value = Opportunity.calculate_pipeline_value()

    # Generate opportunity stats
    entity_stats = {
        'title': 'Opportunities Overview',
        'stats': [
            {
                'value': len(opportunities),
                'label': 'Total Opportunities'
            },
            {
                'value': DisplayFormatter.format_currency(total_value),
                'label': 'Total Pipeline Value'
            },
            {
                'value': len([e for e in opportunities if e.stage == 'closed-won']),
                'label': 'Closed Won'
            },
            {
                'value': len(set(e.company_id for e in opportunities if e.company_id)),
                'label': 'Companies in Pipeline'
            }
        ]
    }

    # Get standardized context using universal helper
    from app.utils.ui.index_helpers import UniversalIndexHelper
    context = UniversalIndexHelper.get_standardized_index_context(
        entity_name='opportunities',
        default_group_by='stage',
        default_sort_by='name',
        additional_context={
            'entity_stats': entity_stats,
            'opportunities': opportunities,
        }
    )

    return render_template("base/entity_index.html", **context)


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