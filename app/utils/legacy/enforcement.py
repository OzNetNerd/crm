"""
Legacy Code Enforcement System
ADR-010: Legacy Code Elimination Strategy with Loud Failure Enforcement

Implements zero-tolerance legacy code policy with aggressive loud failure patterns.
Detects and prevents usage of deprecated patterns with clear modernization guidance.
"""

import os
import inspect
from pathlib import Path
from typing import List, Dict, Optional
from functools import wraps


class LegacyCodeViolationError(Exception):
    """
    Exception raised when legacy code patterns are detected.
    ADR-010: Loud failure enforcement for legacy patterns.
    """
    
    def __init__(self, pattern: str, guidance: str, adr_reference: str, impact: str = None):
        self.pattern = pattern
        self.guidance = guidance
        self.adr_reference = adr_reference
        self.impact = impact
        
        message = f"""
🚨 LEGACY CODE DETECTED: {pattern}

REQUIRED ACTION: {guidance}

REFERENCE: {adr_reference} for detailed migration guidance

IMPACT: {impact or 'This legacy pattern violates architectural standards and must be modernized'}

ADR-010 ENFORCEMENT: Zero tolerance for legacy code patterns.
All changes must modernize legacy code - no compatibility layers allowed.
"""
        super().__init__(message)


class LegacyPatternDetector:
    """
    Detects legacy code patterns and enforces modernization.
    ADR-010: Comprehensive legacy pattern detection system.
    """
    
    @staticmethod
    def detect_raw_sql_usage(function_name: str, file_path: str = None):
        """
        Detect raw SQL usage instead of ORM relationships.
        ADR-003: SQLAlchemy ORM Relationship Refactoring
        """
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        
        raise LegacyCodeViolationError(
            pattern=f"Raw SQL usage in function '{function_name}'",
            guidance="Replace with ORM relationships (self.relationship_name)",
            adr_reference="ADR-003 (SQLAlchemy ORM Refactoring)",
            impact="Raw SQL bypasses ORM benefits and violates single source of truth"
        )
    
    @staticmethod
    def detect_javascript_in_templates(template_path: str):
        """
        Detect JavaScript embedded in Jinja2 templates.
        ADR-004: JavaScript Template Separation
        """
        raise LegacyCodeViolationError(
            pattern=f"JavaScript embedded in template '{template_path}'",
            guidance="Extract JavaScript to separate .js files in app/static/js/",
            adr_reference="ADR-004 (JavaScript Template Separation)",
            impact="Embedded JavaScript causes template syntax errors and poor separation of concerns"
        )
    
    @staticmethod
    def detect_itcss_architecture_usage(css_path: str):
        """
        Detect usage of old ITCSS architecture.
        ADR-011: Simple CSS Architecture
        """
        raise LegacyCodeViolationError(
            pattern=f"ITCSS architecture usage in '{css_path}'",
            guidance="Use flat CSS structure: variables.css, base.css, layout.css, components.css, entities.css, utilities.css",
            adr_reference="ADR-011 (Simple CSS Architecture)",
            impact="ITCSS creates unnecessary complexity and hinders maintainability"
        )
    
    @staticmethod
    def detect_manual_form_definitions(form_class_name: str):
        """
        Detect manual form definitions instead of dynamic generation.
        ADR-008: DRY Principle Implementation
        """
        raise LegacyCodeViolationError(
            pattern=f"Manual form definition '{form_class_name}'",
            guidance="Use DynamicFormBuilder.build_dynamic_form(Model, BaseForm)",
            adr_reference="ADR-008 (DRY Principle Implementation)",
            impact="Manual form definitions create code duplication and maintenance burden"
        )
    
    @staticmethod
    def detect_hardcoded_configuration(config_name: str, value: str):
        """
        Detect hardcoded configuration values.
        ADR-008: DRY Principle Implementation
        """
        raise LegacyCodeViolationError(
            pattern=f"Hardcoded configuration '{config_name}' = '{value}'",
            guidance="Extract to environment variables or configuration classes",
            adr_reference="ADR-008 (DRY Principle Implementation)",
            impact="Hardcoded values prevent environment-specific configuration and violate DRY principles"
        )
    
    @staticmethod
    def detect_manual_dictionary_construction(context: str):
        """
        Detect manual dictionary construction instead of model.to_dict().
        ADR-003: SQLAlchemy ORM Refactoring
        """
        raise LegacyCodeViolationError(
            pattern=f"Manual dictionary construction in '{context}'",
            guidance="Use model.to_dict() method for consistent serialization",
            adr_reference="ADR-003 (SQLAlchemy ORM Refactoring)",
            impact="Manual dictionary construction violates single source of truth and creates maintenance burden"
        )
    
    @staticmethod
    def detect_non_restful_api_patterns(route_path: str):
        """
        Detect non-RESTful API patterns.
        ADR-002: RESTful Resource Hierarchy API Design Pattern
        """
        raise LegacyCodeViolationError(
            pattern=f"Non-RESTful API pattern in route '{route_path}'",
            guidance="Use RESTful resource hierarchy: /api/{entity_type}/{id}/sub_resources",
            adr_reference="ADR-002 (RESTful Resource Hierarchy API Design Pattern)",
            impact="Non-RESTful patterns create API inconsistency and poor developer experience"
        )


def enforce_orm_usage(func):
    """
    Decorator to enforce ORM relationship usage over raw SQL.
    ADR-003: SQLAlchemy ORM Relationship Refactoring
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if function name suggests raw SQL usage
        if any(pattern in func.__name__.lower() for pattern in ['raw_sql', 'execute_sql', 'manual_query']):
            LegacyPatternDetector.detect_raw_sql_usage(func.__name__)
        return func(*args, **kwargs)
    return wrapper


def enforce_dynamic_forms(func):
    """
    Decorator to enforce dynamic form generation.
    ADR-008: DRY Principle Implementation
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if function creates manual form definitions
        if 'manual_form' in func.__name__.lower() or 'hardcoded_form' in func.__name__.lower():
            LegacyPatternDetector.detect_manual_form_definitions(func.__name__)
        return func(*args, **kwargs)
    return wrapper


def check_css_architecture():
    """
    Check for legacy ITCSS architecture usage.
    ADR-011: Simple CSS Architecture
    """
    css_dir = Path("app/static/css")
    
    # Check for ITCSS numbered directories
    itcss_patterns = ['01-settings', '02-tools', '03-generic', '04-elements', 
                      '05-objects', '06-components', '07-trumps']
    
    for pattern in itcss_patterns:
        pattern_path = css_dir / pattern
        if pattern_path.exists():
            LegacyPatternDetector.detect_itcss_architecture_usage(str(pattern_path))


def check_template_javascript():
    """
    Check for JavaScript embedded in templates.
    ADR-004: JavaScript Template Separation
    """
    template_dir = Path("app/templates")
    
    for html_file in template_dir.rglob("*.html"):
        try:
            content = html_file.read_text()
            # Look for embedded JavaScript patterns
            if any(pattern in content for pattern in ['<script>', 'javascript:', 'onclick=', 'onload=']):
                # Allow external script references but not embedded code
                if '<script src=' not in content or any(js_pattern in content for js_pattern in [
                    '<script>\n', '<script type=', 'function ', 'var ', 'let ', 'const '
                ]):
                    LegacyPatternDetector.detect_javascript_in_templates(str(html_file))
        except Exception:
            # Skip files that can't be read
            continue


def validate_api_routes():
    """
    Validate API routes follow RESTful patterns.
    ADR-002: RESTful Resource Hierarchy API Design Pattern
    """
    # This would be integrated with Flask route inspection
    # For now, provide the pattern detection capability
    legacy_patterns = [
        '/api/notes/entity/',  # Should be /api/{entity_type}/{id}/notes
        '/api/generic/',       # Should use specific resource names
        '/api/util/',          # Should be specific endpoints
    ]
    
    for pattern in legacy_patterns:
        if Path(f"app/routes{pattern}").exists():
            LegacyPatternDetector.detect_non_restful_api_patterns(pattern)


class LegacyCodeEnforcer:
    """
    Main enforcement system for legacy code detection.
    ADR-010: Legacy Code Elimination Strategy
    """
    
    @staticmethod
    def run_comprehensive_check():
        """
        Run comprehensive legacy code detection.
        Fails loudly if any legacy patterns are detected.
        """
        checks = [
            ("CSS Architecture", check_css_architecture),
            ("Template JavaScript", check_template_javascript),
            ("API Routes", validate_api_routes),
        ]
        
        violations = []
        
        for check_name, check_function in checks:
            try:
                check_function()
            except LegacyCodeViolationError as e:
                violations.append(f"{check_name}: {str(e)}")
        
        if violations:
            violation_summary = "\n\n".join(violations)
            raise LegacyCodeViolationError(
                pattern="Multiple legacy code violations detected",
                guidance="Address all violations listed below",
                adr_reference="ADR-010 (Legacy Code Elimination Strategy)",
                impact=f"Found {len(violations)} legacy patterns:\n\n{violation_summary}"
            )
    
    @staticmethod
    def enforce_modernization_only():
        """
        Enforce that all code changes modernize rather than accommodate legacy patterns.
        ADR-010: Zero tolerance modernization policy.
        """
        # This can be called from pre-commit hooks or CI/CD
        LegacyCodeEnforcer.run_comprehensive_check()


# Legacy function replacements with loud failures
def get_relationship_owners_legacy():
    """Legacy method that should trigger loud failure."""
    LegacyPatternDetector.detect_raw_sql_usage(
        "get_relationship_owners_legacy",
        "Use self.relationship_owners ORM relationship instead"
    )


def get_account_team_legacy():
    """Legacy method that should trigger loud failure.""" 
    LegacyPatternDetector.detect_raw_sql_usage(
        "get_account_team_legacy",
        "Use self.account_team_assignments ORM relationship instead"
    )


def get_stakeholders_legacy():
    """Legacy method that should trigger loud failure."""
    LegacyPatternDetector.detect_raw_sql_usage(
        "get_stakeholders_legacy", 
        "Use self.stakeholders ORM relationship instead"
    )