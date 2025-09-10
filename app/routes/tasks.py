from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import db, Task, Company, Stakeholder, Opportunity
from app.forms import MultiTaskForm
from app.utils.route_helpers import (
    BaseRouteHandler,
    parse_int_field,
    get_entity_data_for_forms,
)

tasks_bp = Blueprint("tasks", __name__)
task_handler = BaseRouteHandler(Task, "tasks")


def get_all_tasks_context():
    """Simplified function to get all tasks for frontend-only filtering"""
    # Get URL parameters for initial state (frontend will handle filtering/sorting)
    show_completed = request.args.get("show_completed", "false").lower() == "true"
    sort_by = request.args.get("sort_by", "due_date")
    sort_direction = request.args.get("sort_direction", "asc")
    group_by = request.args.get("group_by", "status")
    priority_filter = (
        request.args.get("priority", "").split(",")
        if request.args.get("priority", "")
        else []
    )
    entity_filter = (
        request.args.get("entity", "").split(",")
        if request.args.get("entity", "")
        else []
    )

    # Get ALL tasks - filtering/sorting will be done in frontend
    all_tasks = Task.query.order_by(Task.created_at.desc()).all()

    return {
        "all_tasks": all_tasks,
        "show_completed": show_completed,
        "sort_by": sort_by,
        "sort_direction": sort_direction,
        "group_by": group_by,
        "priority_filter": priority_filter,
        "entity_filter": entity_filter,
        "today": date.today(),
    }


# Removed /content endpoint - using frontend-only filtering


@tasks_bp.route("/")
def index():
    # Get all context data for frontend-only filtering
    context = get_all_tasks_context()

    # Convert tasks to dictionaries for JSON serialization (for Alpine.js compatibility)
    print(f"DEBUG: Found {len(context['all_tasks'])} tasks from database")
    tasks = []
    for i, task in enumerate(context["all_tasks"]):
        try:
            task_dict = task.to_dict()
            tasks.append(task_dict)
        except Exception as e:
            print(f"ERROR: Task {i} (ID: {task.id}) failed to serialize: {e}")

    print(f"DEBUG: Successfully serialized {len(tasks)} tasks")

    # Test final JSON serialization
    try:
        import json

        json_str = json.dumps(tasks)
        print(f"DEBUG: Final JSON length: {len(json_str)}")
    except Exception as e:
        print(f"ERROR: Final JSON serialization failed: {e}")
        tasks = []

    # Serialize objects for JSON use in templates
    companies_data = [
        {"id": c.id, "name": c.name} for c in Company.query.order_by(Company.name).all()
    ]
    contacts_data = [
        {"id": c.id, "name": c.name}
        for c in Stakeholder.query.order_by(Stakeholder.name).all()
    ]
    opportunities_data = [
        {"id": o.id, "name": o.name}
        for o in Opportunity.query.order_by(Opportunity.name).all()
    ]

    return render_template(
        "tasks/index.html",
        tasks=tasks,
        tasks_objects=context["all_tasks"],  # Keep original objects for template logic
        today=context["today"],
        show_completed=context["show_completed"],
        sort_by=context["sort_by"],
        sort_direction=context["sort_direction"],
        group_by=context["group_by"],
        priority_filter=context["priority_filter"],
        entity_filter=context["entity_filter"],
        companies=companies_data,
        contacts=contacts_data,
        opportunities=opportunities_data,
    )




@tasks_bp.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        try:
            data = request.get_json()

            # Create the task with basic fields
            task = Task(
                description=data["description"],
                due_date=(
                    datetime.strptime(data["due_date"], "%Y-%m-%d").date()
                    if data.get("due_date")
                    else None
                ),
                priority=data.get("priority", "medium"),
                status=data.get("status", "todo"),
                next_step_type=data.get("next_step_type"),
                task_type=data.get("task_type", "single"),
                parent_task_id=parse_int_field(data, "parent_task_id"),
                sequence_order=parse_int_field(data, "sequence_order", 0),
                dependency_type=data.get("dependency_type", "parallel"),
            )

            db.session.add(task)
            db.session.flush()  # Get the task ID

            # Handle linked entities
            linked_entities = data.get("linked_entities", [])
            if linked_entities:
                task.set_linked_entities(linked_entities)

            db.session.commit()
            return jsonify({"status": "success", "task_id": task.id})

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    entity_data = get_entity_data_for_forms()
    return render_template(
        "tasks/new.html",
        companies=entity_data["companies"],
        contacts=entity_data["contacts"],
        opportunities=entity_data["opportunities"],
    )


@tasks_bp.route("/multi/new", methods=["GET", "POST"])
def create_multi():
    """Create a new Multi Task with child tasks using WTF form validation"""
    form = MultiTaskForm()

    # Get entity data for form population
    entity_data = get_entity_data_for_forms()

    if form.validate_on_submit():
        try:
            # Create parent task
            parent_task = Task(
                description=form.description.data,
                due_date=form.due_date.data,
                priority=form.priority.data,
                status="todo",
                task_type="parent",
                dependency_type=form.dependency_type.data,
            )

            db.session.add(parent_task)
            db.session.flush()  # Get the parent task ID

            # Create child tasks from form data
            for i, child_form in enumerate(form.child_tasks.entries):
                if child_form.description.data:  # Only create if description exists
                    child_task = Task(
                        description=child_form.description.data,
                        due_date=child_form.due_date.data,
                        priority=child_form.priority.data,
                        status="todo",
                        next_step_type=(
                            child_form.next_step_type.data
                            if child_form.next_step_type.data
                            else None
                        ),
                        task_type="child",
                        parent_task_id=parent_task.id,
                        sequence_order=i,
                        dependency_type=form.dependency_type.data,
                    )
                    db.session.add(child_task)

            db.session.commit()
            flash("Multi Task created successfully!", "success")
            return redirect(url_for("tasks.index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating Multi Task: {str(e)}", "error")

    # Handle JSON requests (from JavaScript)
    elif request.is_json and request.method == "POST":
        try:
            data = request.get_json()

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
            db.session.flush()  # Get the parent task ID

            # Handle linked entities for parent task
            linked_entities = data.get("linked_entities", [])
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
                        task_type="child",
                        parent_task_id=parent_task.id,
                        sequence_order=i,
                        dependency_type=data.get("dependency_type", "parallel"),
                    )
                    db.session.add(child_task)
                    db.session.flush()  # Get child task ID

                    # Handle linked entities for child task (inherit from parent)
                    if linked_entities:
                        child_task.set_linked_entities(linked_entities)

            db.session.commit()
            return jsonify({"status": "success", "task_id": parent_task.id})

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    return render_template(
        "tasks/multi_new.html",
        form=form,
        companies=entity_data["companies"],
        contacts=entity_data["contacts"],
        opportunities=entity_data["opportunities"],
    )


@tasks_bp.route("/parent-tasks", methods=["GET"])
def get_parent_tasks():
    """API endpoint to get available parent tasks for child task creation"""
    parent_tasks = (
        Task.query.filter_by(task_type="parent").order_by(Task.created_at.desc()).all()
    )

    return jsonify(
        [
            {
                "id": task.id,
                "description": task.description,
                "priority": task.priority,
                "completion_percentage": task.completion_percentage,
            }
            for task in parent_tasks
        ]
    )


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task"""
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return (
            jsonify({"status": "success", "message": "Task deleted successfully"}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route("/debug-data")
def debug_data():
    """Debug endpoint to test data flow"""
    context = get_all_tasks_context()
    tasks_data = [task.to_dict() for task in context["all_tasks"]]

    companies_data = [
        {"id": c.id, "name": c.name} for c in Company.query.order_by(Company.name).all()
    ]

    return jsonify(
        {
            "data_counts": {
                "tasks": len(tasks_data),
                "companies": len(companies_data),
                "database_tasks": Task.query.count(),
                "database_companies": Company.query.count(),
            },
            "sample_task": tasks_data[0] if tasks_data else None,
            "sample_company": companies_data[0] if companies_data else None,
        }
    )
