from flask import Blueprint, request, jsonify
from app.models import db, Task, Stakeholder, Company, Opportunity
from app.utils.core.base_handlers import GenericAPIHandler

api_entities_bp = Blueprint("api_entities", __name__, url_prefix="/api")

# Initialize handlers for each entity
company_handler = GenericAPIHandler(Company, "company")
stakeholder_handler = GenericAPIHandler(Stakeholder, "stakeholder")
opportunity_handler = GenericAPIHandler(Opportunity, "opportunity")

# Company endpoints
@api_entities_bp.route("/companies/<int:company_id>")
def get_company_details(company_id):
    """Get company details with notes"""
    return company_handler.get_details(company_id)

@api_entities_bp.route("/companies")
def get_companies():
    """Get all companies for form dropdowns"""
    def list_serializer(company):
        return {
            'id': company.id,
            'name': company.name,
            'industry': company.industry
        }
    return company_handler.get_list(field_serializer=list_serializer, order_by_field="name")

@api_entities_bp.route("/companies/<int:company_id>", methods=["PUT"])
def update_company(company_id):
    """Update company details"""
    update_fields = ['name', 'industry', 'website', 'employee_count', 'notes', 'phone', 'email']
    return company_handler.update_entity(company_id, update_fields)

@api_entities_bp.route("/companies", methods=["POST"])
def create_company():
    """Create new company"""
    create_fields = ['name', 'industry', 'website', 'employee_count']
    return company_handler.create_entity(create_fields)

@api_entities_bp.route("/companies/<int:company_id>", methods=["DELETE"])
def delete_company(company_id):
    """Delete company"""
    return company_handler.delete_entity(company_id)

# Stakeholder endpoints
@api_entities_bp.route("/stakeholders/<int:stakeholder_id>")
def get_stakeholder_details(stakeholder_id):
    """Get stakeholder details with notes"""
    return stakeholder_handler.get_details(stakeholder_id)

@api_entities_bp.route("/stakeholders")
def get_stakeholders():
    """Get all stakeholders for form dropdowns"""
    def list_serializer(stakeholder):
        return {
            'id': stakeholder.id,
            'name': stakeholder.name,
            'job_title': stakeholder.job_title,
            'company_name': getattr(stakeholder, 'company_name', None),
            'meddpicc_roles': getattr(stakeholder, 'meddpicc_roles', [])
        }
    return stakeholder_handler.get_list(field_serializer=list_serializer, order_by_field="name")

@api_entities_bp.route("/stakeholders/<int:stakeholder_id>", methods=["PUT"])
def update_stakeholder(stakeholder_id):
    """Update stakeholder details"""
    update_fields = ['name', 'job_title', 'email', 'phone', 'company_id', 'meddpicc_roles', 'notes']
    return stakeholder_handler.update_entity(stakeholder_id, update_fields)

@api_entities_bp.route("/stakeholders", methods=["POST"])
def create_stakeholder():
    """Create new stakeholder"""
    create_fields = ['name', 'job_title', 'email', 'company_id']
    return stakeholder_handler.create_entity(create_fields)

@api_entities_bp.route("/stakeholders/<int:stakeholder_id>", methods=["DELETE"])
def delete_stakeholder(stakeholder_id):
    """Delete stakeholder"""
    return stakeholder_handler.delete_entity(stakeholder_id)

# Opportunity endpoints
@api_entities_bp.route("/opportunities/<int:opportunity_id>")
def get_opportunity_details(opportunity_id):
    """Get opportunity details with notes"""
    return opportunity_handler.get_details(opportunity_id)

@api_entities_bp.route("/opportunities")
def get_opportunities():
    """Get all opportunities for form dropdowns"""
    def list_serializer(opportunity):
        return {
            'id': opportunity.id,
            'name': getattr(opportunity, 'name', opportunity.description),
            'stage': opportunity.stage,
            'company_name': getattr(opportunity, 'company_name', None)
        }
    return opportunity_handler.get_list(field_serializer=list_serializer, order_by_field="name")

@api_entities_bp.route("/opportunities/<int:opportunity_id>", methods=["PUT"])
def update_opportunity(opportunity_id):
    """Update opportunity details"""
    update_fields = ['description', 'value', 'stage', 'close_date', 'company_id', 'notes', 'priority']
    return opportunity_handler.update_entity(opportunity_id, update_fields)

@api_entities_bp.route("/opportunities", methods=["POST"])
def create_opportunity():
    """Create new opportunity"""
    create_fields = ['description', 'value', 'stage', 'close_date', 'company_id', 'priority']
    return opportunity_handler.create_entity(create_fields)

@api_entities_bp.route("/opportunities/<int:opportunity_id>", methods=["DELETE"])
def delete_opportunity(opportunity_id):
    """Delete opportunity"""
    return opportunity_handler.delete_entity(opportunity_id)


# POST endpoints for entity creation
@api_entities_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create new task with support for linked entities"""
    try:
        data = request.get_json()

        # Handle task creation for single tasks
        if data.get("task_type") == "single" or not data.get("task_type"):
            # Create single task
            task_data = {}
            allowed_fields = [
                "description",
                "due_date",
                "priority",
                "status",
                "next_step_type",
                "task_type",
            ]

            for field in allowed_fields:
                if field in data:
                    if field == "due_date" and data[field]:
                        from datetime import datetime

                        task_data[field] = datetime.strptime(
                            data[field], "%Y-%m-%d"
                        ).date()
                    else:
                        task_data[field] = data[field]

            # Set defaults
            task_data.setdefault("task_type", "single")
            task_data.setdefault("priority", "medium")
            task_data.setdefault("status", "todo")

            task = Task(**task_data)
            db.session.add(task)
            db.session.flush()  # Get task ID

            # Handle linked entities if provided
            linked_entities = data.get("linked_entities", [])
            if isinstance(linked_entities, str):
                import json

                linked_entities = json.loads(linked_entities)

            if linked_entities:
                task.set_linked_entities(linked_entities)

            db.session.commit()
            return jsonify(task.to_dict()), 201

        # Handle multi-task creation (parent with children)
        elif data.get("task_type") == "multi":
            from datetime import datetime

            # Create parent task
            parent_task = Task(
                description=data["description"],
                due_date=(
                    datetime.strptime(data["due_date"], "%Y-%m-%d").date()
                    if data.get("due_date")
                    else None
                ),
                priority=data.get("priority", "medium"),
                status="todo",
                task_type="parent",
                dependency_type=data.get("dependency_type", "parallel"),
            )

            db.session.add(parent_task)
            db.session.flush()

            # Handle linked entities for parent task
            linked_entities = data.get("linked_entities", [])
            if isinstance(linked_entities, str):
                import json

                linked_entities = json.loads(linked_entities)

            if linked_entities:
                parent_task.set_linked_entities(linked_entities)

            # Create child tasks
            child_tasks_data = data.get("child_tasks", [])
            for i, child_data in enumerate(child_tasks_data):
                if child_data.get("description"):
                    child_task = Task(
                        description=child_data["description"],
                        due_date=(
                            datetime.strptime(child_data["due_date"], "%Y-%m-%d").date()
                            if child_data.get("due_date")
                            else None
                        ),
                        priority=child_data.get("priority", "medium"),
                        status="todo",
                        next_step_type=child_data.get("next_step_type"),
                        entity_type=data.get("entity_type"),
                        entity_id=data.get("entity_id"),
                        task_type="child",
                        parent_task_id=parent_task.id,
                        sequence_order=i,
                        dependency_type=data.get("dependency_type", "parallel"),
                    )
                    db.session.add(child_task)

                    # Child tasks inherit parent's linked entities
                    if linked_entities:
                        db.session.flush()  # Ensure child task has ID
                        child_task.set_linked_entities(linked_entities)

            db.session.commit()
            return jsonify(parent_task.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# Validation endpoint for inline duplicate checking
@api_entities_bp.route("/validate/<entity_type>/<field_name>", methods=["POST"])
def validate_field(entity_type, field_name):
    """
    Validate a single field for duplicate values without creating the entity.
    Used for inline validation in forms.
    """
    try:
        data = request.get_json()
        field_value = data.get('value', '').strip()

        # Skip validation for empty values
        if not field_value:
            return '', 200

        # Map entity types to model classes
        entity_map = {
            'company': Company,
            'stakeholder': Stakeholder,
            'opportunity': Opportunity
        }

        model_class = entity_map.get(entity_type.lower())
        if not model_class:
            return '', 200  # Unknown entity, allow

        # Check for duplicates based on field
        unique_fields = {
            'Company': {'name': 'name'},
            'Stakeholder': {'email': 'email'},
            'Opportunity': {}  # No unique fields for opportunities
        }

        model_name = model_class.__name__
        allowed_fields = unique_fields.get(model_name, {})

        # Only validate if this field should be unique
        if field_name not in allowed_fields:
            return '', 200

        # Check if value already exists (case-insensitive)
        existing = model_class.query.filter(
            getattr(model_class, field_name).ilike(field_value)
        ).first()

        if existing:
            field_label = field_name.replace('_', ' ').title()
            # Return HTML for the validation message
            error_html = f'<p class="mt-1 text-sm text-red-600">A {entity_type} with this {field_label.lower()} already exists.</p>'
            return error_html, 200

        # Return empty string for valid input
        return '', 200

    except Exception as e:
        # On error, don't block the user
        return '', 200


