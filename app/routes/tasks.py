from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Task, Company, Contact, Opportunity
# Forms handled directly in routes without WTForms for now

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/')
def index():
    tasks = Task.query.order_by(Task.due_date.asc()).all()
    today = date.today()
    return render_template('tasks/index.html', tasks=tasks, today=today)


@tasks_bp.route('/<int:task_id>')
def detail(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('tasks/detail.html', task=task)


@tasks_bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        task = Task(
            description=data['description'],
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'todo'),
            next_step_type=data.get('next_step_type'),
            entity_type=data.get('entity_type'),
            entity_id=data.get('entity_id'),
            task_type=data.get('task_type', 'single'),
            parent_task_id=data.get('parent_task_id'),
            sequence_order=data.get('sequence_order', 0),
            dependency_type=data.get('dependency_type', 'parallel')
        )
        
        db.session.add(task)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'status': 'success', 'task_id': task.id})
        else:
            return redirect(url_for('tasks.detail', task_id=task.id))
    
    companies = Company.query.order_by(Company.name).all()
    contacts = Contact.query.order_by(Contact.name).all()
    opportunities = Opportunity.query.order_by(Opportunity.name).all()
    
    return render_template('tasks/new.html', 
                         companies=companies, 
                         contacts=contacts, 
                         opportunities=opportunities)


@tasks_bp.route('/multi/new', methods=['GET', 'POST'])
def new_multi():
    """Create a new Multi Task with child tasks"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Create parent task
        parent_task = Task(
            description=data['description'],
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            priority=data.get('priority', 'medium'),
            status='todo',
            entity_type=data.get('entity_type'),
            entity_id=data.get('entity_id'),
            task_type='parent',
            dependency_type=data.get('dependency_type', 'parallel')
        )
        
        db.session.add(parent_task)
        db.session.flush()  # Get the parent task ID
        
        # Create child tasks
        child_tasks_data = data.get('child_tasks', [])
        for i, child_data in enumerate(child_tasks_data):
            if child_data.get('description'):  # Only create if description exists
                child_task = Task(
                    description=child_data['description'],
                    due_date=datetime.strptime(child_data['due_date'], '%Y-%m-%d').date() if child_data.get('due_date') else None,
                    priority=child_data.get('priority', 'medium'),
                    status='todo',
                    next_step_type=child_data.get('next_step_type'),
                    entity_type=data.get('entity_type'),  # Inherit from parent
                    entity_id=data.get('entity_id'),      # Inherit from parent
                    task_type='child',
                    parent_task_id=parent_task.id,
                    sequence_order=i,
                    dependency_type=data.get('dependency_type', 'parallel')
                )
                db.session.add(child_task)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'status': 'success', 'task_id': parent_task.id})
        else:
            return redirect(url_for('tasks.detail', task_id=parent_task.id))
    
    companies = Company.query.order_by(Company.name).all()
    contacts = Contact.query.order_by(Contact.name).all()
    opportunities = Opportunity.query.order_by(Opportunity.name).all()
    
    return render_template('tasks/multi_new.html', 
                         companies=companies, 
                         contacts=contacts, 
                         opportunities=opportunities)


@tasks_bp.route('/parent-tasks', methods=['GET'])
def get_parent_tasks():
    """API endpoint to get available parent tasks for child task creation"""
    parent_tasks = Task.query.filter_by(task_type='parent').order_by(Task.created_at.desc()).all()
    
    return jsonify([
        {
            'id': task.id,
            'description': task.description,
            'priority': task.priority,
            'completion_percentage': task.completion_percentage
        }
        for task in parent_tasks
    ])

