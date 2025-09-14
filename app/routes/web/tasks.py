from datetime import datetime, date, timedelta
import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import db, Task, Company, Stakeholder, Opportunity
from app.forms import MultiTaskForm
from collections import defaultdict

# Create blueprint
tasks_bp = Blueprint("tasks", __name__)






@tasks_bp.route("/content")
def content():
    """HTMX endpoint for filtered task content"""
    return Task.render_content(
        filter_fields=['status', 'priority', 'task_type'],
        join_map={}  # No joins needed for task sorting
    )


@tasks_bp.route("/")
def index():
    # Get all tasks
    all_tasks = Task.query.order_by(Task.created_at.desc()).all()

    # Convert tasks to dictionaries for JSON serialization (for Alpine.js compatibility)
    tasks = []
    for i, task in enumerate(all_tasks):
        try:
            task_dict = task.to_dict()
            tasks.append(task_dict)
        except Exception as e:
            logging.error(f"Task {i} (ID: {task.id}) failed to serialize: {e}")

    # Test final JSON serialization
    try:
        import json
        json_str = json.dumps(tasks)
    except Exception as e:
        logging.error(f"Final JSON serialization failed: {e}")
        tasks = []

    # Simple entity stats
    entity_stats = {
        'title': 'Task Summary',
        'stats': [
            {
                'value': len([t for t in all_tasks if t.status == 'todo']),
                'label': 'To Do'
            },
            {
                'value': len([t for t in all_tasks if t.status == 'in-progress']),
                'label': 'In Progress'
            },
            {
                'value': len([t for t in all_tasks if t.status == 'complete']),
                'label': 'Complete'
            },
            {
                'value': len([t for t in all_tasks if hasattr(t, 'is_overdue') and t.is_overdue]),
                'label': 'Overdue'
            }
        ]
    }

    # Simple context building - no over-engineered helpers
    base_context = {
        'entity_config': {
            'entity_name': 'Tasks',
            'entity_name_singular': 'Task',
            'entity_description': 'Manage your tasks',
            'entity_type': 'task',
            'endpoint_name': 'tasks',
            'entity_buttons': ['tasks']
        },
        'entity_stats': entity_stats,
        'tasks': tasks,
        'tasks_objects': all_tasks,
        'dropdown_configs': {
            'group_by': {
                'options': [
                    {'value': 'status', 'label': 'Status'},
                    {'value': 'priority', 'label': 'Priority'},
                    {'value': 'due_date', 'label': 'Due Date'}
                ],
                'current_value': request.args.get('group_by', 'status'),
                'placeholder': 'Group by...'
            },
            'sort_by': {
                'options': [
                    {'value': 'due_date', 'label': 'Due Date'},
                    {'value': 'priority', 'label': 'Priority'},
                    {'value': 'created_at', 'label': 'Created Date'},
                    {'value': 'status', 'label': 'Status'}
                ],
                'current_value': request.args.get('sort_by', 'due_date'),
                'placeholder': 'Sort by...'
            }
        }
    }
    
    # Add custom filter dropdowns for tasks
    ENTITY_TYPES = [
        {'value': 'company', 'label': Company.__name__},
        {'value': 'opportunity', 'label': Opportunity.__name__}
    ]
    base_context['dropdown_configs']['entity_filter'] = {
        'button_text': 'All Entities',
        'options': ENTITY_TYPES,
        'current_values': request.args.getlist('entity_filter'),
        'name': 'entity_filter'
    }

    # Add status filter
    STATUS_OPTIONS = [
        {'value': 'todo', 'label': 'To Do'},
        {'value': 'in-progress', 'label': 'In Progress'},
        {'value': 'complete', 'label': 'Complete'}
    ]
    base_context['dropdown_configs']['primary_filter'] = {
        'button_text': 'All Status',
        'options': STATUS_OPTIONS,
        'current_values': request.args.getlist('primary_filter'),
        'name': 'primary_filter'
    }

    # Add priority filter
    PRIORITY_OPTIONS = [
        {'value': 'high', 'label': 'High'},
        {'value': 'medium', 'label': 'Medium'},
        {'value': 'low', 'label': 'Low'}
    ]
    base_context['dropdown_configs']['secondary_filter'] = {
        'button_text': 'All Priority',
        'options': PRIORITY_OPTIONS,
        'current_values': request.args.getlist('secondary_filter'),
        'name': 'secondary_filter'
    }

    return render_template("base/entity_index.html", **base_context)






@tasks_bp.route("/multi/create", methods=["GET", "POST"])
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
            
            # Handle entity relationship from form fields
            if form.entity_type.data and form.entity_id.data:
                linked_entities = [{
                    'type': form.entity_type.data,
                    'id': form.entity_id.data
                }]
                parent_task.set_linked_entities(linked_entities)

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
                    db.session.flush()  # Get child task ID
                    
                    # Inherit parent task entity relationships
                    if form.entity_type.data and form.entity_id.data:
                        child_task.set_linked_entities(linked_entities)

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


