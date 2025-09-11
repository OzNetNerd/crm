from .core import api_core_bp
from .entities import api_entities_bp
from .notes import api_notes_bp
from .tasks import tasks_api_bp

def register_api_blueprints(app):
    """Register all API blueprints"""
    app.register_blueprint(api_core_bp)
    app.register_blueprint(api_entities_bp)
    app.register_blueprint(api_notes_bp)
    app.register_blueprint(tasks_api_bp)