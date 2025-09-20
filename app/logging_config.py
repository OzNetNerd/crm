"""
CRM Application Structured Logging Configuration
Implements comprehensive logging for debugging and troubleshooting

Based on chatbot logging patterns but adapted for Flask/WSGI environment.
Provides full visibility into application operations for better debugging.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from contextvars import ContextVar
from functools import wraps
from flask import request, g, has_request_context
import os


# Context variables for request correlation
request_id_var: ContextVar[str] = ContextVar("request_id")
user_session_var: ContextVar[str] = ContextVar("user_session", default=None)
user_id_var: ContextVar[str] = ContextVar("user_id", default=None)


class CRMStructuredFormatter(logging.Formatter):
    """
    JSON structured logging formatter for CRM Flask application.

    Provides consistent structured logs across all components for better
    debugging and troubleshooting capabilities.
    """

    def __init__(self, service_name: str = "crm-web"):
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
                log_entry["user_session"] = getattr(g, 'user_session', None)
                log_entry["user_id"] = getattr(g, 'user_id', None)
                log_entry["method"] = request.method
                log_entry["path"] = request.path
                log_entry["remote_addr"] = request.remote_addr
            except Exception:
                # Don't fail logging if request context is unavailable
                pass

        # Add extra fields from log record
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None
            }

        # Add stack trace for errors
        if record.levelno >= logging.ERROR and record.stack_info:
            log_entry["stack_trace"] = record.stack_info

        return json.dumps(log_entry, default=str, ensure_ascii=False)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Configure structured logging for the CRM application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path. If None, logs to stdout.
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter
    formatter = CRMStructuredFormatter()

    # Setup handler
    if log_file:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    handler.setLevel(numeric_level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Remove default handlers
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)

    # Configure Flask's werkzeug logger to use our formatter
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(handler)
    werkzeug_logger.setLevel(numeric_level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance for CRM components.

    Args:
        name: Component name (e.g., 'crm.routes.users', 'crm.database')

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_function_call(
    logger: logging.Logger,
    func_name: str,
    args: Dict[str, Any] = None,
    level: int = logging.DEBUG
):
    """
    Log function entry with arguments.

    Args:
        logger: Logger instance
        func_name: Function name being called
        args: Function arguments to log
        level: Log level
    """
    extra_fields = {
        "function_name": func_name,
        "function_args": args or {}
    }

    logger.log(
        level,
        f"Entering function: {func_name}",
        extra={'extra_fields': extra_fields}
    )


def log_function_result(
    logger: logging.Logger,
    func_name: str,
    result: Any = None,
    execution_time_ms: float = None,
    level: int = logging.DEBUG
):
    """
    Log function exit with result and timing.

    Args:
        logger: Logger instance
        func_name: Function name that completed
        result: Function result (will be stringified)
        execution_time_ms: Execution time in milliseconds
        level: Log level
    """
    extra_fields = {
        "function_name": func_name,
        "execution_time_ms": execution_time_ms
    }

    if result is not None:
        extra_fields["result_type"] = type(result).__name__
        if hasattr(result, '__len__'):
            extra_fields["result_length"] = len(result)

    logger.log(
        level,
        f"Exiting function: {func_name}",
        extra={'extra_fields': extra_fields}
    )


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table_name: str = None,
    record_id: Any = None,
    execution_time_ms: float = None,
    level: int = logging.INFO
):
    """
    Log database operations for troubleshooting.

    Args:
        logger: Logger instance
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table_name: Database table name
        record_id: Record ID being operated on
        execution_time_ms: Query execution time
        level: Log level
    """
    extra_fields = {
        "db_operation": operation,
        "table_name": table_name,
        "record_id": record_id,
        "execution_time_ms": execution_time_ms
    }

    logger.log(
        level,
        f"Database {operation} on {table_name}",
        extra={'extra_fields': extra_fields}
    )


def log_template_render(
    logger: logging.Logger,
    template_name: str,
    context_keys: list = None,
    execution_time_ms: float = None,
    level: int = logging.DEBUG
):
    """
    Log template rendering operations.

    Args:
        logger: Logger instance
        template_name: Template file name
        context_keys: Keys passed in template context
        execution_time_ms: Rendering time
        level: Log level
    """
    extra_fields = {
        "template_name": template_name,
        "context_keys": context_keys or [],
        "execution_time_ms": execution_time_ms
    }

    logger.log(
        level,
        f"Rendering template: {template_name}",
        extra={'extra_fields': extra_fields}
    )


def log_form_submission(
    logger: logging.Logger,
    form_name: str,
    is_valid: bool,
    errors: Dict[str, list] = None,
    level: int = logging.INFO
):
    """
    Log form submission and validation results.

    Args:
        logger: Logger instance
        form_name: Form class name
        is_valid: Whether form validation passed
        errors: Form validation errors
        level: Log level
    """
    extra_fields = {
        "form_name": form_name,
        "is_valid": is_valid,
        "validation_errors": errors or {}
    }

    status = "valid" if is_valid else "invalid"
    logger.log(
        level,
        f"Form submission {status}: {form_name}",
        extra={'extra_fields': extra_fields}
    )


def log_htmx_request(
    logger: logging.Logger,
    target: str = None,
    trigger: str = None,
    level: int = logging.DEBUG
):
    """
    Log HTMX partial page updates.

    Args:
        logger: Logger instance
        target: HTMX target element
        trigger: HTMX trigger event
        level: Log level
    """
    if has_request_context():
        extra_fields = {
            "htmx_request": True,
            "htmx_target": target or request.headers.get('HX-Target'),
            "htmx_trigger": trigger or request.headers.get('HX-Trigger'),
            "htmx_current_url": request.headers.get('HX-Current-URL'),
            "is_htmx": bool(request.headers.get('HX-Request'))
        }

        logger.log(
            level,
            "HTMX partial update request",
            extra={'extra_fields': extra_fields}
        )


# Component-specific logger instances
routes_logger = get_logger('crm.routes')
database_logger = get_logger('crm.database')
templates_logger = get_logger('crm.templates')
forms_logger = get_logger('crm.forms')
frontend_logger = get_logger('crm.frontend')
performance_logger = get_logger('crm.performance')