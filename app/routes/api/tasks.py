from flask import Blueprint, request, jsonify
from app.models import db, Task
from app.utils.route_helpers import NotesAPIHandler
from datetime import timedelta, date

tasks_api_bp = Blueprint("tasks_api", __name__, url_prefix="/api/tasks")

# Initialize notes handler for tasks
notes_handler = NotesAPIHandler(Task, "task")


@tasks_api_bp.route("/<int:task_id>")
def get_task(task_id):
    """Get a specific task as JSON"""
    task = Task.query.get_or_404(task_id)
    
    # Use the model's to_dict method for consistent serialization
    task_data = task.to_dict()
    
    # Include child task information for parent tasks
    if task.task_type == "parent":
        task_data["child_tasks"] = [
            {
                "id": child.id,
                "description": child.description,
                "status": child.status,
                "priority": child.priority,
            }
            for child in task.child_tasks
        ]
    
    return jsonify(task_data)


@tasks_api_bp.route("/<int:task_id>/notes", methods=["GET"])
def get_task_notes(task_id):
    """Get all notes for a specific task"""
    return notes_handler.get_notes(task_id)


@tasks_api_bp.route("/<int:task_id>/notes", methods=["POST"])
def create_task_note(task_id):
    """Create a new note for a specific task"""
    return notes_handler.create_note(task_id)


@tasks_api_bp.route("/<int:task_id>/reschedule", methods=["PUT"])
def reschedule_task(task_id):
    """Reschedule a task by adjusting its due date"""
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        days_adjustment = data.get("days_adjustment", 0)

        # Update the due date
        if task.due_date:
            task.due_date = task.due_date + timedelta(days=days_adjustment)
        else:
            task.due_date = date.today() + timedelta(days=days_adjustment)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Task rescheduled by {days_adjustment} days",
            "due_date": task.due_date.isoformat() if task.due_date else None,
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
