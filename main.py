import argparse
from pathlib import Path
from flask import Flask
from app.models import db
from app.routes.api import register_api_blueprints
from app.routes.web import register_web_blueprints
from app.utils.template_filters import register_template_filters
from app.models import Company, Stakeholder, Task, Opportunity, User
from app.utils.template_globals import (
    get_field_options,
    get_sortable_fields,
    get_groupable_fields,
    get_model_form_fields,
    get_model_config,
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
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
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
    from app.context_processors import inject_model_configs
    app.context_processor(inject_model_configs)

    # Register clean template functions - no more string hacks!
    app.jinja_env.globals["get_field_options"] = get_field_options
    app.jinja_env.globals["get_sortable_fields"] = get_sortable_fields
    app.jinja_env.globals["get_groupable_fields"] = get_groupable_fields
    app.jinja_env.globals["get_model_form_fields"] = get_model_form_fields
    app.jinja_env.globals["get_model_config"] = get_model_config
    app.jinja_env.globals["PRIORITY_OPTIONS"] = PRIORITY_OPTIONS
    app.jinja_env.globals["SIZE_OPTIONS"] = SIZE_OPTIONS

    # Make model classes available to templates
    app.jinja_env.globals["Company"] = Company
    app.jinja_env.globals["Stakeholder"] = Stakeholder
    app.jinja_env.globals["Task"] = Task
    app.jinja_env.globals["Opportunity"] = Opportunity
    app.jinja_env.globals["User"] = User

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
