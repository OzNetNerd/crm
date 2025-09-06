from datetime import date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Opportunity, Company

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

        opportunity = Opportunity(
            name=data["name"],
            company_id=data["company_id"],
            value=data.get("value"),
            probability=data.get("probability", 0),
            expected_close_date=data.get("expected_close_date"),
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
