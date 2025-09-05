from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models import db
from app.routes.dashboard import dashboard_bp
from app.routes.companies import companies_bp
from app.routes.contacts import contacts_bp
from app.routes.opportunities import opportunities_bp
from app.routes.tasks import tasks_bp
from app.routes.search import search_bp

def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(companies_bp, url_prefix='/companies')
    app.register_blueprint(contacts_bp, url_prefix='/contacts')
    app.register_blueprint(opportunities_bp, url_prefix='/opportunities')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(search_bp, url_prefix='/')
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)