from datetime import datetime, date, timedelta
import logging
from flask import Blueprint, render_template, request, jsonify
from app.models import db, Task, Company, Stakeholder, Opportunity, Note

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    today = date.today()

    # Quick stats for overview
    task_stats = {
        "overdue": Task.query.filter(
            Task.due_date < today, Task.status != "complete"
        ).count(),
        "today": Task.query.filter(
            Task.due_date == today, Task.status != "complete"
        ).count(),
        "this_week": Task.query.filter(
            Task.due_date > today,
            Task.due_date <= today + timedelta(days=7),
            Task.status != "complete",
        ).count(),
        "completed_today": Task.query.filter(
            Task.status == "complete",
            Task.completed_at >= datetime.combine(today, datetime.min.time()),
        ).count(),
    }

    # Pipeline overview
    opportunities = Opportunity.query.all()
    pipeline_stats = {
        "prospect": sum(
            opp.value or 0 for opp in opportunities if opp.stage == "prospect"
        ),
        "qualified": sum(
            opp.value or 0 for opp in opportunities if opp.stage == "qualified"
        ),
        "proposal": sum(
            opp.value or 0 for opp in opportunities if opp.stage == "proposal"
        ),
        "negotiation": sum(
            opp.value or 0 for opp in opportunities if opp.stage == "negotiation"
        ),
        "total_value": sum(opp.value or 0 for opp in opportunities),
        "total_count": len(opportunities),
    }

    # Recent activity (last 5 items) - with formatting at source
    recent_tasks_raw = (
        Task.query.filter(Task.status != "complete")
        .order_by(Task.created_at.desc())
        .limit(5)
        .all()
    )
    recent_tasks = [task.to_display_dict() for task in recent_tasks_raw]
    
    recent_notes_raw = Note.query.order_by(Note.created_at.desc()).limit(3).all()
    recent_notes = [note.to_display_dict() for note in recent_notes_raw]
    
    recent_opportunities_raw = (
        Opportunity.query.order_by(Opportunity.created_at.desc()).limit(3).all()
    )
    recent_opportunities = [opp.to_display_dict() for opp in recent_opportunities_raw]

    # Key metrics
    metrics = {
        "total_companies": Company.query.count(),
        "total_contacts": Stakeholder.query.count(),
        "total_opportunities": Opportunity.query.count(),
        "total_tasks": Task.query.count(),
    }

    # Critical alerts - with formatting at source
    overdue_tasks_raw = (
        Task.query.filter(Task.due_date < today, Task.status != "complete")
        .limit(5)
        .all()
    )
    overdue_tasks = [task.to_display_dict() for task in overdue_tasks_raw]
    
    closing_soon_raw = (
        Opportunity.query.filter(
            Opportunity.expected_close_date <= today + timedelta(days=7),
            Opportunity.expected_close_date >= today,
            Opportunity.stage.in_(["proposal", "negotiation"]),
        )
        .limit(5)
        .all()
    )
    closing_soon = [opp.to_display_dict() for opp in closing_soon_raw]

    # Get entity types dynamically from model registry
    from app.utils.core.model_introspection import get_all_model_configs
    model_configs = get_all_model_configs()
    entity_types = [name.lower() for name in model_configs.keys()]

    return render_template(
        "dashboard/index.html",
        task_stats=task_stats,
        pipeline_stats=pipeline_stats,
        recent_tasks=recent_tasks,
        recent_notes=recent_notes,
        recent_opportunities=recent_opportunities,
        metrics=metrics,
        overdue_tasks=overdue_tasks,
        closing_soon=closing_soon,
        today=today,
        entity_types=entity_types,
    )


@dashboard_bp.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.status = "complete"
    task.completed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"status": "success", "message": "Task completed"})


@dashboard_bp.route("/tasks/<int:task_id>/update", methods=["POST"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

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
    from datetime import timedelta

    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        days = data.get("days", 1)


        old_due_date = task.due_date

        if task.due_date:
            task.due_date = task.due_date + timedelta(days=days)
        else:
            task.due_date = date.today() + timedelta(days=days)


        db.session.commit()

        return jsonify(
            {
                "status": "success",
                "message": f"Task rescheduled by {days} days",
                "due_date": task.due_date.isoformat() if task.due_date else None,
            }
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error rescheduling task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
