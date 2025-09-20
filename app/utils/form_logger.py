"""
Form-Specific Logging Utilities
ADR-012: Structured Logging Framework Implementation

Specialized logging functions for form validation, processing, and data transformation.
Provides detailed insights for troubleshooting form-related issues like MEDDPICC dropdown.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from flask import request, g
from wtforms import Form, Field

from .logging_config import get_crm_logger, log_form_operation, log_meddpicc_operation


class FormLogger:
    """
    Enhanced form logging with detailed field-level tracking.
    Specialized for CRM form operations and validation debugging.
    """

    def __init__(self, logger_name: str = None):
        self.logger = get_crm_logger(logger_name or __name__)

    def log_form_submission(self, form: Form, entity_type: str, entity_id: Optional[int] = None):
        """
        Log form submission with complete field data.

        Args:
            form: WTForms form instance
            entity_type: Type of entity (stakeholder, company, etc.)
            entity_id: Entity ID for updates
        """
        form_data = {}
        field_types = {}
        field_errors = {}

        for field_name, field in form._fields.items():
            form_data[field_name] = field.data
            field_types[field_name] = type(field).__name__
            if field.errors:
                field_errors[field_name] = field.errors

        operation = "update" if entity_id else "create"

        log_form_operation(
            self.logger,
            operation="submission",
            entity_type=entity_type,
            form_data=form_data,
            entity_id=entity_id,
            success=form.validate(),
            errors=field_errors if field_errors else None,
            field_types=field_types,
            form_method=request.method if request else "unknown"
        )

    def log_form_validation(self, form: Form, entity_type: str):
        """
        Log detailed form validation results.

        Args:
            form: WTForms form instance
            entity_type: Type of entity being validated
        """
        validation_start = time.time()
        is_valid = form.validate()
        validation_time_ms = (time.time() - validation_start) * 1000

        errors = {}
        for field_name, field in form._fields.items():
            if field.errors:
                errors[field_name] = {
                    "errors": field.errors,
                    "data": field.data,
                    "field_type": type(field).__name__
                }

        log_form_operation(
            self.logger,
            operation="validation",
            entity_type=entity_type,
            form_data={},  # Don't log data twice
            success=is_valid,
            errors=errors if errors else None,
            validation_time_ms=validation_time_ms,
            total_fields=len(form._fields),
            error_fields=len(errors)
        )

        return is_valid

    def log_select_multiple_field(self, field: Field, field_name: str, entity_type: str):
        """
        Log SelectMultipleField specific processing for MEDDPICC troubleshooting.

        Args:
            field: SelectMultipleField instance
            field_name: Name of the field
            entity_type: Type of entity
        """
        field_data = {
            "field_name": field_name,
            "field_type": type(field).__name__,
            "raw_data": field.raw_data,
            "processed_data": field.data,
            "choices": getattr(field, 'choices', []),
            "has_errors": bool(field.errors),
            "errors": field.errors if field.errors else None
        }

        # Special handling for MEDDPICC roles
        if 'meddpicc' in field_name.lower():
            field_data["is_meddpicc_field"] = True
            if hasattr(field, 'data') and field.data:
                field_data["selected_roles"] = field.data
                field_data["role_count"] = len(field.data) if isinstance(field.data, list) else 0

        self.logger.info(
            f"SelectMultipleField processing: {field_name}",
            extra={
                "custom_fields": field_data,
                "entity_type": entity_type,
                "form_operation": "select_multiple_processing"
            }
        )

    def log_field_data_transformation(self, field_name: str, original_data: Any,
                                    transformed_data: Any, entity_type: str,
                                    transformation_type: str = "unknown"):
        """
        Log data transformation for form fields.

        Args:
            field_name: Name of the field
            original_data: Original data before transformation
            transformed_data: Data after transformation
            entity_type: Type of entity
            transformation_type: Type of transformation applied
        """
        self.logger.info(
            f"Field data transformation: {field_name}",
            extra={
                "custom_fields": {
                    "field_name": field_name,
                    "transformation_type": transformation_type,
                    "original_data": original_data,
                    "transformed_data": transformed_data,
                    "original_type": type(original_data).__name__,
                    "transformed_type": type(transformed_data).__name__,
                    "data_changed": original_data != transformed_data
                },
                "entity_type": entity_type,
                "form_operation": "data_transformation"
            }
        )


class MEDDPICCLogger:
    """
    Specialized logger for MEDDPICC role operations.
    Provides detailed tracking for stakeholder role assignments.
    """

    def __init__(self):
        self.logger = get_crm_logger(__name__)

    def log_role_processing_start(self, stakeholder_id: int, form_data: Any):
        """
        Log the start of MEDDPICC role processing.

        Args:
            stakeholder_id: ID of the stakeholder
            form_data: Raw form data for roles
        """
        self.logger.info(
            f"MEDDPICC role processing started for stakeholder {stakeholder_id}",
            extra={
                "custom_fields": {
                    "operation": "meddpicc_processing_start",
                    "stakeholder_id": stakeholder_id,
                    "raw_form_data": form_data,
                    "form_data_type": type(form_data).__name__
                },
                "entity_type": "stakeholder",
                "entity_id": stakeholder_id,
                "form_operation": "meddpicc_start"
            }
        )

    def log_role_data_parsing(self, stakeholder_id: int, raw_data: str,
                            parsed_data: List[str], success: bool = True):
        """
        Log MEDDPICC role data parsing.

        Args:
            stakeholder_id: ID of the stakeholder
            raw_data: Raw role data string
            parsed_data: Parsed role list
            success: Whether parsing succeeded
        """
        self.logger.info(
            f"MEDDPICC role data parsing for stakeholder {stakeholder_id}",
            extra={
                "custom_fields": {
                    "operation": "meddpicc_data_parsing",
                    "stakeholder_id": stakeholder_id,
                    "raw_data": raw_data,
                    "parsed_data": parsed_data,
                    "role_count": len(parsed_data) if parsed_data else 0,
                    "parsing_success": success
                },
                "entity_type": "stakeholder",
                "entity_id": stakeholder_id,
                "form_operation": "meddpicc_parsing"
            }
        )

    def log_role_assignment(self, stakeholder_id: int, previous_roles: List[str],
                          new_roles: List[str], success: bool = True):
        """
        Log MEDDPICC role assignment operation.

        Args:
            stakeholder_id: ID of the stakeholder
            previous_roles: Previous role assignments
            new_roles: New role assignments
            success: Whether assignment succeeded
        """
        log_meddpicc_operation(
            self.logger,
            operation="assignment",
            stakeholder_id=stakeholder_id,
            previous_roles=previous_roles,
            new_roles=new_roles,
            success=success
        )

    def log_role_database_operation(self, stakeholder_id: int, operation: str,
                                  roles: List[str], success: bool = True,
                                  error: str = None):
        """
        Log database operations for MEDDPICC roles.

        Args:
            stakeholder_id: ID of the stakeholder
            operation: Database operation (insert, delete, update)
            roles: Roles involved in operation
            success: Whether operation succeeded
            error: Error message if failed
        """
        self.logger.info(
            f"MEDDPICC role database {operation} for stakeholder {stakeholder_id}",
            extra={
                "custom_fields": {
                    "operation": f"meddpicc_db_{operation}",
                    "stakeholder_id": stakeholder_id,
                    "roles": roles,
                    "role_count": len(roles) if roles else 0,
                    "success": success,
                    "error": error
                },
                "entity_type": "stakeholder",
                "entity_id": stakeholder_id,
                "database_operation": f"meddpicc_{operation}"
            }
        )


class TemplateRenderLogger:
    """
    Logger for template rendering operations, especially form-related templates.
    """

    def __init__(self):
        self.logger = get_crm_logger(__name__)

    def log_form_render(self, template_name: str, entity_type: str,
                       entity_id: Optional[int] = None, mode: str = "unknown",
                       form_fields: Optional[List[str]] = None):
        """
        Log form template rendering.

        Args:
            template_name: Name of the template being rendered
            entity_type: Type of entity
            entity_id: Entity ID if applicable
            mode: Render mode (create, edit, view)
            form_fields: List of form field names
        """
        self.logger.info(
            f"Form template rendering: {template_name}",
            extra={
                "custom_fields": {
                    "template_name": template_name,
                    "render_mode": mode,
                    "form_fields": form_fields or [],
                    "field_count": len(form_fields) if form_fields else 0,
                    "has_entity_id": entity_id is not None
                },
                "entity_type": entity_type,
                "entity_id": entity_id,
                "form_operation": f"template_render_{mode}"
            }
        )

    def log_select_multiple_render(self, field_name: str, choices: List,
                                 selected_values: List, entity_type: str):
        """
        Log SelectMultipleField rendering details.

        Args:
            field_name: Name of the select multiple field
            choices: Available choices
            selected_values: Currently selected values
            entity_type: Type of entity
        """
        self.logger.info(
            f"SelectMultipleField rendering: {field_name}",
            extra={
                "custom_fields": {
                    "field_name": field_name,
                    "choice_count": len(choices) if choices else 0,
                    "selected_count": len(selected_values) if selected_values else 0,
                    "choices": choices[:10] if choices else [],  # Limit for log size
                    "selected_values": selected_values,
                    "has_selections": bool(selected_values)
                },
                "entity_type": entity_type,
                "form_operation": "select_multiple_render"
            }
        )


# Convenience instances for common usage
form_logger = FormLogger()
meddpicc_logger = MEDDPICCLogger()
template_logger = TemplateRenderLogger()