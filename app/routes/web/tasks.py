from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import db, Task, Company, Stakeholder, Opportunity
from app.forms import MultiTaskForm
from app.utils.route_helpers import (
    BaseRouteHandler,
    parse_int_field,
    get_entity_data_for_forms,
    EntityFilterManager,
    EntityGrouper,
)
from app.utils.model_introspection import ModelIntrospector
from collections import defaultdict

tasks_bp = Blueprint("tasks", __name__)
task_handler = BaseRouteHandler(Task, "tasks")
task_filter_manager = EntityFilterManager(Task, "task")


def task_custom_filters(query, filters):
    """Task-specific filtering logic"""
    if not filters['show_completed']:
        query = query.filter(Task.status != 'complete')
    
    if filters['priority_filter']:
        query = query.filter(Task.priority.in_(filters['priority_filter']))
        
    if filters['entity_filter']:
        query = query.filter(Task.entity_type.in_(filters['entity_filter']))
    
    return query


def task_custom_sorting(query, sort_by, sort_direction):
    """Task-specific sorting logic"""
    if sort_by == "due_date":
        if sort_direction == "desc":
            return query.order_by(Task.due_date.desc().nulls_last())
        else:
            return query.order_by(Task.due_date.asc().nulls_first())
    elif sort_by == "priority":
        # Custom priority order: high, medium, low
        priority_order = ["high", "medium", "low"]
        if sort_direction == "desc":
            priority_order.reverse()
        
        from sqlalchemy import case
        priority_case = case(
            {priority: i for i, priority in enumerate(priority_order)},
            value=Task.priority
        )
        return query.order_by(priority_case)
    elif sort_by == "created_at":
        if sort_direction == "desc":
            return query.order_by(Task.created_at.desc())
        else:
            return query.order_by(Task.created_at.asc())
    else:
        # Default sort
        return query.order_by(Task.created_at.desc())


def task_custom_groupers(entities, group_by):
    """Task-specific grouping logic"""
    grouped = defaultdict(list)
    
    if group_by == "status":
        # Predefined status groups
        status_groups = ["todo", "in-progress", "complete"]
        for task in entities:
            status = task.status or "todo"
            grouped[status].append(task)
        
        # Return in predefined order
        result = []
        for status in status_groups:
            if grouped[status]:
                result.append({
                    "key": status,
                    "label": status.replace("-", " ").title(),
                    "entities": grouped[status],
                    "count": len(grouped[status])
                })
        return result
        
    elif group_by == "priority":
        # Predefined priority groups
        priority_groups = ["high", "medium", "low"]
        for task in entities:
            priority = task.priority or "medium"
            grouped[priority].append(task)
        
        # Return in priority order
        result = []
        for priority in priority_groups:
            if grouped[priority]:
                result.append({
                    "key": priority,
                    "label": priority.title(),
                    "entities": grouped[priority],
                    "count": len(grouped[priority])
                })
        return result
        
    elif group_by == "due_date":
        # Group by due date categories
        today = date.today()
        
        for task in entities:
            if not task.due_date:
                grouped["no_date"].append(task)
            elif task.due_date < today:
                grouped["overdue"].append(task)
            elif task.due_date == today:
                grouped["today"].append(task)
            elif task.due_date <= today + timedelta(days=7):
                grouped["this_week"].append(task)
            else:
                grouped["future"].append(task)
        
        # Return in chronological order
        date_groups = ["overdue", "today", "this_week", "future", "no_date"]
        labels = {
            "overdue": "Overdue",
            "today": "Due Today", 
            "this_week": "Due This Week",
            "future": "Future",
            "no_date": "No Due Date"
        }
        
        result = []
        for group_key in date_groups:
            if grouped[group_key]:
                result.append({
                    "key": group_key,
                    "label": labels[group_key],
                    "entities": grouped[group_key],
                    "count": len(grouped[group_key])
                })
        return result
    
    return None  # Use default grouping


def get_all_tasks_context():
    """Simplified function to get all tasks for frontend-only filtering"""
    # Get URL parameters for initial state (frontend will handle filtering/sorting)
    show_completed = request.args.get("show_completed", "false").lower() == "true"
    sort_by = request.args.get("sort_by", "due_date")
    sort_direction = request.args.get("sort_direction", "asc")
    group_by = request.args.get("group_by", "status")
    primary_filter = (
        request.args.get("priority_filter", "").split(",")
        if request.args.get("priority_filter", "")
        else []
    )
    entity_filter = (
        request.args.get("entity_filter", "").split(",")
        if request.args.get("entity_filter", "")
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
        "primary_filter": primary_filter,
        "entity_filter": entity_filter,
        "today": date.today(),
    }


def get_filtered_tasks_context():
    """Server-side filtering and sorting for HTMX endpoints - DRY version"""
    return task_filter_manager.get_filtered_context(
        custom_filters=task_custom_filters,
        custom_sorting=task_custom_sorting,
        custom_grouper=task_custom_groupers
    )




@tasks_bp.route("/content")
def content():
    """HTMX endpoint for filtered task content - DRY version"""
    context = task_filter_manager.get_content_context(
        custom_filters=task_custom_filters,
        custom_sorting=task_custom_sorting,
        custom_grouper=task_custom_groupers
    )
    
    return render_template("shared/entity_content.html", **context)


@tasks_bp.route("/")
def index():
    from app.utils.index_helpers import UniversalIndexHelper
    
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

    # Custom entity stats for tasks
    all_tasks = context["all_tasks"]
    entity_stats = {
        'title': 'Task Summary',
        'stats': [
            {
                'value': len([t for t in all_tasks if t.status == 'todo']),
                'label': 'To Do',
                'color_class': 'text-blue-600'
            },
            {
                'value': len([t for t in all_tasks if t.status == 'in-progress']),
                'label': 'In Progress',
                'color_class': 'text-yellow-600'
            },
            {
                'value': len([t for t in all_tasks if t.status == 'complete']),
                'label': 'Complete',
                'color_class': 'text-green-600'
            },
            {
                'value': len([t for t in all_tasks if hasattr(t, 'is_overdue') and t.is_overdue]),
                'label': 'Overdue',
                'color_class': 'text-red-600'
            }
        ]
    }

    # Get standardized context using universal helper, preserving existing params from context
    base_context = UniversalIndexHelper.get_standardized_index_context(
        entity_name='tasks',
        default_group_by=context.get("group_by", "status"),
        default_sort_by=context.get("sort_by", "due_date"),
        additional_context={
            'entity_stats': entity_stats,
            'tasks': tasks,
            'tasks_objects': context["all_tasks"],
        }
    )
    
    # Add custom entity filter for tasks
    ENTITY_TYPES = [
        {'value': 'company', 'label': Company.__name__},
        {'value': 'contact', 'label': 'Contact'},  # Legacy name for Stakeholder
        {'value': 'opportunity', 'label': Opportunity.__name__}
    ]
    base_context['dropdown_configs']['entity_filter'] = {
        'button_text': 'All Entities',
        'options': ENTITY_TYPES,
        'current_values': context["entity_filter"],
        'name': 'entity_filter'
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
