"""
CRM Service Structured Logging Configuration
ADR-012: Structured Logging Framework Implementation

Flask-specific structured logging extending chatbot service patterns.
Implements request correlation and comprehensive form/database logging.
"""

import logging
import json
import uuid
import time
from datetime import datetime
from typing import Optional, Dict, Any
from contextvars import ContextVar
from functools import wraps
from flask import request, g, has_request_context

# Context variables for request correlation
request_id_var: ContextVar[str] = ContextVar("request_id")
session_id_var: ContextVar[str] = ContextVar("session_id", default=None)
user_id_var: ContextVar[str] = ContextVar("user_id", default=None)


class CRMStructuredFormatter(logging.Formatter):
    """
    JSON structured logging formatter for Flask CRM service.
    ADR-012: Consistent structured logs across all services.

    Compatible with chatbot service logging format for correlation.
    """

    def __init__(self, service_name: str = "crm-service"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log entry structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "component": record.name,
            "message": record.getMessage(),
        }

        # Add request context if available
        if has_request_context():
            try:
                log_entry["request_id"] = getattr(g, 'request_id', None)
                log_entry["session_id"] = getattr(g, 'session_id', None)
                log_entry["user_id"] = getattr(g, 'user_id', None)
                log_entry["request_method"] = request.method
                log_entry["request_path"] = request.path
            except RuntimeError:
                # Outside request context
                log_entry["request_id"] = None
                log_entry["session_id"] = None
                log_entry["user_id"] = None
        else:
            log_entry["request_id"] = None
            log_entry["session_id"] = None
            log_entry["user_id"] = None

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add custom fields from record
        if hasattr(record, "custom_fields") and record.custom_fields:
            log_entry["custom_fields"] = record.custom_fields

        # Add CRM-specific fields
        if hasattr(record, "entity_type"):
            log_entry["entity_type"] = record.entity_type
        if hasattr(record, "entity_id"):
            log_entry["entity_id"] = record.entity_id
        if hasattr(record, "form_operation"):
            log_entry["form_operation"] = record.form_operation
        if hasattr(record, "database_operation"):
            log_entry["database_operation"] = record.database_operation
        if hasattr(record, "response_time_ms"):
            log_entry["response_time_ms"] = record.response_time_ms

        return json.dumps(log_entry, default=str)


def setup_crm_logging(service_name: str = "crm-service", debug: bool = False):
    """
    Configure structured logging for Flask CRM service.
    ADR-012: Unified logging setup across services.

    Args:
        service_name: Name of the service for log identification
        debug: Whether to enable debug logging
    """
    # Create structured formatter
    formatter = CRMStructuredFormatter(service_name)

    # Configure handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Set logging level
    log_level = logging.DEBUG if debug else logging.INFO

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Remove default handlers
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Configure Flask/Werkzeug loggers for consistency
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(handler)

    logging.info(f"Structured logging configured for {service_name}")


def request_logging_middleware():
    """
    Flask before/after request handlers for request correlation and logging.
    ADR-012: Request correlation across services.
    """
    def before_request():
        """Set up request context and logging."""
        # Extract or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        session_id = request.headers.get("X-Session-ID") or getattr(g, 'session_id', None)
        user_id = request.headers.get("X-User-ID") or getattr(g, 'user_id', None)

        # Set Flask g context for this request
        g.request_id = request_id
        g.session_id = session_id
        g.user_id = user_id
        g.request_start_time = time.time()

        # Log request start
        logging.info(
            "CRM request started",
            extra={
                "custom_fields": {
                    "request_method": request.method,
                    "request_path": request.path,
                    "query_params": dict(request.args),
                    "user_agent": request.headers.get("User-Agent"),
                    "remote_addr": request.remote_addr,
                    "content_type": request.content_type,
                }
            }
        )

    def after_request(response):
        """Log request completion."""
        # Calculate response time
        start_time = getattr(g, 'request_start_time', time.time())
        response_time_ms = (time.time() - start_time) * 1000

        # Add correlation headers to response
        if hasattr(g, 'request_id'):
            response.headers["X-Request-ID"] = g.request_id
        if hasattr(g, 'session_id') and g.session_id:
            response.headers["X-Session-ID"] = g.session_id

        # Log request completion
        logging.info(
            "CRM request completed",
            extra={
                "custom_fields": {
                    "response_status": response.status_code,
                    "response_time_ms": response_time_ms,
                    "response_size": response.content_length,
                },
                "response_time_ms": response_time_ms,
            }
        )

        return response

    return before_request, after_request


def get_crm_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance for CRM service.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_form_operation(
    logger: logging.Logger,
    operation: str,
    entity_type: str,
    form_data: Dict[str, Any],
    entity_id: Optional[int] = None,
    success: bool = True,
    errors: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """
    Log form operations in structured format.

    Args:
        logger: Logger instance
        operation: Type of form operation (create, update, validate)
        entity_type: Type of entity (stakeholder, company, etc.)
        form_data: Form field data
        entity_id: Entity ID if applicable
        success: Whether operation succeeded
        errors: Form validation errors if any
        **kwargs: Additional custom fields
    """
    custom_fields = {
        "operation": operation,
        "entity_type": entity_type,
        "form_fields": list(form_data.keys()) if form_data else [],
        "success": success,
        **kwargs
    }

    if entity_id:
        custom_fields["entity_id"] = entity_id

    if errors:
        custom_fields["validation_errors"] = errors

    # Sanitize form data (remove sensitive info, limit size)
    if form_data:
        sanitized_data = {}
        for key, value in form_data.items():
            if key.lower() in ['password', 'secret', 'token']:
                sanitized_data[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 500:
                sanitized_data[key] = value[:500] + "..."
            else:
                sanitized_data[key] = value
        custom_fields["form_data_sample"] = sanitized_data

    level = logging.INFO if success else logging.ERROR
    message = f"Form {operation} for {entity_type}"

    logger.log(
        level,
        message,
        extra={
            "custom_fields": custom_fields,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "form_operation": operation,
        }
    )


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    changes: Optional[Dict[str, Any]] = None,
    success: bool = True,
    execution_time_ms: Optional[float] = None,
    **kwargs
):
    """
    Log database operations in structured format.

    Args:
        logger: Logger instance
        operation: Type of database operation (create, update, delete, query)
        entity_type: Type of entity affected
        entity_id: Entity ID if applicable
        changes: Changes made to entity
        success: Whether operation succeeded
        execution_time_ms: Query execution time
        **kwargs: Additional custom fields
    """
    custom_fields = {
        "operation": operation,
        "entity_type": entity_type,
        "success": success,
        **kwargs
    }

    if entity_id:
        custom_fields["entity_id"] = entity_id

    if changes:
        custom_fields["changes"] = changes

    if execution_time_ms:
        custom_fields["execution_time_ms"] = execution_time_ms

    level = logging.INFO if success else logging.ERROR
    message = f"Database {operation} for {entity_type}"

    logger.log(
        level,
        message,
        extra={
            "custom_fields": custom_fields,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "database_operation": operation,
            "response_time_ms": execution_time_ms,
        }
    )


def log_meddpicc_operation(
    logger: logging.Logger,
    operation: str,
    stakeholder_id: int,
    previous_roles: Optional[list] = None,
    new_roles: Optional[list] = None,
    success: bool = True,
    **kwargs
):
    """
    Log MEDDPICC role operations specifically.

    Args:
        logger: Logger instance
        operation: Type of operation (assign, update, remove)
        stakeholder_id: Stakeholder entity ID
        previous_roles: Previous MEDDPICC roles
        new_roles: New MEDDPICC roles
        success: Whether operation succeeded
        **kwargs: Additional custom fields
    """
    custom_fields = {
        "operation": "meddpicc_roles_" + operation,
        "entity_type": "stakeholder",
        "entity_id": stakeholder_id,
        "previous_roles": previous_roles or [],
        "new_roles": new_roles or [],
        "roles_added": list(set(new_roles or []) - set(previous_roles or [])),
        "roles_removed": list(set(previous_roles or []) - set(new_roles or [])),
        "success": success,
        **kwargs
    }

    level = logging.INFO if success else logging.ERROR
    message = f"MEDDPICC roles {operation} for stakeholder {stakeholder_id}"

    logger.log(
        level,
        message,
        extra={
            "custom_fields": custom_fields,
            "entity_type": "stakeholder",
            "entity_id": stakeholder_id,
            "form_operation": "meddpicc_roles_" + operation,
        }
    )


def logging_decorator(operation: str):
    """
    Decorator to automatically log function operations.

    Args:
        operation: Type of operation being logged
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_crm_logger(func.__module__)
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                success = False
                error = str(e)
                logger.error(
                    f"Function {func.__name__} failed",
                    extra={
                        "custom_fields": {
                            "function": func.__name__,
                            "operation": operation,
                            "error": error,
                            "args_count": len(args),
                            "kwargs_keys": list(kwargs.keys()),
                        }
                    },
                    exc_info=True
                )
                raise
            finally:
                execution_time_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"Function {func.__name__} completed",
                    extra={
                        "custom_fields": {
                            "function": func.__name__,
                            "operation": operation,
                            "success": success,
                            "execution_time_ms": execution_time_ms,
                            "error": error,
                        },
                        "response_time_ms": execution_time_ms,
                    }
                )

            return result
        return wrapper
    return decorator