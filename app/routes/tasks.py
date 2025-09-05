from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Task, Company, Contact, Opportunity

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
            entity_id=data.get('entity_id')
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