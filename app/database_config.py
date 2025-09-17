"""
Database configuration module.

Handles database URL generation and git worktree detection
using modern Python patterns and standard libraries.
"""

import os
from pathlib import Path
from typing import Optional


class DatabaseConfig:
    """
    Database configuration handler.

    This class manages database URL generation with support for:
    - Git worktrees
    - Environment variable overrides
    - Consistent database location across worktrees
    """

    @classmethod
    def get_default_database_url(cls) -> str:
        """
        Get the default database URL for SQLite.

        Returns database URL with proper path handling for:
        - Regular git repositories
        - Git worktrees (shared database)
        - Non-git directories

        Returns:
            SQLite database URL string
        """
        # Check for environment override first
        if db_url := os.getenv("DATABASE_URL"):
            return db_url

        # Find the main repository root
        repo_root = cls._find_repository_root()
        if not repo_root:
            # Fallback to current directory if not in a git repo
            repo_root = Path.cwd()

        # Ensure instance directory exists
        instance_dir = repo_root / "instance"
        instance_dir.mkdir(parents=True, exist_ok=True)

        # Return SQLite URL
        db_path = instance_dir / "crm.db"
        return f"sqlite:///{db_path}"

    @classmethod
    def _find_repository_root(cls) -> Optional[Path]:
        """
        Find the root of the git repository.

        Handles both regular repositories and worktrees by finding
        the main repository root, ensuring consistent database location.

        Returns:
            Path to repository root or None if not in a git repository
        """
        current = Path.cwd()

        # Walk up the directory tree looking for .git
        while current != current.parent:
            git_path = current / ".git"

            if not git_path.exists():
                current = current.parent
                continue

            if git_path.is_dir():
                # Regular git repository
                return current

            if git_path.is_file():
                # Git worktree - read the gitdir reference
                try:
                    return cls._resolve_worktree_root(git_path)
                except (OSError, ValueError):
                    # If we can't resolve, treat as non-git
                    return None

            current = current.parent

        return None

    @classmethod
    def _resolve_worktree_root(cls, git_file: Path) -> Path:
        """
        Resolve the main repository root from a worktree .git file.

        Args:
            git_file: Path to the .git file in a worktree

        Returns:
            Path to the main repository root

        Raises:
            ValueError: If the .git file format is invalid
        """
        content = git_file.read_text().strip()

        if not content.startswith("gitdir: "):
            raise ValueError(f"Invalid .git file format: {git_file}")

        # Extract gitdir path
        gitdir = content[8:]  # Remove "gitdir: " prefix
        git_dir = Path(gitdir)

        # The gitdir points to .git/worktrees/<branch>
        # We need to go up three levels to get the main repo root
        if "worktrees" in git_dir.parts:
            # Navigate: .git/worktrees/branch -> .git -> repo_root
            return git_dir.parent.parent.parent

        # If it's not a worktree path, return the parent of .git
        return git_dir.parent

    @classmethod
    def get_database_info(cls) -> dict:
        """
        Get database configuration information for debugging.

        Returns:
            Dictionary with database configuration details
        """
        db_url = cls.get_default_database_url()
        repo_root = cls._find_repository_root()

        return {
            "database_url": db_url,
            "repository_root": str(repo_root) if repo_root else None,
            "current_directory": str(Path.cwd()),
            "is_worktree": (
                (Path.cwd() / ".git").is_file()
                if (Path.cwd() / ".git").exists()
                else False
            ),
            "environment_override": bool(os.getenv("DATABASE_URL")),
        }
