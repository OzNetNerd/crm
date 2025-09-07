from pathlib import Path


def get_database_path():
    """
    Find the git root directory and return database path.
    This function works for both the CRM Flask app and the chatbot FastAPI service.
    """
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
    
    # Fallback
    fallback = "sqlite:///crm.db"
    return fallback


# Database configuration constants
DATABASE_URI = get_database_path()
ASYNC_DATABASE_URI = DATABASE_URI.replace("sqlite://", "sqlite+aiosqlite://")

# For testing
if __name__ == "__main__":
    print(f"Database URI: {DATABASE_URI}")
    print(f"Async Database URI: {ASYNC_DATABASE_URI}")