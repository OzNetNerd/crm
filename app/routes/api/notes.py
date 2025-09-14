from flask import Blueprint, request, jsonify
from app.models import db, Note

api_notes_bp = Blueprint("api_notes", __name__, url_prefix="/api")

@api_notes_bp.route("/<entity_type>/<int:entity_id>/notes")
def get_notes(entity_type, entity_id):
    """Get notes for any entity type"""
    notes = Note.query.filter_by(
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by(Note.created_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])

@api_notes_bp.route("/<entity_type>/<int:entity_id>/notes", methods=["POST"])
def create_note(entity_type, entity_id):
    """Create note for any entity type"""
    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({'error': 'Content required'}), 400

    try:
        note = Note(
            content=data['content'],
            entity_type=entity_type,
            entity_id=entity_id,
            is_internal=data.get('is_internal', True)
        )
        db.session.add(note)
        db.session.commit()
        return jsonify(note.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400