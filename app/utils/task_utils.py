"""Simple task utilities - no classes, just functions."""
from typing import List, Dict, Any, Optional


def get_linked_entities(task_id: int) -> List[Dict[str, Any]]:
    """Get all entities linked to a task."""
    if not task_id:
        return []

    from app import db
    from app.models.task import task_entities

    linked = db.session.query(task_entities.c.entity_type, task_entities.c.entity_id).filter(task_entities.c.task_id == task_id).all()

    return [
        {"type": entity_type, "id": entity_id, "name": _get_entity_name(entity_type, entity_id), "entity": _get_entity(entity_type, entity_id)}
        for entity_type, entity_id in linked
        if _get_entity(entity_type, entity_id)
    ]


def _get_entity(entity_type: str, entity_id: int):
    """Get entity by type and id."""
    if entity_type == "company":
        from app.models.company import Company
        return Company.query.get(entity_id)
    elif entity_type == "stakeholder":
        from app.models.stakeholder import Stakeholder
        return Stakeholder.query.get(entity_id)
    elif entity_type == "opportunity":
        from app.models.opportunity import Opportunity
        return Opportunity.query.get(entity_id)
    return None


def _get_entity_name(entity_type: str, entity_id: int) -> str:
    """Get entity name."""
    entity = _get_entity(entity_type, entity_id)
    return entity.name if entity else ""


def get_entity_attr(task_id: int, entity_type: str, attr: str):
    """Get attribute from first matching linked entity."""
    entities = get_linked_entities(task_id)
    entity = next((e for e in entities if e["type"] == entity_type and e["entity"]), None)
    return getattr(entity["entity"], attr, None) if entity else None


def get_company_name(task_id: int) -> Optional[str]:
    """Get company name from any linked entity."""
    entities = get_linked_entities(task_id)

    for entity in entities:
        if entity["type"] == "company":
            return entity["name"]
        elif entity["entity"] and hasattr(entity["entity"], "company") and entity["entity"].company:
            return entity["entity"].company.name
    return None


def can_task_start(task) -> bool:
    """Check if task can be started based on dependencies."""
    if task.task_type != "child" or task.dependency_type != "sequential" or not task.parent_task:
        return True

    from app.models.task import Task
    previous_tasks = Task.query.filter(Task.parent_task_id == task.parent_task_id, Task.sequence_order < task.sequence_order).all()
    return all(t.status == "complete" for t in previous_tasks)


def get_completion_percentage(task) -> int:
    """Calculate completion percentage."""
    if task.task_type != "parent":
        return 100 if task.status == "complete" else 0

    from app.models.task import Task
    child_tasks = Task.query.filter(Task.parent_task_id == task.id).all()

    if not child_tasks:
        return 0

    completed = sum(1 for child in child_tasks if child.status == "complete")
    return int((completed / len(child_tasks)) * 100)


def get_next_available_child(task):
    """Get next child task that can be started."""
    if task.task_type != "parent":
        return None

    return next((child for child in task.child_tasks if child.status != "complete" and can_task_start(child)), None)