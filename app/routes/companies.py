from datetime import date
from flask import Blueprint, render_template, request
from app.models import Company, Stakeholder, Opportunity
from app.utils.route_helpers import BaseRouteHandler

companies_bp = Blueprint("companies", __name__)
company_handler = BaseRouteHandler(Company, "companies")


@companies_bp.route("/")
def index():
    # Get filter parameters for initial state and URL persistence
    group_by = request.args.get('group_by', 'industry')
    sort_by = request.args.get('sort_by', 'name')
    sort_direction = request.args.get('sort_direction', 'asc')
    show_completed = request.args.get('show_completed', 'false').lower() == 'true'
    primary_filter = request.args.get('primary_filter', '').split(',') if request.args.get('primary_filter') else []
    secondary_filter = request.args.get('secondary_filter', '').split(',') if request.args.get('secondary_filter') else []
    entity_filter = request.args.get('entity_filter', '').split(',') if request.args.get('entity_filter') else []
    
    # Get all companies with relationships
    companies = Company.query.all()
    
    # Get all contacts and opportunities for global data
    contacts_objects = Stakeholder.query.all()
    opportunities_objects = Opportunity.query.all()
    
    # Convert to JSON-serializable format for JavaScript
    contacts_data = [{
        'id': contact.id,
        'name': contact.name,
        'email': contact.email,
        'phone': contact.phone,
        'role': contact.job_title,
        'company_id': contact.company_id
    } for contact in contacts_objects]
    
    opportunities_data = [{
        'id': opp.id,
        'name': opp.name,
        'value': float(opp.value) if opp.value else 0,
        'company_id': opp.company_id
    } for opp in opportunities_objects]
    
    companies_data = [{
        'id': company.id,
        'name': company.name,
        'industry': company.industry,
        'website': company.website,
        'contacts': [c for c in contacts_data if c['company_id'] == company.id],
        'opportunities': [o for o in opportunities_data if o['company_id'] == company.id],
        'created_at': company.created_at.isoformat() if hasattr(company, 'created_at') and company.created_at else None
    } for company in companies]
    
    today = date.today()
    
    return render_template(
        "companies/index.html", 
        companies=companies,
        contacts=contacts_data,
        opportunities=opportunities_data,
        companies_data=companies_data,
        today=today,
        # Filter states for URL persistence
        group_by=group_by,
        sort_by=sort_by,
        sort_direction=sort_direction,
        show_completed=show_completed,
        primary_filter=','.join(primary_filter),
        secondary_filter=','.join(secondary_filter),
        entity_filter=','.join(entity_filter)
    )


@companies_bp.route("/<int:company_id>")
def detail(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template("companies/detail.html", company=company)


@companies_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        return company_handler.handle_create(
            name="name",
            industry="industry",
            website="website"
        )

    return render_template("companies/new.html")
