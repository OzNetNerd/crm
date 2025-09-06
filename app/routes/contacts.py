from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Contact, Company

contacts_bp = Blueprint("contacts", __name__)


@contacts_bp.route("/")
def index():
    contacts = Contact.query.join(Company).order_by(Company.name, Contact.name).all()
    return render_template("contacts/index.html", contacts=contacts)


@contacts_bp.route("/<int:contact_id>")
def detail(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    return render_template("contacts/detail.html", contact=contact)


@contacts_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form

        contact = Contact(
            name=data["name"],
            role=data.get("role"),
            email=data.get("email"),
            phone=data.get("phone"),
            company_id=data["company_id"],
        )

        db.session.add(contact)
        db.session.commit()

        if request.is_json:
            return jsonify({"status": "success", "contact_id": contact.id})
        else:
            return redirect(url_for("contacts.detail", contact_id=contact.id))

    companies = Company.query.order_by(Company.name).all()
    return render_template("contacts/new.html", companies=companies)
