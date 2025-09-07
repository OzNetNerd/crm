from datetime import date
from flask import Blueprint, render_template, request, jsonify
from crm.models import Opportunity, Company, Note
from crm.utils.route_helpers import BaseRouteHandler, parse_date_field, parse_int_field, get_entity_data_for_forms

opportunities_bp = Blueprint("opportunities", __name__)
opportunity_handler = BaseRouteHandler(Opportunity, "opportunities")


@opportunities_bp.route("/")
def index():
    opportunities = (
        Opportunity.query.join(Company)
        .order_by(Opportunity.expected_close_date.asc())
        .all()
    )
    today = date.today()
    return render_template(
        "opportunities/index.html", opportunities=opportunities, today=today
    )


@opportunities_bp.route("/<int:opportunity_id>")
def detail(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    return render_template("opportunities/detail.html", opportunity=opportunity)


@opportunities_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        def parse_company_id(data):
            company_id = parse_int_field(data, "company_id")
            if company_id is None:
                return jsonify({"error": "Invalid company ID"}), 400
            return company_id
        
        return opportunity_handler.handle_create(
            name="name",
            company_id=parse_company_id,
            value=lambda data: parse_int_field(data, "value"),
            probability=lambda data: parse_int_field(data, "probability", 0),
            expected_close_date=lambda data: parse_date_field(data, "expected_close_date"),
            stage=lambda data: data.get("stage", "prospect")
        )

    entity_data = get_entity_data_for_forms()
    return render_template("opportunities/new.html", companies=entity_data['companies'])


@opportunities_bp.route("/<int:opportunity_id>", methods=["DELETE"])
def delete_opportunity(opportunity_id):
    """Delete an opportunity"""
    try:
        # Verify opportunity exists
        opportunity = Opportunity.query.get_or_404(opportunity_id)

        # Delete related notes first (if notes exist)
        Note.query.filter_by(entity_type="opportunity", entity_id=opportunity_id).delete()

        # Delete the opportunity
        db.session.delete(opportunity)
        db.session.commit()

        return jsonify({"status": "success", "message": "Opportunity deleted successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@opportunities_bp.route("/<int:opportunity_id>/notes", methods=["GET"])
def get_opportunity_notes(opportunity_id):
    """Get all notes for a specific opportunity"""
    try:
        # Verify opportunity exists
        opportunity = Opportunity.query.get_or_404(opportunity_id)

        notes = (
            Note.query.filter_by(entity_type="opportunity", entity_id=opportunity_id)
            .order_by(Note.created_at.desc())
            .all()
        )

        return jsonify([{
            "id": note.id,
            "content": note.content,
            "entity_type": note.entity_type,
            "entity_id": note.entity_id,
            "is_internal": note.is_internal,
            "created_at": note.created_at.isoformat(),
            "entity_name": note.entity_name,
        } for note in notes])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@opportunities_bp.route("/<int:opportunity_id>/notes", methods=["POST"])
def create_opportunity_note(opportunity_id):
    """Create a new note for a specific opportunity"""
    try:
        # Verify opportunity exists
        opportunity = Opportunity.query.get_or_404(opportunity_id)

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
            jsonify({
                "id": note.id,
                "content": note.content,
                "entity_type": note.entity_type,
                "entity_id": note.entity_id,
                "is_internal": note.is_internal,
                "created_at": note.created_at.isoformat(),
                "entity_name": note.entity_name,
            }),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
