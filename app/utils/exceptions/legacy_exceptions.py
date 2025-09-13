"""
Legacy pattern detection exceptions for ADR-010 compliance.

This module defines custom exceptions that implement loud failure patterns
for legacy code detection and enforcement.
"""

from typing import Optional


class LegacyCodeError(Exception):
    """Base exception for all legacy code pattern detections."""
    
    def __init__(self, message: str, adr_reference: str, modernization_steps: str):
        """
        Initialize legacy code error with standardized message format.
        
        Args:
            message: Specific legacy pattern description
            adr_reference: ADR number for detailed guidance
            modernization_steps: Required actions to modernize
        """
        formatted_message = (
            f"LEGACY CODE DETECTED: {message}\n"
            f"REQUIRED ACTION: {modernization_steps}\n"
            f"REFERENCE: {adr_reference} for detailed migration guidance\n"
            f"IMPACT: This legacy pattern violates established architecture standards"
        )
        super().__init__(formatted_message)
        self.adr_reference = adr_reference
        self.modernization_steps = modernization_steps


class TemplateModernizationError(LegacyCodeError):
    """Loud failure for JavaScript embedded in Jinja2 templates."""
    
    def __init__(self, template_path: str, script_content: Optional[str] = None):
        """
        Initialize template modernization error.
        
        Args:
            template_path: Path to the template containing embedded JavaScript
            script_content: Optional excerpt of the embedded script content
        """
        message = f"JavaScript embedded in Jinja2 template: {template_path}"
        if script_content:
            preview = script_content[:100] + "..." if len(script_content) > 100 else script_content
            message += f"\nDetected script: {preview}"
            
        modernization_steps = (
            "1. Extract JavaScript to separate .js file in app/static/js/\n"
            "2. Use proper module imports and event handlers\n"
            "3. Remove <script> tags from template\n"
            "4. Ensure separation of concerns between HTML and JavaScript"
        )
        
        super().__init__(message, "ADR-004", modernization_steps)
        self.template_path = template_path
        self.script_content = script_content


class LegacySQLError(LegacyCodeError):
    """Loud failure for raw SQL usage instead of ORM relationships."""
    
    def __init__(self, query: str, suggested_orm_method: str):
        """
        Initialize legacy SQL error.
        
        Args:
            query: The raw SQL query that was detected
            suggested_orm_method: Recommended ORM method to use instead
        """
        message = f"Raw SQL query detected: {query[:100]}..."
        modernization_steps = (
            f"1. Replace raw SQL with ORM method: {suggested_orm_method}\n"
            "2. Use SQLAlchemy relationships and query methods\n"
            "3. Leverage established model patterns\n"
            "4. Ensure type safety and relationship integrity"
        )
        
        super().__init__(message, "ADR-003", modernization_steps)
        self.query = query
        self.suggested_orm_method = suggested_orm_method


class ConfigurationLegacyError(LegacyCodeError):
    """Loud failure for hardcoded configuration values."""
    
    def __init__(self, config_key: str, hardcoded_value: str):
        """
        Initialize configuration legacy error.
        
        Args:
            config_key: The configuration key that is hardcoded
            hardcoded_value: The hardcoded value that should be externalized
        """
        message = f"Hardcoded configuration detected: {config_key} = {hardcoded_value}"
        modernization_steps = (
            f"1. Move {config_key} to environment variables\n"
            "2. Use os.environ.get() with appropriate defaults\n"
            "3. Update deployment configuration\n"
            "4. Document required environment variables"
        )
        
        super().__init__(message, "Multiple ADRs", modernization_steps)
        self.config_key = config_key
        self.hardcoded_value = hardcoded_value


class FormDefinitionError(LegacyCodeError):
    """Loud failure for manual form definitions instead of dynamic generation."""
    
    def __init__(self, form_class: str):
        """
        Initialize form definition error.
        
        Args:
            form_class: Name of the manually defined form class
        """
        message = f"Manual form definition detected: {form_class}"
        modernization_steps = (
            "1. Use dynamic form builders from app/forms/base/builders.py\n"
            "2. Leverage metadata-driven form generation\n"
            "3. Remove manual form class definitions\n"
            "4. Ensure DRY principle compliance"
        )
        
        super().__init__(message, "ADR-008", modernization_steps)
        self.form_class = form_class


class RouteHandlerLegacyError(LegacyCodeError):
    """Loud failure for duplicated CRUD logic instead of base classes."""
    
    def __init__(self, route_handler: str, duplicated_pattern: str):
        """
        Initialize route handler legacy error.
        
        Args:
            route_handler: Name of the route handler with legacy patterns
            duplicated_pattern: Description of the duplicated logic
        """
        message = f"Duplicated CRUD logic in route handler: {route_handler}"
        modernization_steps = (
            "1. Use base handler classes from app/utils/core/base_handlers.py\n"
            "2. Leverage established CRUD patterns\n"
            "3. Remove duplicated route logic\n"
            "4. Ensure consistent error handling and response patterns"
        )
        
        super().__init__(message, "ADR-008", modernization_steps)
        self.route_handler = route_handler
        self.duplicated_pattern = duplicated_pattern