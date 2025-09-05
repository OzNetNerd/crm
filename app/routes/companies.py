from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Company, Contact, Opportunity, Note

companies_bp = Blueprint('companies', __name__)


@companies_bp.route('/')
def index():
    companies = Company.query.all()
    return render_template('companies/index.html', companies=companies)


@companies_bp.route('/<int:company_id>')
def detail(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('companies/detail.html', company=company)


@companies_bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        company = Company(
            name=data['name'],
            industry=data.get('industry'),
            website=data.get('website')
        )
        
        db.session.add(company)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'status': 'success', 'company_id': company.id})
        else:
            return redirect(url_for('companies.detail', company_id=company.id))
    
    return render_template('companies/new.html')


@companies_bp.route('/<int:company_id>/notes', methods=['GET'])
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


@companies_bp.route('/<int:company_id>/notes', methods=['POST'])
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