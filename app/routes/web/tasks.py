from datetime import datetime
from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from app.models import db, Task, Company, Stakeholder, Opportunity
from app.forms import MultiTaskForm

tasks_bp = Blueprint("tasks", __name__)


def _create_task(description, due_date=None, priority='medium', status='todo',
                task_type='single', parent_id=None, order=None, **kwargs):
    """Create a task with common parameters"""
    task = Task(
        description=description,
        due_date=due_date,
        priority=priority,
        status=status,
        task_type=task_type,
        parent_task_id=parent_id,
        sequence_order=order,
        **kwargs
    )
    db.session.add(task)
    db.session.flush()
    return task


def _parse_date(date_value):
    """Parse date from various formats"""
    if not date_value:
        return None
    if isinstance(date_value, str):
        return datetime.strptime(date_value, "%Y-%m-%d").date()
    return date_value


def _get_request_data(form=None):
    """Extract data from form or JSON request"""
    if form and form.validate_on_submit():
        return {
            'description': form.description.data,
            'due_date': form.due_date.data,
            'priority': form.priority.data,
            'dependency_type': form.dependency_type.data,
            'entity_type': form.entity_type.data,
            'entity_id': form.entity_id.data,
            'child_tasks': [
                {
                    'description': c.description.data,
                    'due_date': c.due_date.data,
                    'priority': c.priority.data,
                    'next_step_type': c.next_step_type.data
                }
                for c in form.child_tasks.entries
                if c.description.data
            ]
        }
    elif request.is_json:
        data = request.get_json()
        return {
            'description': data['description'],
            'due_date': _parse_date(data.get('due_date')),
            'priority': data.get('priority', 'medium'),
            'dependency_type': data.get('dependency_type', 'parallel'),
            'linked_entities': data.get('linked_entities', []),
            'child_tasks': data.get('child_tasks', [])
        }
    return None


@tasks_bp.route("/multi/create", methods=["GET", "POST"])
def create_multi():
    """Create a new Multi Task with child tasks"""
    form = MultiTaskForm()

    # GET request - show form
    if request.method == "GET":
        entity_data = {
            'companies': Company.query.order_by(Company.name).all(),
            'contacts': Stakeholder.query.order_by(Stakeholder.name).all(),
            'opportunities': Opportunity.query.order_by(Opportunity.name).all()
        }
        return render_template(
            "components/modals/wtforms_modal.html",
            form=form,
            model_name='task',
            modal_title='Create Multi Task',
            action_url='/tasks/multi/create',
            is_edit=False,
            **entity_data
        )

    # POST request - process data
    data = _get_request_data(form)
    if not data:
        if request.is_json:
            return jsonify({"status": "error", "message": "Invalid data"}), 400
        flash("Invalid form data", "error")
        return redirect(url_for("entities.tasks_index"))

    try:
        # Create parent task
        parent = _create_task(
            description=data['description'],
            due_date=data.get('due_date'),
            priority=data.get('priority', 'medium'),
            task_type='parent',
            dependency_type=data.get('dependency_type', 'parallel')
        )

        # Handle linked entities
        if data.get('entity_type') and data.get('entity_id'):
            entities = [{'type': data['entity_type'], 'id': data['entity_id']}]
            parent.set_linked_entities(entities)
        elif data.get('linked_entities'):
            parent.set_linked_entities(data['linked_entities'])
            entities = data['linked_entities']
        else:
            entities = None

        # Create child tasks
        for i, child_data in enumerate(data.get('child_tasks', [])):
            if child_data.get('description'):
                child_due = _parse_date(child_data.get('due_date')) if request.is_json else child_data.get('due_date')
                child = _create_task(
                    description=child_data['description'],
                    due_date=child_due,
                    priority=child_data.get('priority', 'medium'),
                    task_type='child',
                    parent_id=parent.id,
                    order=i,
                    next_step_type=child_data.get('next_step_type'),
                    dependency_type=data.get('dependency_type', 'parallel')
                )
                if entities:
                    child.set_linked_entities(entities)

        db.session.commit()

        # Return response
        if request.is_json:
            return jsonify({"status": "success", "task_id": parent.id})
        flash("Multi Task created successfully!", "success")
        return redirect(url_for("entities.tasks_index"))

    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({"status": "error", "message": str(e)}), 500
        flash(f"Error creating Multi Task: {str(e)}", "error")
        return redirect(url_for("entities.tasks_index"))


@tasks_bp.route("/parent-tasks", methods=["GET"])
def get_parent_tasks():
    """API endpoint to get available parent tasks for child task creation"""
    parent_tasks = Task.query.filter_by(task_type="parent").order_by(Task.created_at.desc()).all()
    return jsonify([
        {
            "id": task.id,
            "description": task.description,
            "priority": task.priority,
            "completion_percentage": task.completion_percentage,
        }
        for task in parent_tasks
    ])