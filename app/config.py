"""
Application configuration module following best practices.

This module centralizes all configuration, using environment variables
with sensible defaults. Follows the principle of failing loudly for
critical configuration errors.
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Environment(Enum):
    """Application environment enumeration."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass(frozen=True)
class Config:
    """
    Application configuration using dataclass for immutability.

    All configuration is loaded from environment variables with
    appropriate defaults for development. Production values must
    be explicitly set via environment variables.
    """

    # Core application settings
    environment: Environment
    debug: bool
    testing: bool
    secret_key: str

    # Database configuration
    database_url: str
    track_modifications: bool

    # Server configuration
    host: str
    port: int

    # Paths
    instance_path: Path
    template_folder: Path
    static_folder: Path

    @classmethod
    def from_environment(cls) -> "Config":
        """
        Create configuration from environment variables.

        Raises:
            ValueError: If required production configuration is missing.
        """
        env_str = os.getenv("FLASK_ENV", "development").lower()

        try:
            environment = Environment(env_str)
        except ValueError:
            raise ValueError(
                f"Invalid FLASK_ENV: {env_str}. "
                f"Must be one of: {[e.value for e in Environment]}"
            )

        is_production = environment == Environment.PRODUCTION
        is_testing = environment == Environment.TESTING

        # Secret key MUST be set in production
        secret_key = os.getenv("SECRET_KEY")
        if is_production and not secret_key:
            raise ValueError(
                "SECRET_KEY must be set in production environment. "
                "Generate with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )

        if not secret_key:
            # Development only - generate deterministic key for consistency
            import hashlib

            secret_key = hashlib.sha256(
                b"development-key-do-not-use-in-production"
            ).hexdigest()

        # Database URL with environment-specific defaults
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            if is_testing:
                database_url = "sqlite:///:memory:"
            else:
                from .database_config import DatabaseConfig

                database_url = DatabaseConfig.get_default_database_url()

        # Server configuration
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "5000"))

        # Path configuration
        app_root = Path(__file__).parent
        instance_path = Path(os.getenv("INSTANCE_PATH", app_root.parent / "instance"))

        return cls(
            environment=environment,
            debug=not is_production and os.getenv("DEBUG", "true").lower() == "true",
            testing=is_testing,
            secret_key=secret_key,
            database_url=database_url,
            track_modifications=False,  # Never track modifications (deprecated feature)
            host=host,
            port=port,
            instance_path=instance_path,
            template_folder=app_root / "templates",
            static_folder=app_root / "static",
        )

    def apply_to_flask(self, app) -> None:
        """
        Apply configuration to Flask application.

        Args:
            app: Flask application instance
        """
        app.config["SECRET_KEY"] = self.secret_key
        app.config["SQLALCHEMY_DATABASE_URI"] = self.database_url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = self.track_modifications
        app.config["DEBUG"] = self.debug
        app.config["TESTING"] = self.testing

        # Ensure instance directory exists
        self.instance_path.mkdir(parents=True, exist_ok=True)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING


# Global configuration instance (created once at import)
config = Config.from_environment()
