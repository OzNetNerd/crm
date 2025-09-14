from flask import Blueprint, request, jsonify, abort
from app.models import db, Task, Stakeholder, Company, Opportunity

api_entities_bp = Blueprint("api_entities", __name__, url_prefix="/api")

# Single source of truth - simple entity mapping
ENTITIES = {
    'companies': Company,
    'stakeholders': Stakeholder,
    'opportunities': Opportunity
}

# Generic CRUD functions - DRY approach
def get_entity_list(entity_name):
    """Get list of entities"""
    model = ENTITIES.get(entity_name)
    if not model:
        abort(404)

    entities = model.query.order_by(getattr(model, 'name', model.id)).all()
    return jsonify([entity.to_dict() for entity in entities])

def get_entity_detail(entity_name, entity_id):
    """Get single entity details"""
    model = ENTITIES.get(entity_name)
    if not model:
        abort(404)

    entity = model.query.get_or_404(entity_id)
    return jsonify(entity.to_dict())

def create_entity(entity_name):
    """Create new entity"""
    model = ENTITIES.get(entity_name)
    if not model:
        abort(404)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        entity = model(**data)
        db.session.add(entity)
        db.session.commit()
        return jsonify(entity.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def update_entity(entity_name, entity_id):
    """Update existing entity"""
    model = ENTITIES.get(entity_name)
    if not model:
        abort(404)

    entity = model.query.get_or_404(entity_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        db.session.commit()
        return jsonify(entity.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def delete_entity(entity_name, entity_id):
    """Delete entity"""
    model = ENTITIES.get(entity_name)
    if not model:
        abort(404)

    entity = model.query.get_or_404(entity_id)
    try:
        db.session.delete(entity)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Auto-generate routes for all entities
def create_route_handlers():
    """Create route handlers to avoid lambda closure issues"""

    def make_list_handler(entity_name):
        def handler():
            return get_entity_list(entity_name)
        return handler

    def make_detail_handler(entity_name):
        def handler(entity_id):
            return get_entity_detail(entity_name, entity_id)
        return handler

    def make_create_handler(entity_name):
        def handler():
            return create_entity(entity_name)
        return handler

    def make_update_handler(entity_name):
        def handler(entity_id):
            return update_entity(entity_name, entity_id)
        return handler

    def make_delete_handler(entity_name):
        def handler(entity_id):
            return delete_entity(entity_name, entity_id)
        return handler

    # Register routes for all entities
    for entity_name in ENTITIES:
        singular = entity_name[:-1] if entity_name.endswith('s') else entity_name

        # GET list
        api_entities_bp.add_url_rule(f'/{entity_name}', f'list_{entity_name}',
                                    make_list_handler(entity_name))

        # GET single
        api_entities_bp.add_url_rule(f'/{entity_name}/<int:entity_id>', f'get_{singular}',
                                    make_detail_handler(entity_name))

        # POST create
        api_entities_bp.add_url_rule(f'/{entity_name}', f'create_{singular}',
                                    make_create_handler(entity_name), methods=['POST'])

        # PUT update
        api_entities_bp.add_url_rule(f'/{entity_name}/<int:entity_id>', f'update_{singular}',
                                    make_update_handler(entity_name), methods=['PUT'])

        # DELETE
        api_entities_bp.add_url_rule(f'/{entity_name}/<int:entity_id>', f'delete_{singular}',
                                    make_delete_handler(entity_name), methods=['DELETE'])

# Call the function to register routes
create_route_handlers()

# Task creation helper functions - DRY and focused
def _parse_date_field(date_string):
    """Parse date string to date object"""
    if not date_string:
        return None
    from datetime import datetime
    return datetime.strptime(date_string, "%Y-%m-%d").date()


def _process_linked_entities(data):
    """Process and normalize linked entities data"""
    linked_entities = data.get("linked_entities", [])
    if isinstance(linked_entities, str):
        import json
        linked_entities = json.loads(linked_entities)
    return linked_entities


def _parse_task_data(data):
    """Parse and validate task data with defaults"""
    allowed_fields = [
        "description", "due_date", "priority", "status", "next_step_type", "task_type"
    ]

    task_data = {}
    for field in allowed_fields:
        if field in data:
            if field == "due_date":
                task_data[field] = _parse_date_field(data[field])
            else:
                task_data[field] = data[field]

    # Set defaults
    task_data.setdefault("task_type", "single")
    task_data.setdefault("priority", "medium")
    task_data.setdefault("status", "todo")

    return task_data


def _create_single_task(data):
    """Create a single task with linked entities"""
    task_data = _parse_task_data(data)
    task = Task(**task_data)
    db.session.add(task)
    db.session.flush()

    linked_entities = _process_linked_entities(data)
    if linked_entities:
        task.set_linked_entities(linked_entities)

    db.session.commit()
    return task


def _create_multi_task(data):
    """Create parent task with child tasks"""
    # Create parent task
    parent_task = Task(
        description=data["description"],
        due_date=_parse_date_field(data.get("due_date")),
        priority=data.get("priority", "medium"),
        status="todo",
        task_type="parent",
        dependency_type=data.get("dependency_type", "parallel")
    )

    db.session.add(parent_task)
    db.session.flush()

    # Handle linked entities for parent
    linked_entities = _process_linked_entities(data)
    if linked_entities:
        parent_task.set_linked_entities(linked_entities)

    # Create child tasks
    child_tasks_data = data.get("child_tasks", [])
    for i, child_data in enumerate(child_tasks_data):
        if child_data.get("description"):
            child_task = Task(
                description=child_data["description"],
                due_date=_parse_date_field(child_data.get("due_date")),
                priority=child_data.get("priority", "medium"),
                status="todo",
                next_step_type=child_data.get("next_step_type"),
                entity_type=data.get("entity_type"),
                entity_id=data.get("entity_id"),
                task_type="child",
                parent_task_id=parent_task.id,
                sequence_order=i,
                dependency_type=data.get("dependency_type", "parallel")
            )
            db.session.add(child_task)

            # Child tasks inherit parent's linked entities
            if linked_entities:
                db.session.flush()
                child_task.set_linked_entities(linked_entities)

    db.session.commit()
    return parent_task


# Task endpoints - clean and focused
@api_entities_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create new task with support for linked entities"""
    try:
        data = request.get_json()

        # Route to appropriate task creation function
        if data.get("task_type") == "multi":
            task = _create_multi_task(data)
        else:
            task = _create_single_task(data)

        return jsonify(task.to_dict()), 201

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

        # Use the same ENTITIES mapping for consistency
        entity_singular = entity_type.lower()
        if entity_singular.endswith('s'):
            entity_plural = entity_singular
        else:
            entity_plural = f"{entity_singular}s"

        model_class = ENTITIES.get(entity_plural)
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
            error_html = f'<p data-validation-error="true">A {entity_type} with this {field_label.lower()} already exists.</p>'
            return error_html, 200

        # Return empty string for valid input
        return '', 200

    except Exception as e:
        # On error, don't block the user
        return '', 200