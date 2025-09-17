"""Task routes with multi-task support - DRY and clean."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from app.models import db, Task, Company, Stakeholder, Opportunity
from app.forms import MultiTaskForm


tasks_bp = Blueprint("tasks", __name__)


def get_entity_data() -> Dict[str, List[Any]]:
    """Get entities for form dropdowns.

    Returns:
        Dictionary with companies, contacts, and opportunities.
    """
    return {
        "companies": Company.query.order_by(Company.name).all(),
        "contacts": Stakeholder.query.order_by(Stakeholder.name).all(),
        "opportunities": Opportunity.query.order_by(Opportunity.name).all(),
    }


def create_parent_task(data: Dict[str, Any], from_form: bool = True) -> Task:
    """Create parent task from form or JSON data.

    Args:
        data: Task data from form or JSON.
        from_form: Whether data is from WTForms.

    Returns:
        Created parent task instance.
    """
    if from_form:
        return Task(
            description=data.description.data,
            due_date=data.due_date.data,
            priority=data.priority.data,
            status="todo",
            task_type="parent",
            dependency_type=data.dependency_type.data,
        )

    # JSON data
    return Task(
        description=data["description"],
        due_date=datetime.strptime(data["due_date"], "%Y-%m-%d").date() if data.get("due_date") else None,
        priority=data.get("priority", "medium"),
        status="todo",
        task_type="parent",
        dependency_type=data.get("dependency_type", "parallel"),
    )


def create_child_task(
    child_data: Any,
    parent_id: int,
    sequence: int,
    dependency_type: str,
    from_form: bool = True
) -> Optional[Task]:
    """Create child task from form or JSON data.

    Args:
        child_data: Child task data.
        parent_id: Parent task ID.
        sequence: Sequence order.
        dependency_type: Dependency type from parent.
        from_form: Whether data is from WTForms.

    Returns:
        Created child task or None if no description.
    """
    if from_form:
        if not child_data.description.data:
            return None

        return Task(
            description=child_data.description.data,
            due_date=child_data.due_date.data,
            priority=child_data.priority.data,
            status="todo",
            next_step_type=child_data.next_step_type.data or None,
            task_type="child",
            parent_task_id=parent_id,
            sequence_order=sequence,
            dependency_type=dependency_type,
        )

    # JSON data
    if not child_data.get("description"):
        return None

    return Task(
        description=child_data["description"],
        due_date=datetime.strptime(child_data["due_date"], "%Y-%m-%d").date() if child_data.get("due_date") else None,
        priority=child_data.get("priority", "medium"),
        status="todo",
        next_step_type=child_data.get("next_step_type"),
        task_type="child",
        parent_task_id=parent_id,
        sequence_order=sequence,
        dependency_type=dependency_type,
    )


def set_task_entities(task: Task, entity_type: str, entity_id: int) -> None:
    """Set linked entities for a task.

    Args:
        task: Task instance.
        entity_type: Type of entity.
        entity_id: Entity ID.
    """
    if not (entity_type and entity_id):
        return

    linked_entities = [{"type": entity_type, "id": entity_id}]
    task.set_linked_entities(linked_entities)


def handle_form_submission(form: MultiTaskForm) -> Optional[Any]:
    """Handle form submission for multi-task creation.

    Args:
        form: Validated MultiTaskForm.

    Returns:
        Redirect response on success, None on failure.
    """
    try:
        # Create parent
        parent_task = create_parent_task(form)
        db.session.add(parent_task)
        db.session.flush()

        # Set entities
        set_task_entities(parent_task, form.entity_type.data, form.entity_id.data)

        # Create children
        for i, child_form in enumerate(form.child_tasks.entries):
            child = create_child_task(
                child_form,
                parent_task.id,
                i,
                form.dependency_type.data
            )
            if child:
                db.session.add(child)
                db.session.flush()
                set_task_entities(child, form.entity_type.data, form.entity_id.data)

        db.session.commit()
        flash("Multi Task created successfully!", "success")
        return redirect(url_for("entities.tasks_index"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error creating Multi Task: {str(e)}", "error")
        return None


def handle_json_submission(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON submission for multi-task creation.

    Args:
        data: JSON data from request.

    Returns:
        JSON response with success status.
    """
    try:
        # Create parent
        parent_task = create_parent_task(data, from_form=False)
        db.session.add(parent_task)
        db.session.flush()

        # Set entities
        if entity_data := data.get("entity"):
            set_task_entities(parent_task, entity_data.get("type"), entity_data.get("id"))

        # Create children
        for i, child_data in enumerate(data.get("child_tasks", [])):
            child = create_child_task(
                child_data,
                parent_task.id,
                i,
                data.get("dependency_type", "parallel"),
                from_form=False
            )
            if child:
                db.session.add(child)
                db.session.flush()
                if entity_data:
                    set_task_entities(child, entity_data.get("type"), entity_data.get("id"))

        db.session.commit()
        return {"success": True, "message": "Multi Task created successfully", "task_id": parent_task.id}

    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Error creating Multi Task: {str(e)}"}


@tasks_bp.route("/multi/create", methods=["GET", "POST"])
def create_multi() -> Any:
    """Create a new Multi Task with child tasks.

    Returns:
        Template render for GET, redirect for successful POST,
        or JSON response for API calls.
    """
    # Handle JSON requests
    if request.is_json and request.method == "POST":
        return jsonify(handle_json_submission(request.get_json()))

    form = MultiTaskForm()

    # Handle form submission
    if form.validate_on_submit():
        if response := handle_form_submission(form):
            return response

    # Render form
    entity_data = get_entity_data()
    return render_template(
        "forms/multi_task_form.html",
        form=form,
        entity_data=entity_data
    )


@tasks_bp.route("/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id: int) -> Dict[str, Any]:
    """Mark a task as complete via AJAX.

    Args:
        task_id: ID of task to complete.

    Returns:
        JSON response with success status.
    """
    task = Task.query.get_or_404(task_id)

    try:
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Task marked as complete",
            "task_id": task.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        })


@tasks_bp.route("/<int:task_id>/uncomplete", methods=["POST"])
def uncomplete_task(task_id: int) -> Dict[str, Any]:
    """Mark a task as incomplete via AJAX.

    Args:
        task_id: ID of task to uncomplete.

    Returns:
        JSON response with success status.
    """
    task = Task.query.get_or_404(task_id)

    try:
        task.status = "todo"
        task.completed_at = None
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Task marked as incomplete",
            "task_id": task.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        })