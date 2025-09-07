from flask import Blueprint, request, jsonify
from app.models import db, Task, Contact, Company, Opportunity, Note
from app.utils.route_helpers import GenericAPIHandler

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Create generic API handlers
task_api = GenericAPIHandler(Task, "task")
contact_api = GenericAPIHandler(Contact, "contact")  
company_api = GenericAPIHandler(Company, "company")
opportunity_api = GenericAPIHandler(Opportunity, "opportunity")


@api_bp.route("/tasks/<int:task_id>")
def get_task_details(task_id):
    """Get task details with notes"""
    return task_api.get_details(task_id)


@api_bp.route("/contacts/<int:contact_id>")
def get_contact_details(contact_id):
    """Get contact details with notes"""
    return contact_api.get_details(contact_id)


@api_bp.route("/companies")
def get_companies():
    """Get all companies for form dropdowns"""
    try:
        companies = Company.query.order_by(Company.name).all()
        return jsonify([{
            'id': company.id,
            'name': company.name,
            'industry': company.industry
        } for company in companies])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route("/companies/<int:company_id>")
def get_company_details(company_id):
    """Get company details with notes"""
    return company_api.get_details(company_id)


@api_bp.route("/opportunities/<int:opportunity_id>")
def get_opportunity_details(opportunity_id):
    """Get opportunity details with notes"""
    return opportunity_api.get_details(opportunity_id)


@api_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update task details"""
    return task_api.update_entity(task_id, ["description", "due_date", "priority", "status", "next_step_type"])


@api_bp.route("/contacts/<int:contact_id>", methods=["PUT"])
def update_contact(contact_id):
    """Update contact details"""
    return contact_api.update_entity(contact_id, ["name", "role", "email", "phone"])


@api_bp.route("/companies/<int:company_id>", methods=["PUT"])
def update_company(company_id):
    """Update company details"""
    return company_api.update_entity(company_id, ["name", "industry", "website"])


@api_bp.route("/opportunities/<int:opportunity_id>", methods=["PUT"])
def update_opportunity(opportunity_id):
    """Update opportunity details"""
    return opportunity_api.update_entity(opportunity_id, ["name", "value", "probability", "expected_close_date", "stage"])
