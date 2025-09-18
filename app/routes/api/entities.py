from flask import Blueprint, request, jsonify, abort
from app.models import db, Task, MODEL_REGISTRY
from app.utils.entity_crud import (
    get_model_by_table_name,
    get_entity_list,
    get_entity_detail,
    create_entity,
    update_entity,
    delete_entity,
)
from app.utils.task_crud import create_single_task, create_multi_task

api_entities_bp = Blueprint("api_entities", __name__, url_prefix="/api")


def create_route_handlers():
    """Create dynamic routes for all registered models - ULTRA DRY."""
    for model_name, model_class in MODEL_REGISTRY.items():
        if not model_class.is_api_enabled():
            continue

        table_name = model_class.__tablename__

        # Skip Task - has custom handlers
        if table_name == "tasks":
            continue

        # List endpoint
        api_entities_bp.add_url_rule(
            f"/{table_name}",
            endpoint=f"get_{table_name}",
            view_func=lambda t=table_name: get_entity_list(t),
            methods=["GET"],
        )

        # Detail endpoint
        api_entities_bp.add_url_rule(
            f"/{table_name}/<int:entity_id>",
            endpoint=f"get_{table_name}_detail",
            view_func=lambda entity_id, t=table_name: get_entity_detail(t, entity_id),
            methods=["GET"],
        )

        # Create endpoint
        api_entities_bp.add_url_rule(
            f"/{table_name}",
            endpoint=f"create_{table_name}",
            view_func=lambda t=table_name, m=model_class: jsonify(
                create_entity(m, request.get_json()).to_dict()
            ),
            methods=["POST"],
        )

        # Update endpoint
        api_entities_bp.add_url_rule(
            f"/{table_name}/<int:entity_id>",
            endpoint=f"update_{table_name}",
            view_func=lambda entity_id, t=table_name, m=model_class: jsonify(
                update_entity(m, entity_id, request.get_json()).to_dict()
            ),
            methods=["PUT"],
        )

        # Delete endpoint
        api_entities_bp.add_url_rule(
            f"/{table_name}/<int:entity_id>",
            endpoint=f"delete_{table_name}",
            view_func=lambda entity_id, t=table_name, m=model_class: jsonify(
                delete_entity(m, entity_id)
            ),
            methods=["DELETE"],
        )


# Task-specific routes (custom handling required)
@api_entities_bp.route("/tasks", methods=["GET"])
def get_tasks():
    """Get all tasks."""
    return get_entity_list("tasks")


@api_entities_bp.route("/tasks/<int:entity_id>", methods=["GET"])
def get_task(entity_id):
    """Get single task."""
    return get_entity_detail("tasks", entity_id)


@api_entities_bp.route("/tasks", methods=["POST"])
def create_task():
    """Create task - handles single and multi-task."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Determine task type
        if data.get("children"):
            task = create_multi_task(data)
        else:
            task = create_single_task(data)

        return jsonify(task.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@api_entities_bp.route("/tasks/<int:entity_id>", methods=["PUT"])
def update_task(entity_id):
    """Update task."""
    return jsonify(update_entity(Task, entity_id, request.get_json()).to_dict())


@api_entities_bp.route("/tasks/<int:entity_id>", methods=["DELETE"])
def delete_task(entity_id):
    """Delete task with modern safety checks."""
    return jsonify(delete_entity(Task, entity_id))


@api_entities_bp.route("/validate/<entity_type>/<field_name>", methods=["POST"])
def validate_field(entity_type, field_name):
    """Validate a specific field value - useful for form validation."""
    model = get_model_by_table_name(entity_type)
    if not model:
        abort(404)

    data = request.get_json()
    value = data.get("value")
    entity_id = data.get("entity_id")  # For edit mode

    if not value or not value.strip():
        return jsonify({"valid": False, "message": f"{field_name} is required"}), 200

    # Check uniqueness for specific fields
    if field_name in ["email", "name"]:
        # Use case-insensitive search for company names
        if entity_type == "companies" and field_name == "name":
            existing = model.query.filter(model.name.ilike(value.strip())).first()
        else:
            existing = model.query.filter(getattr(model, field_name) == value).first()

        if existing:
            # Allow editing the same entity
            if entity_id and existing.id == int(entity_id):
                return jsonify({"valid": True})

            # Custom message for company names
            if entity_type == "companies" and field_name == "name":
                return (
                    jsonify(
                        {
                            "valid": False,
                            "message": "A company with this name already exists.",
                        }
                    ),
                    200,
                )
            else:
                return (
                    jsonify(
                        {"valid": False, "message": f"{field_name} already exists"}
                    ),
                    200,
                )

    return jsonify({"valid": True})


# Initialize dynamic routes when blueprint is registered
create_route_handlers()
