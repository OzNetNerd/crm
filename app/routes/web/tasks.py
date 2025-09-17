from datetime import datetime
from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from app.models import db, Task, Company, Stakeholder, Opportunity, MODEL_REGISTRY
from app.forms import MultiTaskForm

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/multi/create", methods=["GET", "POST"])
def create_multi():
    """Create multi-task endpoint."""
    if request.method == "GET":
        return render_task_form()

    form = MultiTaskForm()
    if not form.validate_on_submit():
        flash("Invalid form data", "error")
        return redirect(url_for("entities.tasks_index"))

    parent_id = save_task_hierarchy(form)
    flash("Multi Task created successfully!", "success")
    return redirect(url_for("entities.tasks_index"))


def render_task_form():
    """Render creation form with entities."""
    return render_template(
        "components/modals/wtforms_modal.html",
        form=MultiTaskForm(),
        model_name='task',
        modal_title='Create Multi Task',
        action_url='/tasks/multi/create',
        companies=Company.query.order_by(Company.name).all(),
        contacts=Stakeholder.query.order_by(Stakeholder.name).all(),
        opportunities=Opportunity.query.order_by(Opportunity.name).all()
    )


def save_task_hierarchy(form):
    """Save parent and children to database."""
    parent_task = Task(
        description=form.description.data,
        due_date=form.due_date.data,
        priority=form.priority.data,
        task_type='parent',
        dependency_type=form.dependency_type.data
    )
    db.session.add(parent_task)
    db.session.flush()

    # Link entities if provided
    if form.entity_type.data and form.entity_id.data:
        parent_task.set_linked_entities([{
            'type': form.entity_type.data,
            'id': form.entity_id.data
        }])

    # Add child tasks
    valid_children = [entry for entry in form.child_tasks.entries if entry.description.data]

    for index, child_form in enumerate(valid_children):
        child_task = Task(
            description=child_form.description.data,
            due_date=child_form.due_date.data,
            priority=child_form.priority.data,
            next_step_type=child_form.next_step_type.data,
            parent_task_id=parent_task.id,
            sequence_order=index,
            task_type='child',
            dependency_type=form.dependency_type.data
        )
        db.session.add(child_task)

        # Copy parent's linked entities to child
        if form.entity_type.data and form.entity_id.data:
            child_task.set_linked_entities([{
                'type': form.entity_type.data,
                'id': form.entity_id.data
            }])

    db.session.commit()
    return parent_task.id


@tasks_bp.route("/parent-tasks", methods=["GET"])
def get_parent_tasks():
    """Get parent tasks for dropdowns."""
    parents = Task.query.filter_by(task_type="parent").order_by(Task.created_at.desc()).all()

    return jsonify([{
        "id": task.id,
        "description": task.description,
        "priority": task.priority,
        "completion_percentage": task.completion_percentage
    } for task in parents])