"""Custom exceptions - fail loudly with clear messages."""


class CRMException(Exception):
    """Base exception for CRM application."""

    pass


class ValidationError(CRMException):
    """Raised when validation fails."""

    pass


class NotFoundError(CRMException):
    """Raised when entity not found."""

    pass


class DuplicateError(CRMException):
    """Raised when duplicate entity detected."""

    pass


class InvalidStateError(CRMException):
    """Raised when operation invalid for current state."""

    pass


class DatabaseError(CRMException):
    """Raised when database operation fails."""

    pass


class ConfigurationError(CRMException):
    """Raised when configuration is invalid."""

    pass


class AuthenticationError(CRMException):
    """Raised when authentication fails."""

    pass


class AuthorizationError(CRMException):
    """Raised when authorization fails."""

    pass
