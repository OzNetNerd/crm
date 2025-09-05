from flask import Blueprint, request, jsonify
from app.models import db, Task, Contact, Company, Opportunity, Note

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/tasks/<int:task_id>')
def get_task_details(task_id):
    """Get task details with notes"""
    try:
        task = Task.query.get_or_404(task_id)
        notes = Note.query.filter_by(
            entity_type='task',
            entity_id=task_id
        ).order_by(Note.created_at.desc()).all()
        
        return jsonify({
            'id': task.id,
            'description': task.description,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'priority': task.priority,
            'status': task.status,
            'next_step_type': task.next_step_type,
            'entity_type': task.entity_type,
            'entity_id': task.entity_id,
            'entity_name': task.entity_name,
            'company_name': task.company_name,
            'opportunity_name': task.opportunity_name,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'is_overdue': task.is_overdue,
            'notes': [{
                'id': note.id,
                'content': note.content,
                'is_internal': note.is_internal,
                'created_at': note.created_at.isoformat()
            } for note in notes]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/contacts/<int:contact_id>')
def get_contact_details(contact_id):
    """Get contact details with notes"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        notes = Note.query.filter_by(
            entity_type='contact',
            entity_id=contact_id
        ).order_by(Note.created_at.desc()).all()
        
        return jsonify({
            'id': contact.id,
            'name': contact.name,
            'role': contact.role,
            'email': contact.email,
            'phone': contact.phone,
            'company_id': contact.company_id,
            'company_name': contact.company.name if contact.company else None,
            'opportunities': [{
                'id': opp.id,
                'name': opp.name,
                'value': float(opp.value) if opp.value else None,
                'stage': opp.stage
            } for opp in contact.opportunities],
            'notes': [{
                'id': note.id,
                'content': note.content,
                'is_internal': note.is_internal,
                'created_at': note.created_at.isoformat()
            } for note in notes]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/companies/<int:company_id>')
def get_company_details(company_id):
    """Get company details with notes"""
    try:
        company = Company.query.get_or_404(company_id)
        notes = Note.query.filter_by(
            entity_type='company',
            entity_id=company_id
        ).order_by(Note.created_at.desc()).all()
        
        return jsonify({
            'id': company.id,
            'name': company.name,
            'industry': company.industry,
            'website': company.website,
            'contacts': [{
                'id': contact.id,
                'name': contact.name,
                'role': contact.role,
                'email': contact.email
            } for contact in company.contacts],
            'opportunities': [{
                'id': opp.id,
                'name': opp.name,
                'value': float(opp.value) if opp.value else None,
                'stage': opp.stage,
                'probability': opp.probability
            } for opp in company.opportunities],
            'notes': [{
                'id': note.id,
                'content': note.content,
                'is_internal': note.is_internal,
                'created_at': note.created_at.isoformat()
            } for note in notes]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/opportunities/<int:opportunity_id>')
def get_opportunity_details(opportunity_id):
    """Get opportunity details with notes"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        notes = Note.query.filter_by(
            entity_type='opportunity',
            entity_id=opportunity_id
        ).order_by(Note.created_at.desc()).all()
        
        return jsonify({
            'id': opportunity.id,
            'name': opportunity.name,
            'value': float(opportunity.value) if opportunity.value else None,
            'probability': opportunity.probability,
            'expected_close_date': opportunity.expected_close_date.isoformat() if opportunity.expected_close_date else None,
            'stage': opportunity.stage,
            'company_id': opportunity.company_id,
            'company_name': opportunity.company.name if opportunity.company else None,
            'deal_age': opportunity.deal_age,
            'created_at': opportunity.created_at.isoformat(),
            'contacts': [{
                'id': contact.id,
                'name': contact.name,
                'role': contact.role,
                'email': contact.email
            } for contact in opportunity.contacts],
            'notes': [{
                'id': note.id,
                'content': note.content,
                'is_internal': note.is_internal,
                'created_at': note.created_at.isoformat()
            } for note in notes]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task details"""
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        
        if 'description' in data:
            task.description = data['description']
        if 'due_date' in data:
            task.due_date = data['due_date']
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
        if 'next_step_type' in data:
            task.next_step_type = data['next_step_type']
        
        db.session.commit()
        
        return jsonify({
            'id': task.id,
            'description': task.description,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'priority': task.priority,
            'status': task.status,
            'next_step_type': task.next_step_type
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update contact details"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        data = request.get_json()
        
        if 'name' in data:
            contact.name = data['name']
        if 'role' in data:
            contact.role = data['role']
        if 'email' in data:
            contact.email = data['email']
        if 'phone' in data:
            contact.phone = data['phone']
        
        db.session.commit()
        
        return jsonify({
            'id': contact.id,
            'name': contact.name,
            'role': contact.role,
            'email': contact.email,
            'phone': contact.phone
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    """Update company details"""
    try:
        company = Company.query.get_or_404(company_id)
        data = request.get_json()
        
        if 'name' in data:
            company.name = data['name']
        if 'industry' in data:
            company.industry = data['industry']
        if 'website' in data:
            company.website = data['website']
        
        db.session.commit()
        
        return jsonify({
            'id': company.id,
            'name': company.name,
            'industry': company.industry,
            'website': company.website
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/opportunities/<int:opportunity_id>', methods=['PUT'])
def update_opportunity(opportunity_id):
    """Update opportunity details"""
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        data = request.get_json()
        
        if 'name' in data:
            opportunity.name = data['name']
        if 'value' in data:
            opportunity.value = data['value']
        if 'probability' in data:
            opportunity.probability = data['probability']
        if 'expected_close_date' in data:
            opportunity.expected_close_date = data['expected_close_date']
        if 'stage' in data:
            opportunity.stage = data['stage']
        
        db.session.commit()
        
        return jsonify({
            'id': opportunity.id,
            'name': opportunity.name,
            'value': float(opportunity.value) if opportunity.value else None,
            'probability': opportunity.probability,
            'expected_close_date': opportunity.expected_close_date.isoformat() if opportunity.expected_close_date else None,
            'stage': opportunity.stage
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500