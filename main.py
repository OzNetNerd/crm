from pathlib import Path
from flask import Flask
from app.models import db
from app.routes.dashboard import dashboard_bp
from app.routes.companies import companies_bp
from app.routes.contacts import contacts_bp
from app.routes.opportunities import opportunities_bp
from app.routes.tasks import tasks_bp
from app.routes.search import search_bp
from app.routes.api import api_bp
from app.routes.notes import notes_bp


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
                    print(f"DEBUG: Worktree detected, using main repo database: {db_path}")
                    return db_path
            else:
                # Regular git repo
                db_path = f"sqlite:///{current}/instance/crm.db"
                print(f"DEBUG: Using database path: {db_path}")
                return db_path
        current = current.parent
    fallback = "sqlite:///crm.db"
    print(f"DEBUG: Using fallback database path: {fallback}")
    return fallback


def create_app():
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_path()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(companies_bp, url_prefix="/companies")
    app.register_blueprint(contacts_bp, url_prefix="/contacts")
    app.register_blueprint(opportunities_bp, url_prefix="/opportunities")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(search_bp, url_prefix="/")
    app.register_blueprint(api_bp)
    app.register_blueprint(notes_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5001)
