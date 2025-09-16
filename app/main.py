import argparse
import sys
import os
import logging
from pathlib import Path
from flask import Flask

# Add project root to Python path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.models import db
from app.routes.api import register_api_blueprints
from app.routes.web import register_web_blueprints
# Models are imported via app.models - no registration needed


def badge_class(value):
    """
    Convert a value to a badge-compatible CSS class.

    Rules:
    - Lowercase the value
    - Replace underscores with spaces
    - Replace hyphens with spaces
    """
    if not value:
        return ''
    return str(value).lower().replace('_', ' ').replace('-', ' ')


def get_database_path():
    """Get database path from environment or default location."""
    # Allow environment variable override
    if db_url := os.environ.get('DATABASE_URL'):
        return db_url

    # Default to local SQLite database in instance folder
    current = Path.cwd()
    # Look for existing instance directory or create in current dir
    while current != current.parent:
        git_path = current / ".git"
        if git_path.exists():
            if git_path.is_file():
                # Worktree: read gitdir from .git file
                gitdir_content = git_path.read_text().strip()
                if gitdir_content.startswith("gitdir: "):
                    gitdir = gitdir_content[8:]  # Remove "gitdir: " prefix
                    # gitdir points to /path/to/repo/.git/worktrees/branch
                    # we need /path/to/repo
                    git_dir = Path(gitdir)
                    main_repo_root = git_dir.parent.parent.parent
                    return f"sqlite:///{main_repo_root}/instance/crm.db"
            # Found regular git root
            return f"sqlite:///{current}/instance/crm.db"
        current = current.parent

    # Fallback to current directory
    return f"sqlite:///{Path.cwd()}/instance/crm.db"


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

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
        return ['companies', 'tasks', 'opportunities', 'stakeholders', 'teams']

    app.jinja_env.globals["get_dashboard_action_buttons"] = get_dashboard_action_buttons

    # Helper functions for templates
    app.jinja_env.globals["getattr"] = getattr
    app.jinja_env.globals["hasattr"] = hasattr

    # URL helper function for entities
    def entity_url(entity, entity_type, action='view'):
        """Generate modal URLs for entities."""
        urls = {
            'view': f'/modals/{entity_type}/view/{entity.id}',
            'edit': f'/modals/{entity_type}/{entity.id}/edit',
            'delete': f'/modals/{entity_type}/{entity.id}/delete',
            'create': f'/modals/{entity_type}/create'
        }
        return urls.get(action, '#')

    app.jinja_env.globals["entity_url"] = entity_url

    # Register custom Jinja2 filters
    app.jinja_env.filters["badge_class"] = badge_class


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