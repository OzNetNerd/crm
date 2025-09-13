from datetime import date
from flask import Blueprint, render_template, request, jsonify
from app.models import Opportunity, Company, Stakeholder, Note, db
from app.utils.core.base_handlers import GenericAPIHandler, EntityFilterManager, EntityGrouper
from app.utils.core.model_introspection import ModelIntrospector
from app.utils.core.entity_handlers import OpportunityHandler, UniversalEntityManager
from collections import defaultdict

opportunities_bp = Blueprint("opportunities", __name__)
opportunity_handler = GenericAPIHandler(Opportunity, "opportunity")

# Create metadata-driven universal entity manager
opportunity_entity_manager = UniversalEntityManager(Opportunity, OpportunityHandler())
opportunity_filter_manager = EntityFilterManager(Opportunity, "opportunity")


# Use universal entity manager methods instead of duplicated functions
def opportunity_custom_filters(query, filters):
    """Opportunity-specific filtering using universal manager"""
    return opportunity_entity_manager.apply_custom_filters(query, filters)


def opportunity_custom_sorting(query, sort_by, sort_direction):
    """Opportunity-specific sorting using universal manager"""
    return opportunity_entity_manager.apply_custom_sorting(query, sort_by, sort_direction)


def opportunity_custom_groupers(entities, group_by):
    """Opportunity-specific grouping using universal manager"""
    return opportunity_entity_manager.apply_custom_grouping(entities, group_by)


@opportunities_bp.route("/")
def index():
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

    # Get all opportunities for stats
    opportunities = Opportunity.query.join(Company).all()
    today = date.today()

    # Generate opportunity stats
    total_value = sum(getattr(e, 'value', 0) or 0 for e in opportunities)
    entity_stats = {
        'title': 'Opportunities Overview',
        'stats': [
            {
                'value': len(opportunities),
                'label': 'Total Opportunities'
            },
            {
                'value': f"${total_value:,}",
                'label': 'Total Pipeline Value'
            },
            {
                'value': len([e for e in opportunities if getattr(e, 'stage', None) == 'closed-won']),
                'label': 'Closed Won'
            },
            {
                'value': len(set(getattr(e, 'company_id', None) for e in opportunities if getattr(e, 'company_id', None))),
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
    """Delete an opportunity"""
    try:
        # Verify opportunity exists
        opportunity = Opportunity.query.get_or_404(opportunity_id)

        # Delete related notes first (if notes exist)
        Note.query.filter_by(
            entity_type="opportunity", entity_id=opportunity_id
        ).delete()

        # Delete the opportunity
        db.session.delete(opportunity)
        db.session.commit()

        return jsonify(
            {"status": "success", "message": "Opportunity deleted successfully"}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@opportunities_bp.route("/<int:opportunity_id>/notes", methods=["GET"])
def get_opportunity_notes(opportunity_id):
    """Get all notes for a specific opportunity"""
    try:
        # Verify opportunity exists
        Opportunity.query.get_or_404(opportunity_id)

        notes = (
            Note.query.filter_by(entity_type="opportunity", entity_id=opportunity_id)
            .order_by(Note.created_at.desc())
            .all()
        )

        return jsonify(
            [
                {
                    "id": note.id,
                    "content": note.content,
                    "entity_type": note.entity_type,
                    "entity_id": note.entity_id,
                    "is_internal": note.is_internal,
                    "created_at": note.created_at.isoformat(),
                    "entity_name": note.entity_name,
                }
                for note in notes
            ]
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@opportunities_bp.route("/<int:opportunity_id>/notes", methods=["POST"])
def create_opportunity_note(opportunity_id):
    """Create a new note for a specific opportunity"""
    try:
        # Verify opportunity exists
        Opportunity.query.get_or_404(opportunity_id)

        data = request.get_json()
        if not data or not data.get("content"):
            return jsonify({"error": "Note content is required"}), 400

        note = Note(
            content=data["content"],
            entity_type="opportunity",
            entity_id=opportunity_id,
            is_internal=data.get("is_internal", True),
        )

        db.session.add(note)
        db.session.commit()

        return (
            jsonify(
                {
                    "id": note.id,
                    "content": note.content,
                    "entity_type": note.entity_type,
                    "entity_id": note.entity_id,
                    "is_internal": note.is_internal,
                    "created_at": note.created_at.isoformat(),
                    "entity_name": note.entity_name,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def get_filtered_opportunities_context():
    """Server-side filtering and sorting for opportunities HTMX endpoints - DRY version"""
    return opportunity_filter_manager.get_filtered_context(
        custom_filters=opportunity_custom_filters,
        custom_sorting=opportunity_custom_sorting,
        custom_grouper=opportunity_custom_groupers,
        joins=[Company]
    )




@opportunities_bp.route("/content")
def content():
    """HTMX endpoint for filtered opportunity content - DRY version"""
    context = opportunity_filter_manager.get_content_context(
        custom_filters=opportunity_custom_filters,
        custom_sorting=opportunity_custom_sorting,
        custom_grouper=opportunity_custom_groupers,
        joins=[Company]
    )
    
    return render_template("shared/entity_content.html", **context)


@opportunities_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        return opportunity_handler.create_entity(
            [
                "name",
                "value",
                "probability",
                "expected_close_date",
                "stage",
                "company_id",
            ]
        )

    # GET request - redirect to index (modal creation handled by HTMX)
    from flask import redirect, url_for
    return redirect(url_for('opportunities.index'))
