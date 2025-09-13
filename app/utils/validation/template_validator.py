"""
Template validation utilities for ADR-004 compliance.

This module provides functions to detect and prevent legacy patterns
in Jinja2 templates, particularly embedded JavaScript.
"""

import re
import os
from pathlib import Path
from typing import List, Tuple, Optional
from jinja2 import Environment, BaseLoader, TemplateSyntaxError

from app.utils.exceptions.legacy_exceptions import TemplateModernizationError


class TemplateValidator:
    """Validates Jinja2 templates for legacy pattern compliance."""
    
    def __init__(self, template_dir: str = "app/templates"):
        """
        Initialize template validator.
        
        Args:
            template_dir: Directory containing Jinja2 templates to validate
        """
        self.template_dir = Path(template_dir)
        self.javascript_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
        self.inline_js_pattern = re.compile(r'on\w+\s*=\s*["\'][^"\']*["\']', re.IGNORECASE)
        
    def validate_template(self, template_path: Path) -> None:
        """
        Validate a single template for legacy patterns.
        
        Args:
            template_path: Path to the template file to validate
            
        Raises:
            TemplateModernizationError: If embedded JavaScript is detected
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            # Skip files that can't be read (not templates)
            return
            
        # Check for embedded JavaScript
        script_matches = self.javascript_pattern.findall(content)
        if script_matches:
            # Extract first script content for error message
            script_content = script_matches[0].strip()
            raise TemplateModernizationError(
                template_path=str(template_path),
                script_content=script_content
            )
            
        # Check for inline JavaScript event handlers
        inline_matches = self.inline_js_pattern.findall(content)
        if inline_matches:
            raise TemplateModernizationError(
                template_path=str(template_path),
                script_content=f"Inline event handlers: {', '.join(inline_matches[:3])}"
            )
    
    def validate_all_templates(self) -> List[TemplateModernizationError]:
        """
        Validate all templates in the template directory.
        
        Returns:
            List of validation errors found
        """
        errors = []
        
        if not self.template_dir.exists():
            return errors
            
        # Find all HTML template files
        template_files = list(self.template_dir.rglob("*.html"))
        
        for template_path in template_files:
            try:
                self.validate_template(template_path)
            except TemplateModernizationError as e:
                errors.append(e)
                
        return errors
    
    def get_legacy_templates(self) -> List[Tuple[str, str]]:
        """
        Get list of templates with legacy JavaScript patterns.
        
        Returns:
            List of tuples containing (template_path, violation_description)
        """
        legacy_templates = []
        
        if not self.template_dir.exists():
            return legacy_templates
            
        template_files = list(self.template_dir.rglob("*.html"))
        
        for template_path in template_files:
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError):
                continue
                
            violations = []
            
            # Check for embedded scripts
            script_matches = self.javascript_pattern.findall(content)
            if script_matches:
                violations.append(f"Embedded <script> tags ({len(script_matches)} found)")
                
            # Check for inline event handlers
            inline_matches = self.inline_js_pattern.findall(content)
            if inline_matches:
                violations.append(f"Inline event handlers ({len(inline_matches)} found)")
                
            if violations:
                relative_path = template_path.relative_to(self.template_dir)
                legacy_templates.append((str(relative_path), "; ".join(violations)))
                
        return legacy_templates


def enforce_template_compliance(template_path: str) -> None:
    """
    Enforce template compliance for a specific template.
    
    This function implements loud failure for template legacy patterns.
    It should be called during template rendering to catch violations.
    
    Args:
        template_path: Path to the template being rendered
        
    Raises:
        TemplateModernizationError: If legacy patterns are detected
    """
    validator = TemplateValidator()
    
    # Convert relative path to full path for validation
    full_path = Path(validator.template_dir) / template_path
    
    if full_path.exists():
        validator.validate_template(full_path)


def check_template_directory() -> bool:
    """
    Check entire template directory for legacy patterns.
    
    Returns:
        True if all templates are compliant, False if violations found
        
    Raises:
        TemplateModernizationError: On first violation found (loud failure)
    """
    validator = TemplateValidator()
    errors = validator.validate_all_templates()
    
    if errors:
        # Implement loud failure - raise the first error found
        raise errors[0]
        
    return True


def get_compliance_report() -> dict:
    """
    Generate a compliance report for all templates.
    
    Returns:
        Dictionary containing compliance statistics and violations
    """
    validator = TemplateValidator()
    legacy_templates = validator.get_legacy_templates()
    
    if not validator.template_dir.exists():
        return {
            "status": "error",
            "message": "Template directory not found",
            "violations": []
        }
    
    total_templates = len(list(validator.template_dir.rglob("*.html")))
    compliant_templates = total_templates - len(legacy_templates)
    
    return {
        "status": "non_compliant" if legacy_templates else "compliant",
        "total_templates": total_templates,
        "compliant_templates": compliant_templates,
        "violation_count": len(legacy_templates),
        "compliance_percentage": (compliant_templates / total_templates * 100) if total_templates > 0 else 100,
        "violations": legacy_templates
    }