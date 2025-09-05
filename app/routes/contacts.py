from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Contact, Company, Opportunity, Note

contacts_bp = Blueprint('contacts', __name__)


@contacts_bp.route('/')
def index():
    contacts = Contact.query.join(Company).order_by(Company.name, Contact.name).all()
    return render_template('contacts/index.html', contacts=contacts)


@contacts_bp.route('/<int:contact_id>')
def detail(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    return render_template('contacts/detail.html', contact=contact)


@contacts_bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        contact = Contact(
            name=data['name'],
            role=data.get('role'),
            email=data.get('email'),
            phone=data.get('phone'),
            company_id=data['company_id']
        )
        
        db.session.add(contact)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'status': 'success', 'contact_id': contact.id})
        else:
            return redirect(url_for('contacts.detail', contact_id=contact.id))
    
    companies = Company.query.order_by(Company.name).all()
    return render_template('contacts/new.html', companies=companies)


@contacts_bp.route('/<int:contact_id>/notes', methods=['GET'])
def get_contact_notes(contact_id):
    """Get all notes for a specific contact"""
    try:
        # Verify contact exists
        contact = Contact.query.get_or_404(contact_id)
        
        notes = Note.query.filter_by(
            entity_type='contact',
            entity_id=contact_id
        ).order_by(Note.created_at.desc()).all()
        
        return jsonify([{
            'id': note.id,
            'content': note.content,
            'entity_type': note.entity_type,
            'entity_id': note.entity_id,
            'is_internal': note.is_internal,
            'created_at': note.created_at.isoformat(),
            'entity_name': note.entity_name
        } for note in notes])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@contacts_bp.route('/<int:contact_id>/notes', methods=['POST'])
def create_contact_note(contact_id):
    """Create a new note for a specific contact"""
    try:
        # Verify contact exists
        contact = Contact.query.get_or_404(contact_id)
        
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'error': 'Note content is required'}), 400
        
        note = Note(
            content=data['content'],
            entity_type='contact',
            entity_id=contact_id,
            is_internal=data.get('is_internal', True)
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'id': note.id,
            'content': note.content,
            'entity_type': note.entity_type,
            'entity_id': note.entity_id,
            'is_internal': note.is_internal,
            'created_at': note.created_at.isoformat(),
            'entity_name': note.entity_name
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500