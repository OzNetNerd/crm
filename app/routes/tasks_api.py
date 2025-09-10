from flask import Blueprint, request, jsonify
from app.models import db, Task, Note
from datetime import timedelta, date

tasks_api_bp = Blueprint("tasks_api", __name__)


@tasks_api_bp.route("/<int:task_id>")
def get_task(task_id):
    """Get a specific task as JSON"""
    task = Task.query.get_or_404(task_id)

    task_data = {
        "id": task.id,
        "description": task.description,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority,
        "status": task.status,
        "next_step_type": task.next_step_type,
        "linked_entities": [{"type": entity["type"], "id": entity["id"], "name": entity["name"]} for entity in task.linked_entities],
        "company_name": task.company_name,
        "opportunity_name": task.opportunity_name,
        "entity_name": task.entity_name,
        "is_overdue": task.is_overdue,
        "task_type": task.task_type,
    }

    # Include child task information and completion percentage for parent tasks
    if task.task_type == "parent":
        child_tasks = [
            {
                "id": child.id,
                "description": child.description,
                "status": child.status,
                "priority": child.priority,
            }
            for child in task.child_tasks
        ]
        task_data["child_tasks"] = child_tasks
        task_data["completion_percentage"] = task.completion_percentage

    return jsonify(task_data)


@tasks_api_bp.route("/<int:task_id>/notes", methods=["GET"])
def get_task_notes(task_id):
    """Get all notes for a specific task"""
    try:
        # Verify task exists
        _ = Task.query.get_or_404(task_id)  # Verify task exists

        notes = (
            Note.query.filter_by(entity_type="task", entity_id=task_id)
            .order_by(Note.created_at.desc())
            .all()
        )

        return jsonify(
            [
                {
                    "id": note.id,
                    "content": note.content,
                    "entity_type": note.entity_type,
                    "entity_id": note.entity_id,
                    "is_internal": note.is_internal,
                    "created_at": note.created_at.isoformat(),
                    "entity_name": note.entity_name,
                }
                for note in notes
            ]
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_api_bp.route("/<int:task_id>/notes", methods=["POST"])
def create_task_note(task_id):
    """Create a new note for a specific task"""
    try:
        # Verify task exists
        _ = Task.query.get_or_404(task_id)  # Verify task exists

        data = request.get_json()
        if not data or not data.get("content"):
            return jsonify({"error": "Note content is required"}), 400

        note = Note(
            content=data["content"],
            entity_type="task",
            entity_id=task_id,
            is_internal=data.get("is_internal", True),
        )

        db.session.add(note)
        db.session.commit()

        return (
            jsonify(
                {
                    "id": note.id,
                    "content": note.content,
                    "entity_type": note.entity_type,
                    "entity_id": note.entity_id,
                    "is_internal": note.is_internal,
                    "created_at": note.created_at.isoformat(),
                    "entity_name": note.entity_name,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@tasks_api_bp.route("/<int:task_id>/reschedule", methods=["PUT"])
def reschedule_task(task_id):
    """Reschedule a task by adjusting its due date"""
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
            
        days_adjustment = data.get("days_adjustment", 0)
        
        if task.due_date:
            task.due_date = task.due_date + timedelta(days=days_adjustment)
        else:
            task.due_date = date.today() + timedelta(days=days_adjustment)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Task rescheduled by {days_adjustment} days",
            "due_date": task.due_date.isoformat() if task.due_date else None
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
