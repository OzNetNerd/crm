import argparse
import sys
import os
from pathlib import Path
from flask import Flask

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.models import db
from app.routes.api import register_api_blueprints
from app.routes.web import register_web_blueprints
from app.utils.template_utils import badge_class, get_dashboard_action_buttons
from app import config


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Apply configuration
    app.config.update(
        {
            "SECRET_KEY": config.SECRET_KEY,
            "SQLALCHEMY_DATABASE_URI": config.SQLALCHEMY_DATABASE_URI,
            "SQLALCHEMY_TRACK_MODIFICATIONS": config.SQLALCHEMY_TRACK_MODIFICATIONS,
        }
    )

    # Global configuration
    app.url_map.strict_slashes = False
    app.jinja_env.add_extension("jinja2.ext.do")

    # Template globals and filters
    def entity_url(entity, entity_type, action):
        """Generate URLs for entity operations (view, edit, delete)."""
        if action in ["view", "edit", "delete"]:
            return f"/modals/{entity_type}/{entity.id}/{action}"
        elif action == "create":
            return f"/modals/{entity_type}/create"
        raise ValueError(f"Unknown action: {action}")

    app.jinja_env.globals.update(
        {
            "get_dashboard_action_buttons": get_dashboard_action_buttons,
            "entity_url": entity_url,
            "getattr": getattr,
            "hasattr": hasattr,
        }
    )
    app.jinja_env.filters["badge_class"] = badge_class

    # Basic logging
    if os.environ.get("WERKZEUG_RUN_MAIN"):
        app.logger.info("CRM Application startup")

    # Initialize database
    db.init_app(app)

    # Register blueprints
    register_api_blueprints(app)
    register_web_blueprints(app)

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the CRM Flask application")
    parser.add_argument(
        "--port", type=int, required=True, help="Port number to run the application on"
    )
    args = parser.parse_args()

    app = create_app()

    try:
        app.run(debug=True, port=args.port, use_reloader=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {args.port} is already in use!")
            print("💡 Use ./run.sh to auto-detect a free port")
        else:
            raise
