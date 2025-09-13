"""
Structured Logging Configuration
ADR-012: Structured Logging Framework Implementation

Provides JSON structured logging with cross-service correlation.
Implements request correlation, performance logging, and unified format.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g, has_request_context


class StructuredFormatter(logging.Formatter):
    """
    JSON structured logging formatter.
    ADR-012: Consistent structured logs across all services.
    
    Output format:
    {
        "timestamp": "2025-09-13T12:45:30.123Z",
        "level": "INFO",
        "service": "crm-service",
        "component": "routes.companies",
        "message": "Company created successfully",
        "request_id": "uuid4-string",
        "session_id": "session-identifier", 
        "user_id": "authenticated-user-id",
        "custom_fields": {...}
    }
    """
    
    def __init__(self, service_name: str = "crm-service"):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log entry structure
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'service': self.service_name,
            'component': record.name,
            'message': record.getMessage(),
        }
        
        # Add request context if available
        if has_request_context():
            log_entry.update({
                'request_id': getattr(g, 'request_id', None),
                'session_id': getattr(g, 'session_id', None),
                'user_id': getattr(g, 'user_id', None),
                'request_method': request.method if request else None,
                'request_path': request.path if request else None,
            })
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add custom fields from record
        if hasattr(record, 'custom_fields') and record.custom_fields:
            log_entry['custom_fields'] = record.custom_fields
            
        # Add performance metrics if present
        if hasattr(record, 'execution_time_ms'):
            log_entry['execution_time_ms'] = record.execution_time_ms
        if hasattr(record, 'response_time_ms'):
            log_entry['response_time_ms'] = record.response_time_ms
            
        # Add entity context if present
        if hasattr(record, 'entity_type'):
            log_entry['entity_type'] = record.entity_type
        if hasattr(record, 'entity_id'):
            log_entry['entity_id'] = record.entity_id
            
        return json.dumps(log_entry, default=str)


def setup_structured_logging(app, service_name: str = "crm-service"):
    """
    Configure structured logging for Flask application.
    ADR-012: Unified logging setup across services.
    
    Args:
        app: Flask application instance
        service_name: Name of the service for log identification
    """
    # Create structured formatter
    formatter = StructuredFormatter(service_name)
    
    # Configure handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # Set logging level
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    # Configure app logger
    app.logger.handlers.clear()  # Remove default handlers
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    
    # Configure root logger for consistent formatting
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)
    
    # Add request correlation middleware
    @app.before_request
    def before_request_logging():
        """Add request correlation IDs to Flask g context."""
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.session_id = request.headers.get('X-Session-ID')
        g.user_id = getattr(request, 'user_id', None)  # Set by auth middleware
        
        # Log request start
        app.logger.info(
            "Request started",
            extra={
                'custom_fields': {
                    'request_method': request.method,
                    'request_path': request.path,
                    'request_args': dict(request.args),
                    'user_agent': request.headers.get('User-Agent'),
                    'remote_addr': request.remote_addr,
                }
            }
        )
    
    @app.after_request
    def after_request_logging(response):
        """Log request completion with response details."""
        app.logger.info(
            "Request completed",
            extra={
                'custom_fields': {
                    'status_code': response.status_code,
                    'content_length': response.content_length,
                    'content_type': response.content_type,
                }
            }
        )
        
        # Add request ID to response headers for correlation
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
            
        return response
    
    app.logger.info(f"Structured logging configured for {service_name}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_performance(logger: logging.Logger, func_name: str, execution_time_ms: float, 
                   success: bool = True, error: Optional[str] = None, **kwargs):
    """
    Log performance metrics in structured format.
    
    Args:
        logger: Logger instance
        func_name: Name of the function being measured
        execution_time_ms: Execution time in milliseconds
        success: Whether the function completed successfully
        error: Error message if function failed
        **kwargs: Additional custom fields
    """
    custom_fields = {
        'function_name': func_name,
        'execution_time_ms': execution_time_ms,
        'success': success,
        **kwargs
    }
    
    if error:
        custom_fields['error'] = error
        
    level = logging.INFO if success else logging.ERROR
    message = f"Function {func_name} completed" if success else f"Function {func_name} failed"
    
    logger.log(
        level,
        message,
        extra={'custom_fields': custom_fields}
    )


def log_entity_operation(logger: logging.Logger, operation: str, entity_type: str, 
                        entity_id: Any, success: bool = True, **kwargs):
    """
    Log entity operations in structured format.
    
    Args:
        logger: Logger instance
        operation: Type of operation (create, update, delete, etc.)
        entity_type: Type of entity (company, task, etc.)
        entity_id: Entity identifier
        success: Whether operation succeeded
        **kwargs: Additional custom fields
    """
    custom_fields = {
        'operation': operation,
        'entity_type': entity_type,
        'entity_id': str(entity_id),
        'success': success,
        **kwargs
    }
    
    level = logging.INFO if success else logging.ERROR
    message = f"Entity {operation}: {entity_type}#{entity_id}"
    
    logger.log(
        level,
        message,
        extra={
            'custom_fields': custom_fields,
            'entity_type': entity_type,
            'entity_id': str(entity_id)
        }
    )