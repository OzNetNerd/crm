from flask import Blueprint, request, jsonify, abort
from app.models import db, Task, MODEL_REGISTRY

api_entities_bp = Blueprint("api_entities", __name__, url_prefix="/api")

# Generic CRUD functions - DRY approach
def get_model_by_name(entity_name):
    """Get model class from entity name (plural or singular)."""
    # Try exact match first (singular form)
    model = MODEL_REGISTRY.get(entity_name)
    if model:
        return model

    # Try plural forms - map common plurals to singular
    plural_map = {
        'companies': 'company',
        'stakeholders': 'stakeholder',
        'opportunities': 'opportunity',
        'tasks': 'task',
        'users': 'user',
        'notes': 'note'
    }

    singular = plural_map.get(entity_name)
    if singular:
        return MODEL_REGISTRY.get(singular)

    return None

def get_entity_list(entity_name):
    """Get list of entities"""
    model = get_model_by_name(entity_name)
    if not model:
        abort(404)

    # Use model's default sort field
    sort_field = model.get_default_sort_field()
    entities = model.query.order_by(getattr(model, sort_field)).all()
    return jsonify([entity.to_dict() for entity in entities])

def get_entity_detail(entity_name, entity_id):
    """Get single entity details"""
    model = get_model_by_name(entity_name)
    if not model:
        abort(404)

    entity = model.query.get_or_404(entity_id)
    return jsonify(entity.to_dict())

def create_entity(entity_name):
    """Create new entity"""
    model = get_model_by_name(entity_name)
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
    model = get_model_by_name(entity_name)
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
    model = get_model_by_name(entity_name)
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

    # Register routes for entities that have API endpoints
    # Use plural forms for REST API endpoints
    # NOTE: 'tasks' is excluded because it has custom handling below
    api_entities = {
        'companies': 'company',
        'stakeholders': 'stakeholder',
        'opportunities': 'opportunity'
    }

    for plural_name, singular_name in api_entities.items():
        # GET list
        api_entities_bp.add_url_rule(f'/{plural_name}', f'list_{plural_name}',
                                    make_list_handler(plural_name))

        # GET single
        api_entities_bp.add_url_rule(f'/{plural_name}/<int:entity_id>', f'get_{singular_name}',
                                    make_detail_handler(plural_name))

        # POST create
        api_entities_bp.add_url_rule(f'/{plural_name}', f'create_{singular_name}',
                                    make_create_handler(plural_name), methods=['POST'])

        # PUT update
        api_entities_bp.add_url_rule(f'/{plural_name}/<int:entity_id>', f'update_{singular_name}',
                                    make_update_handler(plural_name), methods=['PUT'])

        # DELETE
        api_entities_bp.add_url_rule(f'/{plural_name}/<int:entity_id>', f'delete_{singular_name}',
                                    make_delete_handler(plural_name), methods=['DELETE'])

# Call the function to register routes
create_route_handlers()

# Add standard task routes (GET, PUT, DELETE) that don't conflict with custom POST
@api_entities_bp.route("/tasks", methods=["GET"])
def get_tasks():
    """Get list of tasks"""
    return get_entity_list('tasks')

@api_entities_bp.route("/tasks/<int:entity_id>", methods=["GET"])
def get_task(entity_id):
    """Get single task"""
    return get_entity_detail('tasks', entity_id)

@api_entities_bp.route("/tasks/<int:entity_id>", methods=["PUT"])
def update_task(entity_id):
    """Update task"""
    return update_entity('tasks', entity_id)

@api_entities_bp.route("/tasks/<int:entity_id>", methods=["DELETE"])
def delete_task(entity_id):
    """Delete task"""
    return delete_entity('tasks', entity_id)

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


# Task endpoints - custom handling for complex task creation
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

        # Allow empty values - they're handled by required validation
        if not field_value:
            return '', 200

        # Use MODEL_REGISTRY for validation
        model_class = MODEL_REGISTRY.get(entity_type.lower())
        if not model_class:
            return '', 200  # Unknown entity, allow

        # Check for duplicates based on field
        unique_fields = {
            'Company': {'name'},
            'Stakeholder': {'email'},
            'Opportunity': set()  # No unique fields for opportunities
        }

        model_name = model_class.__name__
        allowed_fields = unique_fields.get(model_name, set())

        # Only validate if this field should be unique
        if field_name not in allowed_fields:
            return '', 200

        # Always check database for duplicates (case-insensitive)
        field_attribute = getattr(model_class, field_name)
        existing = model_class.query.filter(
            field_attribute.ilike(field_value)
        ).first()


        if existing:
            field_label = field_name.replace('_', ' ').title()
            error_message = f'A {entity_type} with this {field_label.lower()} already exists.'
            return jsonify({'error': error_message}), 400

        # No duplicates found - field is valid
        return '', 200

    except Exception as e:
        # On error, don't block the user - but log for debugging
        return '', 200