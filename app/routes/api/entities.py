from flask import Blueprint, request, jsonify
from app.models import db, Task, Stakeholder, Company, Opportunity
from app.utils.entities.entity_config import EntityConfigGenerator

api_entities_bp = Blueprint("api_entities", __name__, url_prefix="/api")

# Auto-generate entity configurations from model metadata - much more DRY!
ENTITY_CONFIGS = EntityConfigGenerator.generate_all_configs()


# Dynamically register GET detail endpoints (skip tasks - handled by dedicated tasks API)
for entity_name, config in ENTITY_CONFIGS.items():
    if entity_name == "tasks":
        continue  # Tasks have dedicated API in app.routes.api.tasks
        
    route_param = config["route_param"]
    handler = config["handler"]
    
    # Create endpoint function with proper closure
    def make_detail_endpoint(handler_func):
        def endpoint(entity_id):
            return handler_func(entity_id)
        return endpoint
    
    endpoint_func = make_detail_endpoint(handler.get_details)
    endpoint_func.__name__ = f"get_{entity_name[:-1]}_details"  # Remove 's' from plural
    endpoint_func.__doc__ = f"Get {entity_name[:-1]} details with notes"
    
    api_entities_bp.route(f"/{entity_name}/<int:{route_param}>")(endpoint_func)


# Dynamically register GET list endpoints for dropdowns (skip tasks - not needed for dropdowns)  
for entity_name, config in ENTITY_CONFIGS.items():
    if entity_name == "tasks":
        continue  # Tasks don't need dropdown endpoints
        
    handler = config["handler"]
    list_serializer = config.get("list_serializer")
    
    # Create list endpoint function with proper closure
    def make_list_endpoint(handler_func, serializer):
        def endpoint():
            return handler_func(field_serializer=serializer, order_by_field="name")
        return endpoint
    
    endpoint_func = make_list_endpoint(handler.get_list, list_serializer)
    endpoint_func.__name__ = f"get_{entity_name}"  # Keep plural for list endpoints
    endpoint_func.__doc__ = f"Get all {entity_name} for form dropdowns"
    
    api_entities_bp.route(f"/{entity_name}")(endpoint_func)


# Dynamically register PUT endpoints for entity updates (skip tasks - handled by dedicated tasks API)
for entity_name, config in ENTITY_CONFIGS.items():
    if entity_name == "tasks":
        continue  # Tasks have dedicated API in app.routes.api.tasks
        
    route_param = config["route_param"]
    handler = config["handler"]
    update_fields = config["update_fields"]
    
    # Create update endpoint function with proper closure
    def make_update_endpoint(handler_func, fields):
        def endpoint(entity_id):
            return handler_func(entity_id, fields)
        return endpoint
    
    endpoint_func = make_update_endpoint(handler.update_entity, update_fields)
    endpoint_func.__name__ = f"update_{entity_name[:-1]}"  # Remove 's' from plural
    endpoint_func.__doc__ = f"Update {entity_name[:-1]} details"
    
    api_entities_bp.route(f"/{entity_name}/<int:{route_param}>", methods=["PUT"])(endpoint_func)


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


# Dynamically register POST endpoints for simple entity creation (skip tasks - has custom logic)
for entity_name, config in ENTITY_CONFIGS.items():
    if config.get("has_custom_create"):
        continue  # Skip entities with custom creation logic
        
    handler = config["handler"]
    create_fields = config["create_fields"]
    
    # Create endpoint function with proper closure
    def make_create_endpoint(handler_func, fields):
        def endpoint():
            return handler_func(fields)
        return endpoint
    
    endpoint_func = make_create_endpoint(handler.create_entity, create_fields)
    endpoint_func.__name__ = f"create_{entity_name[:-1]}"  # Remove 's' from plural
    endpoint_func.__doc__ = f"Create new {entity_name[:-1]}"
    
    api_entities_bp.route(f"/{entity_name}", methods=["POST"])(endpoint_func)


# Dynamically register DELETE endpoints for entity deletion (skip tasks - handled by dedicated tasks API if needed)
for entity_name, config in ENTITY_CONFIGS.items():
    if entity_name == "tasks":
        continue  # Tasks don't currently have delete endpoint, but would be handled by dedicated API
        
    route_param = config["route_param"]
    handler = config["handler"]
    
    # Create delete endpoint function with proper closure
    def make_delete_endpoint(handler_func):
        def endpoint(entity_id):
            return handler_func(entity_id)
        return endpoint
    
    endpoint_func = make_delete_endpoint(handler.delete_entity)
    endpoint_func.__name__ = f"delete_{entity_name[:-1]}"  # Remove 's' from plural
    endpoint_func.__doc__ = f"Delete {entity_name[:-1]}"
    
    api_entities_bp.route(f"/{entity_name}/<int:{route_param}>", methods=["DELETE"])(endpoint_func)