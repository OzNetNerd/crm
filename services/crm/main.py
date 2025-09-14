import argparse
import sys
import os
import logging
from pathlib import Path
from flask import Flask

# Add project root to Python path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.models import db
from app.routes.api import register_api_blueprints
from app.routes.web import register_web_blueprints
# Models are imported via app.models - no registration needed
from app.utils.cards.config_builder import CardConfigBuilder


def get_database_path():
    """Find the git root directory and return database path."""
    current = Path.cwd()
    while current != current.parent:
        git_path = current / ".git"
        if git_path.exists():
            if git_path.is_file():
                # Worktree: read gitdir from .git file
                gitdir_content = git_path.read_text().strip()
                if gitdir_content.startswith("gitdir: "):
                    gitdir = gitdir_content[8:]  # Remove "gitdir: " prefix
                    # Get main repo root from worktree gitdir
                    # gitdir points to /path/to/repo/.git/worktrees/branch
                    # we need /path/to/repo
                    git_dir = Path(gitdir)  # /home/will/code/crm/.git/worktrees/text
                    main_repo_root = git_dir.parent.parent.parent  # /home/will/code/crm
                    db_path = f"sqlite:///{main_repo_root}/instance/crm.db"
                    return db_path
            else:
                # Regular git repo
                db_path = f"sqlite:///{current}/instance/crm.db"
                return db_path
        current = current.parent

    # No git repository found - this is a configuration error
    raise RuntimeError(
        "No git repository found. The application must be run from within a git repository. "
        "This ensures proper database path detection and prevents configuration issues."
    )


def create_app():
    app = Flask(__name__, template_folder="../../app/templates", static_folder="../../app/static")

    # Global trailing slash handling - DRY solution for all routes
    app.url_map.strict_slashes = False

    app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_path()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Basic logging setup
    if os.environ.get('WERKZEUG_RUN_MAIN'):
        app.logger.info('CRM Application startup')
        
    # Enable Jinja2 do extension for template logic
    app.jinja_env.add_extension('jinja2.ext.do')

    db.init_app(app)

    # Register API and web blueprints
    register_api_blueprints(app)
    register_web_blueprints(app)

    # Register context processors for global template data
    
    # Dashboard button function
    def get_dashboard_action_buttons():
        return ['companies', 'tasks', 'opportunities', 'stakeholders']

    # Model metadata function - DRY replacement for ModelRegistry
    def get_model_metadata(model_name):
        """Provide model metadata for templates"""
        metadata = {
            'company': {'display_name': 'Company', 'display_name_plural': 'Companies'},
            'stakeholder': {'display_name': 'Stakeholder', 'display_name_plural': 'Stakeholders'},
            'opportunity': {'display_name': 'Opportunity', 'display_name_plural': 'Opportunities'},
            'task': {'display_name': 'Task', 'display_name_plural': 'Tasks'},
            'user': {'display_name': 'User', 'display_name_plural': 'Users'},
            'note': {'display_name': 'Note', 'display_name_plural': 'Notes'},
        }

        class ModelMetadata:
            def __init__(self, data):
                self.display_name = data.get('display_name', model_name.title())
                self.display_name_plural = data.get('display_name_plural', model_name.title() + 's')

        return ModelMetadata(metadata.get(model_name.lower(), {}))

    app.jinja_env.globals["get_dashboard_action_buttons"] = get_dashboard_action_buttons
    
    # Dynamic card system
    app.jinja_env.globals["build_dynamic_card_config"] = CardConfigBuilder.build_card_config
    app.jinja_env.globals["get_model_metadata"] = get_model_metadata
    app.jinja_env.globals["getattr"] = getattr
    app.jinja_env.globals["hasattr"] = hasattr
    
    
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
        app.run(debug=os.environ.get('DEBUG', 'False').lower() == 'true', port=args.port)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {args.port} is already in use!")
            print("💡 Use ./run.sh to auto-detect a free port")
        else:
            raise
