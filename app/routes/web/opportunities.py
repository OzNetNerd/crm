from datetime import date
from flask import Blueprint, render_template, request, jsonify
from app.models import Opportunity, Company, Stakeholder, Note, db
from app.utils.route_helpers import GenericAPIHandler
from app.utils.model_introspection import ModelIntrospector
from collections import defaultdict

opportunities_bp = Blueprint("opportunities", __name__)
opportunity_handler = GenericAPIHandler(Opportunity, "opportunity")


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

    # Ultra-DRY one-line dropdown generation using pure model introspection
    from app.utils.form_configs import DropdownConfigGenerator
    dropdown_configs = DropdownConfigGenerator.generate_entity_dropdown_configs('opportunities', group_by, sort_by, sort_direction, primary_filter)

    # Entity stats for summary cards
    total_value = sum(o.value or 0 for o in opportunities)
    entity_stats = {
        'title': 'Pipeline Summary',
        'stats': [
            {
                'value': f"${total_value:,}",
                'label': 'Total Pipeline Value',
                'color_class': 'text-green-600'
            },
            {
                'value': len(opportunities),
                'label': 'Total Opportunities',
                'color_class': 'text-blue-600'
            },
            {
                'value': len([o for o in opportunities if o.stage == 'closed-won']),
                'label': 'Closed Won',
                'color_class': 'text-emerald-600'
            },
            {
                'value': len(set(o.company.name for o in opportunities if o.company)),
                'label': 'Companies in Pipeline',
                'color_class': 'text-purple-600'
            }
        ]
    }
    
    # Entity buttons for header actions
    entity_buttons = [
        {
            'text': 'New Opportunity',
            'onclick': 'openNewOpportunityModal()',
            'icon': 'plus',
            'classes': 'btn-primary'
        }
    ]

    return render_template(
        "opportunities/index.html",
        entity_name="Opportunities",
        entity_description="Manage your sales opportunities",
        entity_type="opportunity", 
        entity_endpoint="opportunities",
        entity_stats=entity_stats,
        entity_buttons=entity_buttons,
        dropdown_configs=dropdown_configs,
        opportunities=opportunities,
    )


@opportunities_bp.route("/<int:opportunity_id>")
def show(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    return render_template("opportunities/detail.html", opportunity=opportunity)




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
    """Server-side filtering and sorting for opportunities HTMX endpoints"""
    # Get filter parameters
    group_by = request.args.get("group_by", "stage")
    sort_by = request.args.get("sort_by", "value")
    sort_direction = request.args.get("sort_direction", "desc")
    
    # Parse filter arrays
    primary_filter = []
    if request.args.get("primary_filter"):
        primary_filter = [p.strip() for p in request.args.get("primary_filter").split(",") if p.strip()]
    
    secondary_filter = []
    if request.args.get("secondary_filter"):
        secondary_filter = [p.strip() for p in request.args.get("secondary_filter").split(",") if p.strip()]

    # Start with base query
    query = Opportunity.query.join(Company)
    
    # Apply filters
    if primary_filter:
        query = query.filter(Opportunity.stage.in_(primary_filter))
    
    if secondary_filter:
        query = query.filter(Company.name.in_(secondary_filter))
    
    # Apply sorting
    if sort_by == "name":
        if sort_direction == "desc":
            query = query.order_by(Opportunity.name.desc())
        else:
            query = query.order_by(Opportunity.name.asc())
    elif sort_by == "value":
        if sort_direction == "desc":
            query = query.order_by(Opportunity.value.desc().nulls_last())
        else:
            query = query.order_by(Opportunity.value.asc().nulls_last())
    elif sort_by == "stage":
        if sort_direction == "desc":
            query = query.order_by(Opportunity.stage.desc())
        else:
            query = query.order_by(Opportunity.stage.asc())
    elif sort_by == "expected_close_date":
        if sort_direction == "desc":
            query = query.order_by(Opportunity.expected_close_date.desc().nulls_last())
        else:
            query = query.order_by(Opportunity.expected_close_date.asc().nulls_last())
    else:
        # Default sort by value
        query = query.order_by(Opportunity.value.desc().nulls_last())
    
    filtered_opportunities = query.all()
    
    # Group opportunities by the specified grouping
    grouped_opportunities = group_opportunities_by_field(filtered_opportunities, group_by)
    
    return {
        "grouped_opportunities": grouped_opportunities,
        "group_by": group_by,
        "total_count": len(filtered_opportunities),
        "sort_by": sort_by,
        "sort_direction": sort_direction,
        "primary_filter": primary_filter,
        "secondary_filter": secondary_filter,
        "today": date.today(),
    }


def group_opportunities_by_field(opportunities, group_by):
    """Group opportunities by specified field"""
    grouped = defaultdict(list)
    
    if group_by == "stage":
        for opportunity in opportunities:
            stage = opportunity.stage or "Other"
            grouped[stage].append(opportunity)
        
        # Return in stage order
        stage_order = ["prospect", "qualified", "proposal", "negotiation", "closed-won", "closed-lost", "Other"]
        result = []
        for stage in stage_order:
            if stage in grouped and grouped[stage]:
                result.append({
                    "key": stage,
                    "label": stage.replace("-", " ").title(),
                    "entities": grouped[stage],
                    "count": len(grouped[stage])
                })
        return result
        
    elif group_by == "company":
        for opportunity in opportunities:
            company_name = opportunity.company.name if opportunity.company else "No Company"
            grouped[company_name].append(opportunity)
        
        # Return sorted by company name
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
    
    else:
        # Default: no grouping, return all in one group
        return [{
            "key": "all",
            "label": "All Opportunities",
            "entities": opportunities,
            "count": len(opportunities)
        }]


@opportunities_bp.route("/content")
def content():
    """HTMX endpoint for filtered opportunity content"""
    context = get_filtered_opportunities_context()
    
    # Universal template configuration using model introspection
    context.update({
        'grouped_entities': context["grouped_opportunities"],
        'entity_type': 'opportunity',
        'entity_name_singular': 'opportunity',
        'entity_name_plural': 'opportunities',
        'card_config': ModelIntrospector.get_card_config(Opportunity),
        'model_class': Opportunity
    })
    
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

    # GET request - render template (if needed)
    companies = Company.query.all()
    return render_template("opportunities/new.html", companies=companies)
