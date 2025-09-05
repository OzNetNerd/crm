from flask import Blueprint, request, jsonify
from app.models import db, Company, Contact, Opportunity, Note

api_notes_bp = Blueprint('api_notes', __name__, url_prefix='/api')


@api_notes_bp.route('/companies/<int:company_id>/notes', methods=['GET'])
def get_company_notes(company_id):
    """Get all notes for a specific company"""
    try:
        # Verify company exists
        company = Company.query.get_or_404(company_id)
        
        notes = Note.query.filter_by(
            entity_type='company',
            entity_id=company_id
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


@api_notes_bp.route('/companies/<int:company_id>/notes', methods=['POST'])
def create_company_note(company_id):
    """Create a new note for a specific company"""
    try:
        # Verify company exists
        company = Company.query.get_or_404(company_id)
        
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'error': 'Note content is required'}), 400
        
        note = Note(
            content=data['content'],
            entity_type='company',
            entity_id=company_id,
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


@api_notes_bp.route('/contacts/<int:contact_id>/notes', methods=['GET'])
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


@api_notes_bp.route('/contacts/<int:contact_id>/notes', methods=['POST'])
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


@api_notes_bp.route('/opportunities/<int:opportunity_id>/notes', methods=['GET'])
def get_opportunity_notes(opportunity_id):
    """Get all notes for a specific opportunity"""
    try:
        # Verify opportunity exists
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        
        notes = Note.query.filter_by(
            entity_type='opportunity',
            entity_id=opportunity_id
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


@api_notes_bp.route('/opportunities/<int:opportunity_id>/notes', methods=['POST'])
def create_opportunity_note(opportunity_id):
    """Create a new note for a specific opportunity"""
    try:
        # Verify opportunity exists
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'error': 'Note content is required'}), 400
        
        note = Note(
            content=data['content'],
            entity_type='opportunity',
            entity_id=opportunity_id,
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