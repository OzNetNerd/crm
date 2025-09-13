"""
Exception classes for legacy code detection and enforcement.
"""

from .legacy_exceptions import (
    LegacyCodeError,
    TemplateModernizationError,
    LegacySQLError,
    ConfigurationLegacyError,
    FormDefinitionError,
    RouteHandlerLegacyError
)

__all__ = [
    "LegacyCodeError",
    "TemplateModernizationError", 
    "LegacySQLError",
    "ConfigurationLegacyError",
    "FormDefinitionError",
    "RouteHandlerLegacyError"
]