from .dashboard import dashboard_bp
from .companies import companies_bp
from .stakeholders import stakeholders_bp
from .opportunities import opportunities_bp
from .tasks import tasks_bp
from .notes import notes_bp
from .teams import teams_bp
from .modals import modals_bp
from .search import search_bp

def register_web_blueprints(app):
    """Register all web blueprints"""
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(companies_bp, url_prefix="/companies")
    app.register_blueprint(stakeholders_bp, url_prefix="/stakeholders")
    app.register_blueprint(opportunities_bp, url_prefix="/opportunities")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(notes_bp)
    app.register_blueprint(teams_bp, url_prefix="/teams")
    app.register_blueprint(modals_bp)
    app.register_blueprint(search_bp, url_prefix="/")