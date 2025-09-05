from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify
from app.models import db, Task, Company, Contact, Opportunity

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    tasks = Task.query.filter(Task.status != 'complete').order_by(Task.due_date.asc()).all()
    
    # Group tasks by sections
    today = date.today()
    
    sections = {
        'overdue': [t for t in tasks if t.is_overdue],
        'today': [t for t in tasks if t.due_date == today and not t.is_overdue],
        'this_week': [t for t in tasks if t.due_date and t.due_date > today and 
                     (t.due_date - today).days <= 7],
        'next_week': [t for t in tasks if t.due_date and 
                     (t.due_date - today).days > 7 and (t.due_date - today).days <= 14],
        'completed_today': Task.query.filter(
            Task.status == 'complete',
            Task.completed_at >= datetime.combine(today, datetime.min.time())
        ).all()
    }
    
    return render_template('dashboard/index.html', sections=sections)


@dashboard_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.status = 'complete'
    task.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Task completed'})


@dashboard_bp.route('/tasks/<int:task_id>/update', methods=['POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'description' in data:
        task.description = data['description']
    if 'due_date' in data:
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    if 'priority' in data:
        task.priority = data['priority']
    
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Task updated'})


@dashboard_bp.route('/tasks/<int:task_id>/reschedule', methods=['POST'])
def reschedule_task(task_id):
    from datetime import timedelta
    
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    days = data.get('days', 1)
    
    if task.due_date:
        task.due_date = task.due_date + timedelta(days=days)
    else:
        task.due_date = date.today() + timedelta(days=days)
    
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': f'Task rescheduled by {days} days'})