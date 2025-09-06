from datetime import date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Opportunity, Company, Note

opportunities_bp = Blueprint("opportunities", __name__)


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
        data = request.get_json() if request.is_json else request.form
        # Convert data types properly
        value = data.get("value")
        if value:
            try:
                value = int(value)
            except (ValueError, TypeError):
                value = None
        else:
            value = None

        probability = data.get("probability", 0)
        if isinstance(probability, str):
            try:
                probability = int(probability)
            except (ValueError, TypeError):
                probability = 0

        expected_close_date = data.get("expected_close_date")
        if not expected_close_date or expected_close_date == "":
            expected_close_date = None
        elif isinstance(expected_close_date, str):
            try:
                from datetime import datetime

                expected_close_date = datetime.strptime(
                    expected_close_date, "%Y-%m-%d"
                ).date()
            except (ValueError, TypeError):
                expected_close_date = None

        company_id = data.get("company_id")
        if isinstance(company_id, str):
            try:
                company_id = int(company_id)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid company ID"}), 400

        opportunity = Opportunity(
            name=data["name"],
            company_id=company_id,
            value=value,
            probability=probability,
            expected_close_date=expected_close_date,
            stage=data.get("stage", "prospect"),
        )

        db.session.add(opportunity)
        db.session.commit()

        if request.is_json:
            return jsonify({"status": "success", "opportunity_id": opportunity.id})
        else:
            return redirect(
                url_for("opportunities.detail", opportunity_id=opportunity.id)
            )

    companies = Company.query.order_by(Company.name).all()
    return render_template("opportunities/new.html", companies=companies)


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
