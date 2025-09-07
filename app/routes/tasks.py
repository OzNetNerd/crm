from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import db, Task, Company, Contact, Opportunity
from app.forms import MultiTaskForm

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/")
def index():
    # Check if user wants to show completed tasks
    show_completed = request.args.get('show_completed', 'false').lower() == 'true'
    
    if show_completed:
        tasks_query = Task.query.order_by(Task.due_date.asc()).all()
    else:
        # Filter out completed tasks by default
        tasks_query = Task.query.filter(Task.status != 'complete').order_by(Task.due_date.asc()).all()
    
    today = date.today()

    # Convert tasks to dictionaries for JSON serialization
    tasks = [task.to_dict() for task in tasks_query]

    # Serialize objects for JSON use in templates
    companies_data = [
        {"id": c.id, "name": c.name} for c in Company.query.order_by(Company.name).all()
    ]
    contacts_data = [
        {"id": c.id, "name": c.name} for c in Contact.query.order_by(Contact.name).all()
    ]
    opportunities_data = [
        {"id": o.id, "name": o.name}
        for o in Opportunity.query.order_by(Opportunity.name).all()
    ]

    return render_template(
        "tasks/index.html",
        tasks=tasks,
        tasks_objects=tasks_query,  # Keep original objects for template logic
        today=today,
        show_completed=show_completed,
        companies=companies_data,
        contacts=contacts_data,
        opportunities=opportunities_data,
    )


@tasks_bp.route("/<int:task_id>")
def detail(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("tasks/detail.html", task=task)


@tasks_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form

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
            entity_type=data.get("entity_type"),
            entity_id=data.get("entity_id"),
            task_type=data.get("task_type", "single"),
            parent_task_id=data.get("parent_task_id"),
            sequence_order=data.get("sequence_order", 0),
            dependency_type=data.get("dependency_type", "parallel"),
        )

        db.session.add(task)
        db.session.commit()

        if request.is_json:
            return jsonify({"status": "success", "task_id": task.id})
        else:
            return redirect(url_for("tasks.detail", task_id=task.id))

    companies = Company.query.order_by(Company.name).all()
    contacts = Contact.query.order_by(Contact.name).all()
    opportunities = Opportunity.query.order_by(Opportunity.name).all()

    return render_template(
        "tasks/new.html",
        companies=companies,
        contacts=contacts,
        opportunities=opportunities,
    )


@tasks_bp.route("/multi/new", methods=["GET", "POST"])
def new_multi():
    """Create a new Multi Task with child tasks using WTF form validation"""
    form = MultiTaskForm()

    # Populate entity choices dynamically
    companies = Company.query.order_by(Company.name).all()
    contacts = Contact.query.order_by(Contact.name).all()
    opportunities = Opportunity.query.order_by(Opportunity.name).all()

    if form.validate_on_submit():
        try:
            # Create parent task
            parent_task = Task(
                description=form.description.data,
                due_date=form.due_date.data,
                priority=form.priority.data,
                status="todo",
                entity_type=form.entity_type.data if form.entity_type.data else None,
                entity_id=form.entity_id.data if form.entity_id.data else None,
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
                        entity_type=(
                            form.entity_type.data if form.entity_type.data else None
                        ),
                        entity_id=form.entity_id.data if form.entity_id.data else None,
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
            entity_type=data.get("entity_type"),
            entity_id=data.get("entity_id"),
            task_type="parent",
            dependency_type=data.get("dependency_type", "parallel"),
        )

        db.session.add(parent_task)
        db.session.flush()

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

        db.session.commit()
        return jsonify({"status": "success", "task_id": parent_task.id})

    # Convert objects to dictionaries for JSON serialization in template
    companies_dict = [{"id": c.id, "name": c.name} for c in companies]
    contacts_dict = [
        {"id": c.id, "name": c.name, "company_id": c.company_id} for c in contacts
    ]
    opportunities_dict = [
        {"id": o.id, "name": o.name, "company_id": o.company_id} for o in opportunities
    ]

    return render_template(
        "tasks/multi_new.html",
        form=form,
        companies=companies_dict,
        contacts=contacts_dict,
        opportunities=opportunities_dict,
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
        return jsonify({"status": "success", "message": "Task deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
