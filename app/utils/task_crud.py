"""Task-specific CRUD utilities - handling task creation logic."""

from datetime import datetime
from app.models import db, Task


def parse_date_field(date_string):
    """Parse date string to date object."""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def process_linked_entities(data):
    """Extract and process linked entities from request data."""
    linked_entities = []
    for entity_type in ["company", "opportunity", "stakeholder"]:
        entity_id = data.pop(f"{entity_type}_id", None)
        if entity_id:
            linked_entities.append({"type": entity_type, "id": entity_id})
    return linked_entities


def parse_task_data(data):
    """Parse and validate task data from request."""
    # Parse dates
    data["due_date"] = parse_date_field(data.get("due_date"))
    data["expected_close_date"] = parse_date_field(data.get("expected_close_date"))

    # Process linked entities
    linked_entities = process_linked_entities(data)

    # Clean up data
    data.pop("linked_entities", None)  # Remove if exists from client

    return data, linked_entities


def create_single_task(data):
    """Create a single task."""
    data, linked_entities = parse_task_data(data)

    task = Task(**data)
    db.session.add(task)
    db.session.flush()  # Get ID without committing

    # Add linked entities
    if linked_entities:
        for entity in linked_entities:
            task.add_linked_entity(entity["type"], entity["id"])

    db.session.commit()
    return task


def create_multi_task(data):
    """Create parent task with children."""
    parent_data = {
        "description": data.get("description", "Multi-task project"),
        "due_date": parse_date_field(data.get("due_date")),
        "priority": data.get("priority", "medium"),
        "status": "todo",
        "task_type": "parent",
        "comments": data.get("comments", ""),
    }

    # Process linked entities for parent
    linked_entities = process_linked_entities(data)

    # Create parent task
    parent_task = Task(**parent_data)
    db.session.add(parent_task)
    db.session.flush()

    # Add linked entities to parent
    if linked_entities:
        for entity in linked_entities:
            parent_task.add_linked_entity(entity["type"], entity["id"])

    # Create child tasks
    children = data.get("children", [])
    dependency_type = data.get("dependency_type", "parallel")

    for idx, child_data in enumerate(children):
        child = Task(
            description=child_data.get("description", f"Subtask {idx + 1}"),
            due_date=parse_date_field(child_data.get("due_date")),
            priority=child_data.get("priority", parent_data["priority"]),
            status="todo",
            task_type="child",
            parent_task_id=parent_task.id,
            sequence_order=idx,
            dependency_type=dependency_type,
            next_step_type=child_data.get("next_step_type"),
        )
        db.session.add(child)

    db.session.commit()
    return parent_task
