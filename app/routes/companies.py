from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Company

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


