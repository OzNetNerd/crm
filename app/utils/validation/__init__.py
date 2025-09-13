"""
Validation utilities for legacy code detection and compliance enforcement.
"""

from .template_validator import (
    TemplateValidator,
    enforce_template_compliance,
    check_template_directory,
    get_compliance_report
)

__all__ = [
    "TemplateValidator",
    "enforce_template_compliance", 
    "check_template_directory",
    "get_compliance_report"
]