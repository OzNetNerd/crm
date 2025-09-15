from datetime import datetime, date, timedelta
import logging
from flask import Blueprint, render_template, request, jsonify
from app.models import db, Task
from .dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    """
    Dashboard index page showing pipeline overview and recent activity.

    Uses DashboardService to aggregate all dashboard data in a clean,
    maintainable way.
    """
    context = DashboardService.get_dashboard_data()
    return render_template("dashboard/index.html", **context)


@dashboard_bp.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    """Mark a task as complete."""
    task = Task.query.get_or_404(task_id)
    task.status = "complete"
    task.completed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"status": "success", "message": "Task completed"})


@dashboard_bp.route("/tasks/<int:task_id>/update", methods=["POST"])
def update_task(task_id):
    """Update task fields from dashboard."""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    # Update fields if provided
    if "description" in data:
        task.description = data["description"]
    if "due_date" in data:
        task.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
    if "priority" in data:
        task.priority = data["priority"]

    db.session.commit()
    return jsonify({"status": "success", "message": "Task updated"})


@dashboard_bp.route("/tasks/<int:task_id>/reschedule", methods=["POST"])
def reschedule_task(task_id):
    """Reschedule a task by specified number of days."""
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        days = data.get("days", 1)

        # Update due date
        if task.due_date:
            task.due_date = task.due_date + timedelta(days=days)
        else:
            task.due_date = date.today() + timedelta(days=days)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Task rescheduled by {days} days",
            "due_date": task.due_date.isoformat() if task.due_date else None
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error rescheduling task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500