import argparse
import socket
from pathlib import Path
from flask import Flask
from app.models import db
from app.routes.dashboard import dashboard_bp
from app.routes.companies import companies_bp
from app.routes.contacts import contacts_bp
from app.routes.opportunities import opportunities_bp
from app.routes.tasks import tasks_bp
from app.routes.tasks_api import tasks_api_bp
from app.routes.search import search_bp
from app.routes.api import api_bp
from app.routes.api_notes import api_notes_bp
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
    app.register_blueprint(tasks_api_bp, url_prefix="/api/tasks")
    app.register_blueprint(search_bp, url_prefix="/")
    app.register_blueprint(api_bp)
    app.register_blueprint(api_notes_bp)
    app.register_blueprint(notes_bp)

    with app.app_context():
        db.create_all()

    return app


def find_free_port(start_port=5000, max_attempts=10):
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free port found in range {start_port}-{start_port + max_attempts - 1}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the CRM Flask application')
    parser.add_argument('--port', type=int, help='Port number to run the application on (auto-detects if not specified)')
    args = parser.parse_args()
    
    app = create_app()
    
    if args.port:
        # Use specified port
        port = args.port
        try:
            app.run(debug=True, port=port)
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"\n❌ Error: Port {port} is already in use!")
                print(f"💡 Try running without --port to auto-detect a free port")
            else:
                raise
    else:
        # Auto-detect free port
        port = find_free_port()
        print(f"🚀 Starting CRM application on http://127.0.0.1:{port}")
        print(f"📝 Claude Code: Use this URL to access the application")
        app.run(debug=True, port=port)
