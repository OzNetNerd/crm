"""Simple application configuration - no over-engineering."""

import os
from pathlib import Path


def get_database_url():
    """Get database URL - environment override or git-aware default."""
    if db_url := os.environ.get("DATABASE_URL"):
        return db_url

    # Find git root for database placement
    current = Path.cwd()
    while current != current.parent:
        git_path = current / ".git"
        if git_path.exists():
            # Handle worktree vs regular repo
            if git_path.is_file() and (
                content := git_path.read_text().strip()
            ).startswith("gitdir: "):
                # Worktree: extract main repo path
                git_dir = Path(content[8:])
                main_repo_root = git_dir.parent.parent.parent
                return f"sqlite:///{main_repo_root}/instance/crm.db"
            # Regular repo
            return f"sqlite:///{current}/instance/crm.db"
        current = current.parent

    # Fallback
    return f"sqlite:///{Path.cwd()}/instance/crm.db"


def get_log_level():
    """Get logging level from environment with sensible default."""
    return os.environ.get("LOG_LEVEL", "INFO").upper()


def get_log_file():
    """Get log file path from environment, None for stdout."""
    log_file = os.environ.get("LOG_FILE")
    if log_file:
        return Path(log_file)
    return None


# Simple configuration - just what we need
SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
SQLALCHEMY_DATABASE_URI = get_database_url()
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Logging configuration
LOG_LEVEL = get_log_level()
LOG_FILE = get_log_file()

# Development vs Production settings
DEBUG = os.environ.get("FLASK_ENV") == "development"
TESTING = os.environ.get("TESTING", "false").lower() == "true"
