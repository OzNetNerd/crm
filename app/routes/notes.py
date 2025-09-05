from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import db, Note

notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')


@notes_bp.route('/', methods=['POST'])
def create_note():
    """Create a new note for an entity"""
    try:
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({'error': 'Note content is required'}), 400
        
        if not data.get('entity_type') or not data.get('entity_id'):
            return jsonify({'error': 'Entity type and ID are required'}), 400
        
        note = Note(
            content=data['content'],
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
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


@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update an existing note"""
    try:
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({'error': 'Note content is required'}), 400
        
        note.content = data['content']
        note.is_internal = data.get('is_internal', note.is_internal)
        
        db.session.commit()
        
        return jsonify({
            'id': note.id,
            'content': note.content,
            'entity_type': note.entity_type,
            'entity_id': note.entity_id,
            'is_internal': note.is_internal,
            'created_at': note.created_at.isoformat(),
            'entity_name': note.entity_name
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note"""
    try:
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({'message': 'Note deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notes_bp.route('/entity/<string:entity_type>/<int:entity_id>')
def get_entity_notes(entity_type, entity_id):
    """Get all notes for a specific entity"""
    try:
        notes = Note.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
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