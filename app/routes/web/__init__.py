from .dashboard import dashboard_bp
from .entities import entities_web_bp
from .tasks import tasks_bp
from .modals import modals_bp
from .search import search_bp


def register_web_blueprints(app):
    """Register all web blueprints"""
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(entities_web_bp, url_prefix="/")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(modals_bp)
    app.register_blueprint(search_bp, url_prefix="/")
