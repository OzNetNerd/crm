import argparse
import sys
from pathlib import Path
from flask import Flask

# Add project root to Python path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.models import db
from app.routes.api import register_api_blueprints
from app.routes.web import register_web_blueprints
from app.utils.ui.template_filters import register_template_filters
from app.models import Company, Stakeholder, Task, Opportunity, User
from app.utils.ui.template_globals import (
    get_field_options,
    get_model_form_fields,
    get_model_config,
    # get_create_modal_config,  # Removed - using WTForms modal system now
    # get_detail_modal_config,  # Removed - using WTForms modal system now
    # get_all_modal_configs,  # Removed - using WTForms modal system now
    # get_all_detail_modal_configs,  # Removed - using WTForms modal system now
    PRIORITY_OPTIONS,
    SIZE_OPTIONS,
)


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
                    print(f"DEBUG: gitdir = {gitdir}")
                    # Get main repo root from worktree gitdir
                    # gitdir points to /path/to/repo/.git/worktrees/branch
                    # we need /path/to/repo
                    git_dir = Path(gitdir)  # /home/will/code/crm/.git/worktrees/text
                    print(f"DEBUG: git_dir = {git_dir}")
                    main_repo_root = git_dir.parent.parent.parent  # /home/will/code/crm
                    print(f"DEBUG: main_repo_root = {main_repo_root}")
                    db_path = f"sqlite:///{main_repo_root}/instance/crm.db"
                    print(
                        f"DEBUG: Worktree detected, using main repo database: {db_path}"
                    )
                    return db_path
            else:
                # Regular git repo
                db_path = f"sqlite:///{current}/instance/crm.db"
                print(f"DEBUG: Using database path: {db_path}")
                return db_path
        current = current.parent

    # No git repository found - this is a configuration error
    raise RuntimeError(
        "No git repository found. The application must be run from within a git repository. "
        "This ensures proper database path detection and prevents configuration issues."
    )


def create_app():
    app = Flask(__name__, template_folder="../../app/templates", static_folder="../../app/static")
    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_path()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Register API and web blueprints
    register_api_blueprints(app)
    register_web_blueprints(app)

    # Register custom template filters
    register_template_filters(app)
    
    # Register context processors for global template data
    # Context processor removed - model configs accessed directly via get_all_model_configs() where needed

    # Register clean template functions - no more string hacks!
    app.jinja_env.globals["get_field_options"] = get_field_options
    app.jinja_env.globals["get_model_form_fields"] = get_model_form_fields
    app.jinja_env.globals["get_model_config"] = get_model_config
    # app.jinja_env.globals["get_create_modal_config"] = get_create_modal_config  # Removed
    # app.jinja_env.globals["get_detail_modal_config"] = get_detail_modal_config  # Removed
    # app.jinja_env.globals["get_all_modal_configs"] = get_all_modal_configs  # Removed
    # app.jinja_env.globals["get_all_detail_modal_configs"] = get_all_detail_modal_configs  # Removed
    # Dashboard buttons now generated in templates using Jinja macros
    app.jinja_env.globals["PRIORITY_OPTIONS"] = PRIORITY_OPTIONS
    app.jinja_env.globals["SIZE_OPTIONS"] = SIZE_OPTIONS
    
    
    # Modal configs removed - using WTForms modal system now (keeping main branch approach)
    # from app.utils.ui.modal_configs import MODAL_CONFIGS
    # from app.utils.ui.modal_configs import DETAIL_MODAL_CONFIGS
    # app.jinja_env.globals["modal_configs"] = MODAL_CONFIGS
    # app.jinja_env.globals["detail_modal_configs"] = DETAIL_MODAL_CONFIGS

    # Model class globals removed - use get_all_model_configs() for model metadata

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
        app.run(debug=True, port=args.port)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {args.port} is already in use!")
            print("💡 Use ./run.sh to auto-detect a free port")
        else:
            raise
