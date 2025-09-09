from flask import Blueprint, request, jsonify
from app.models import db, Task, Contact, Company, Opportunity, Note
from app.utils.route_helpers import GenericAPIHandler
from datetime import datetime

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


@api_bp.route("/contacts")
def get_contacts():
    """Get all contacts for form dropdowns"""
    try:
        contacts = Contact.query.order_by(Contact.name).all()
        return jsonify([{
            'id': contact.id,
            'name': contact.name,
            'role': contact.role,
            'company_name': contact.company.name if contact.company else None
        } for contact in contacts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route("/opportunities")
def get_opportunities():
    """Get all opportunities for form dropdowns"""
    try:
        opportunities = Opportunity.query.order_by(Opportunity.name).all()
        return jsonify([{
            'id': opportunity.id,
            'name': opportunity.name,
            'stage': opportunity.stage,
            'company_name': opportunity.company.name if opportunity.company else None
        } for opportunity in opportunities])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task with optional related entities"""
    try:
        data = request.get_json()
        
        # Create main task
        task = Task(
            description=data.get('description'),
            due_date=(
                datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                if data.get('due_date')
                else None
            ),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'todo'),
            next_step_type=data.get('next_step_type'),
            entity_type=data.get('entity_type'),
            entity_id=data.get('entity_id'),
            task_type=data.get('task_type', 'single'),
            parent_task_id=data.get('parent_task_id'),
            sequence_order=data.get('sequence_order', 0),
            dependency_type=data.get('dependency_type', 'parallel')
        )
        
        db.session.add(task)
        db.session.flush()  # Get the task ID
        
        # Add related entities
        if data.get('related_company_ids'):
            companies = Company.query.filter(Company.id.in_(data['related_company_ids'])).all()
            task.related_companies.extend(companies)
            
        if data.get('related_contact_ids'):
            contacts = Contact.query.filter(Contact.id.in_(data['related_contact_ids'])).all()
            task.related_contacts.extend(contacts)
            
        if data.get('related_opportunity_ids'):
            opportunities = Opportunity.query.filter(Opportunity.id.in_(data['related_opportunity_ids'])).all()
            task.related_opportunities.extend(opportunities)
        
        # Handle child tasks for multi-task creation
        if data.get('task_type') == 'multi' and data.get('child_tasks'):
            for i, child_data in enumerate(data['child_tasks']):
                if child_data.get('description'):
                    child_task = Task(
                        description=child_data['description'],
                        due_date=(
                            datetime.strptime(child_data['due_date'], '%Y-%m-%d').date()
                            if child_data.get('due_date')
                            else None
                        ),
                        priority=child_data.get('priority', 'medium'),
                        status='todo',
                        next_step_type=child_data.get('next_step_type'),
                        entity_type=data.get('entity_type'),
                        entity_id=data.get('entity_id'),
                        task_type='child',
                        parent_task_id=task.id,
                        sequence_order=i,
                        dependency_type=data.get('dependency_type', 'parallel')
                    )
                    db.session.add(child_task)
        
        db.session.commit()
        return jsonify({'status': 'success', 'task_id': task.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


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


# POST endpoints for entity creation
@api_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create new task"""
    return task_api.create_entity(["description", "due_date", "priority", "status", "next_step_type", "entity_type", "entity_id"])


@api_bp.route("/contacts", methods=["POST"])
def create_contact():
    """Create new contact"""
    return contact_api.create_entity(["name", "role", "email", "phone", "company_id"])


@api_bp.route("/companies", methods=["POST"])
def create_company():
    """Create new company"""
    return company_api.create_entity(["name", "industry", "size", "website", "phone", "address"])


@api_bp.route("/opportunities", methods=["POST"])
def create_opportunity():
    """Create new opportunity"""
    return opportunity_api.create_entity(["name", "value", "probability", "expected_close_date", "stage", "company_id", "contact_id"])


# DELETE endpoints for entity deletion
@api_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete task"""
    return task_api.delete_entity(task_id)


@api_bp.route("/contacts/<int:contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    """Delete contact"""
    return contact_api.delete_entity(contact_id)


@api_bp.route("/companies/<int:company_id>", methods=["DELETE"])
def delete_company(company_id):
    """Delete company"""
    return company_api.delete_entity(company_id)


@api_bp.route("/opportunities/<int:opportunity_id>", methods=["DELETE"])
def delete_opportunity(opportunity_id):
    """Delete opportunity"""
    return opportunity_api.delete_entity(opportunity_id)
