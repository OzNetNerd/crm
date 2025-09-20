"""
CRM Logging Middleware
Provides request correlation and logging context for Flask requests
"""

import uuid
import time
from flask import g, request, session
from app.logging_config import routes_logger, performance_logger, log_htmx_request


class LoggingMiddleware:
    """
    Flask middleware to add request correlation and timing to all requests.

    Sets up request context for structured logging and tracks performance.
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the middleware with Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)

    def before_request(self):
        """Set up logging context before each request."""
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())[:8]

        # Extract user session information
        g.user_session = session.get('session_id') or f"anon_{g.request_id}"
        g.user_id = session.get('user_id')

        # Record request start time
        g.request_start_time = time.time()

        # Log the incoming request
        routes_logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'extra_fields': {
                    'request_id': g.request_id,
                    'method': request.method,
                    'path': request.path,
                    'query_string': request.query_string.decode(),
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'referer': request.headers.get('Referer', ''),
                    'content_type': request.content_type,
                    'content_length': request.content_length
                }
            }
        )

        # Log HTMX requests separately for frontend debugging
        if request.headers.get('HX-Request'):
            log_htmx_request(routes_logger)

    def after_request(self, response):
        """Log request completion and performance metrics."""
        if hasattr(g, 'request_start_time'):
            # Calculate request duration
            duration_ms = (time.time() - g.request_start_time) * 1000

            # Log request completion
            routes_logger.info(
                f"Request completed: {request.method} {request.path} - {response.status_code}",
                extra={
                    'extra_fields': {
                        'request_id': getattr(g, 'request_id', 'unknown'),
                        'status_code': response.status_code,
                        'duration_ms': round(duration_ms, 2),
                        'response_size': self._get_safe_response_size(response),
                        'is_htmx': bool(request.headers.get('HX-Request'))
                    }
                }
            )

            # Log performance warnings for slow requests
            if duration_ms > 1000:  # Warn for requests over 1 second
                performance_logger.warning(
                    f"Slow request detected: {request.method} {request.path}",
                    extra={
                        'extra_fields': {
                            'request_id': getattr(g, 'request_id', 'unknown'),
                            'duration_ms': round(duration_ms, 2),
                            'slow_request': True
                        }
                    }
                )

        return response

    def _get_safe_response_size(self, response):
        """Safely get response size without breaking static file serving."""
        try:
            # For static files and other responses that can't use get_data()
            if hasattr(response, 'content_length') and response.content_length:
                return response.content_length

            # For dynamic content, try to get actual data length
            data = response.get_data()
            return len(data) if data else 0
        except RuntimeError:
            # Static files in passthrough mode - use content-length header or 0
            return response.content_length or 0

    def teardown_request(self, exception=None):
        """Clean up request context and log any exceptions."""
        if exception:
            routes_logger.error(
                f"Request failed with exception: {str(exception)}",
                extra={
                    'extra_fields': {
                        'request_id': getattr(g, 'request_id', 'unknown'),
                        'exception_type': type(exception).__name__,
                        'exception_message': str(exception),
                        'request_path': request.path if request else 'unknown',
                        'request_method': request.method if request else 'unknown'
                    }
                },
                exc_info=True
            )