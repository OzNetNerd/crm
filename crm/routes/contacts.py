from flask import Blueprint, render_template
from crm.models import Contact, Company
from crm.utils.route_helpers import BaseRouteHandler, get_entity_data_for_forms

contacts_bp = Blueprint("contacts", __name__)
contact_handler = BaseRouteHandler(Contact, "contacts")


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
        return contact_handler.handle_create(
            name="name",
            role="role", 
            email="email",
            phone="phone",
            company_id="company_id"
        )

    entity_data = get_entity_data_for_forms()
    return render_template("contacts/new.html", companies=entity_data['companies'])
