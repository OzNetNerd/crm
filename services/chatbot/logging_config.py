"""
Chatbot Service Structured Logging Configuration
ADR-012: Structured Logging Framework Implementation

FastAPI-specific structured logging with async support.
Implements request correlation with CRM service integration.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
from fastapi import Request


# Context variables for request correlation in async environment
request_id_var: ContextVar[str] = ContextVar('request_id')
session_id_var: ContextVar[str] = ContextVar('session_id', default=None)
user_id_var: ContextVar[str] = ContextVar('user_id', default=None)


class ChatbotStructuredFormatter(logging.Formatter):
    """
    JSON structured logging formatter for FastAPI chatbot service.
    ADR-012: Consistent structured logs across all services.
    
    Compatible with CRM service logging format for correlation.
    """
    
    def __init__(self, service_name: str = "chatbot-service"):
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
        
        # Add request context from context variables
        try:
            log_entry['request_id'] = request_id_var.get(None)
        except LookupError:
            log_entry['request_id'] = None
            
        try:
            log_entry['session_id'] = session_id_var.get(None)
        except LookupError:
            log_entry['session_id'] = None
            
        try:
            log_entry['user_id'] = user_id_var.get(None)
        except LookupError:
            log_entry['user_id'] = None
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add custom fields from record
        if hasattr(record, 'custom_fields') and record.custom_fields:
            log_entry['custom_fields'] = record.custom_fields
            
        # Add AI/chatbot specific fields
        if hasattr(record, 'ai_model'):
            log_entry['ai_model'] = record.ai_model
        if hasattr(record, 'response_time_ms'):
            log_entry['response_time_ms'] = record.response_time_ms
        if hasattr(record, 'query_type'):
            log_entry['query_type'] = record.query_type
        if hasattr(record, 'vector_results'):
            log_entry['vector_results'] = record.vector_results
            
        return json.dumps(log_entry, default=str)


def setup_chatbot_logging(service_name: str = "chatbot-service", debug: bool = False):
    """
    Configure structured logging for FastAPI chatbot service.
    ADR-012: Unified logging setup across services.
    
    Args:
        service_name: Name of the service for log identification
        debug: Whether to enable debug logging
    """
    # Create structured formatter
    formatter = ChatbotStructuredFormatter(service_name)
    
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
    
    # Configure uvicorn loggers for consistency
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers.clear()
    uvicorn_logger.addHandler(handler)
    
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers.clear()
    uvicorn_access_logger.addHandler(handler)
    
    logging.info(f"Structured logging configured for {service_name}")


async def log_request_middleware(request: Request, call_next):
    """
    FastAPI middleware for request correlation and logging.
    ADR-012: Request correlation across services.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware in chain
        
    Returns:
        Response with correlation headers
    """
    # Extract or generate request ID
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    session_id = request.headers.get('X-Session-ID')
    user_id = request.headers.get('X-User-ID')  # From authentication
    
    # Set context variables for async logging
    request_id_var.set(request_id)
    if session_id:
        session_id_var.set(session_id)
    if user_id:
        user_id_var.set(user_id)
    
    # Log request start
    start_time = datetime.utcnow()
    logging.info(
        "Chatbot request started",
        extra={
            'custom_fields': {
                'request_method': request.method,
                'request_path': str(request.url.path),
                'query_params': dict(request.query_params),
                'user_agent': request.headers.get('User-Agent'),
                'client_host': request.client.host if request.client else None,
            }
        }
    )
    
    # Process request
    try:
        response = await call_next(request)
        success = True
        error = None
    except Exception as e:
        success = False
        error = str(e)
        logging.error(
            "Chatbot request failed",
            extra={
                'custom_fields': {
                    'error': error,
                    'error_type': type(e).__name__
                }
            },
            exc_info=True
        )
        raise
    finally:
        # Log request completion
        end_time = datetime.utcnow()
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        logging.info(
            "Chatbot request completed",
            extra={
                'custom_fields': {
                    'success': success,
                    'response_time_ms': response_time_ms,
                    'error': error
                }
            }
        )
    
    # Add correlation headers to response
    response.headers['X-Request-ID'] = request_id
    if session_id:
        response.headers['X-Session-ID'] = session_id
        
    return response


def get_chatbot_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance for chatbot service.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_ai_operation(logger: logging.Logger, operation: str, model: str,
                    response_time_ms: float, success: bool = True, 
                    query_type: Optional[str] = None, **kwargs):
    """
    Log AI operations in structured format.
    
    Args:
        logger: Logger instance
        operation: Type of AI operation (query, embedding, etc.)
        model: AI model used (llama2, codellama, etc.)
        response_time_ms: Response time in milliseconds
        success: Whether operation succeeded
        query_type: Type of query (company, task, etc.)
        **kwargs: Additional custom fields
    """
    custom_fields = {
        'operation': operation,
        'ai_model': model,
        'response_time_ms': response_time_ms,
        'success': success,
        **kwargs
    }
    
    if query_type:
        custom_fields['query_type'] = query_type
        
    level = logging.INFO if success else logging.ERROR
    message = f"AI {operation} using {model}"
    
    logger.log(
        level,
        message,
        extra={
            'custom_fields': custom_fields,
            'ai_model': model,
            'response_time_ms': response_time_ms,
            'query_type': query_type
        }
    )


def log_vector_search(logger: logging.Logger, query: str, results_count: int,
                     search_time_ms: float, success: bool = True, **kwargs):
    """
    Log vector search operations in structured format.
    
    Args:
        logger: Logger instance
        query: Search query text
        results_count: Number of results returned
        search_time_ms: Search time in milliseconds  
        success: Whether search succeeded
        **kwargs: Additional custom fields
    """
    custom_fields = {
        'operation': 'vector_search',
        'query_length': len(query),
        'results_count': results_count,
        'search_time_ms': search_time_ms,
        'success': success,
        **kwargs
    }
        
    level = logging.INFO if success else logging.ERROR
    message = f"Vector search returned {results_count} results"
    
    logger.log(
        level,
        message,
        extra={
            'custom_fields': custom_fields,
            'vector_results': results_count
        }
    )