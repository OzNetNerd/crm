from datetime import date
from flask import Blueprint, render_template, request
from app.models import Stakeholder, Company, Opportunity
from app.utils.route_helpers import BaseRouteHandler, get_entity_data_for_forms

stakeholders_bp = Blueprint("stakeholders", __name__)
stakeholder_handler = BaseRouteHandler(Stakeholder, "stakeholders")


@stakeholders_bp.route("/")
def index():
    # Get filter parameters for initial state and URL persistence
    group_by = request.args.get('group_by', 'company')
    sort_by = request.args.get('sort_by', 'name')
    sort_direction = request.args.get('sort_direction', 'asc')
    show_completed = request.args.get('show_completed', 'false').lower() == 'true'
    primary_filter = request.args.get('primary_filter', '').split(',') if request.args.get('primary_filter') else []
    secondary_filter = request.args.get('secondary_filter', '').split(',') if request.args.get('secondary_filter') else []
    entity_filter = request.args.get('entity_filter', '').split(',') if request.args.get('entity_filter') else []
    
    # Get all contacts with relationships
    contacts = Stakeholder.query.join(Company).order_by(Company.name, Stakeholder.name).all()
    
    # Get all companies and opportunities for global data
    companies_objects = Company.query.all()
    opportunities_objects = Opportunity.query.all()
    
    # Convert to JSON-serializable format for JavaScript
    companies_data = [{
        'id': company.id,
        'name': company.name,
        'industry': company.industry,
        'website': company.website
    } for company in companies_objects]
    
    opportunities_data = [{
        'id': opp.id,
        'name': opp.name,
        'value': float(opp.value) if opp.value else 0,
        'company_id': opp.company_id
    } for opp in opportunities_objects]
    
    contacts_data = [{
        'id': contact.id,
        'name': contact.name,
        'email': contact.email,
        'phone': contact.phone,
        'role': contact.job_title,
        'company_id': contact.company_id,
        'company': {
            'id': contact.company.id,
            'name': contact.company.name,
            'industry': contact.company.industry
        } if contact.company else None
    } for contact in contacts]
    
    today = date.today()
    
    return render_template(
        "stakeholders/index.html", 
        contacts=contacts,
        companies=companies_data,
        opportunities=opportunities_data,
        contacts_data=contacts_data,
        today=today,
        # Filter states for URL persistence
        group_by=group_by,
        sort_by=sort_by,
        sort_direction=sort_direction,
        show_completed=show_completed,
        primary_filter=primary_filter,
        secondary_filter=secondary_filter,
        entity_filter=entity_filter
    )


@stakeholders_bp.route("/<int:contact_id>")
def detail(contact_id):
    contact = Stakeholder.query.get_or_404(contact_id)
    return render_template("stakeholders/detail.html", contact=contact)


@stakeholders_bp.route("/new", methods=["GET", "POST"])
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
    return render_template("stakeholders/new.html", companies=entity_data['companies'])
