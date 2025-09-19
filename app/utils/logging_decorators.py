"""
Logging Decorators for CRM Application
Provides easy-to-use decorators for adding logging to route handlers and functions
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional
from flask import request, g

from app.logging_config import (
    routes_logger,
    database_logger,
    forms_logger,
    performance_logger,
    log_function_call,
    log_function_result,
    log_database_operation,
    log_form_submission
)


def log_route(logger=None, level="INFO", log_args=True, log_result=True):
    """
    Decorator to add comprehensive logging to route handlers.

    Args:
        logger: Logger instance to use (defaults to routes_logger)
        level: Log level for function entry/exit
        log_args: Whether to log function arguments
        log_result: Whether to log function results

    Example:
        @app.route('/users')
        @log_route()
        def users_index():
            return render_template('users/index.html')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_logger = logger or routes_logger
            start_time = time.time()

            # Log function entry
            if log_args:
                log_function_call(
                    func_logger,
                    func.__name__,
                    {'args': args, 'kwargs': kwargs}
                )
            else:
                log_function_call(func_logger, func.__name__)

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Log successful completion
                execution_time = (time.time() - start_time) * 1000
                if log_result:
                    log_function_result(
                        func_logger,
                        func.__name__,
                        result,
                        execution_time
                    )
                else:
                    log_function_result(
                        func_logger,
                        func.__name__,
                        execution_time_ms=execution_time
                    )

                return result

            except Exception as e:
                # Log the exception
                execution_time = (time.time() - start_time) * 1000
                func_logger.error(
                    f"Route handler {func.__name__} failed: {str(e)}",
                    extra={
                        'extra_fields': {
                            'function_name': func.__name__,
                            'execution_time_ms': round(execution_time, 2),
                            'exception_type': type(e).__name__,
                            'request_path': request.path if request else 'unknown'
                        }
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_database_query(operation_type=None, table_name=None):
    """
    Decorator to log database operations with timing.

    Args:
        operation_type: Type of database operation (SELECT, INSERT, UPDATE, DELETE)
        table_name: Database table being operated on

    Example:
        @log_database_query(operation_type="SELECT", table_name="users")
        def get_user_by_id(user_id):
            return User.query.get(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                # Extract record ID if result has an ID
                record_id = None
                if hasattr(result, 'id'):
                    record_id = result.id
                elif isinstance(result, (list, tuple)) and result and hasattr(result[0], 'id'):
                    record_id = f"batch_of_{len(result)}"

                log_database_operation(
                    database_logger,
                    operation_type or "QUERY",
                    table_name or func.__name__,
                    record_id,
                    execution_time
                )

                return result

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                database_logger.error(
                    f"Database operation {func.__name__} failed: {str(e)}",
                    extra={
                        'extra_fields': {
                            'function_name': func.__name__,
                            'operation_type': operation_type,
                            'table_name': table_name,
                            'execution_time_ms': round(execution_time, 2),
                            'exception_type': type(e).__name__
                        }
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_form_processing(form_name=None):
    """
    Decorator to log form processing and validation.

    Args:
        form_name: Name of the form being processed

    Example:
        @log_form_processing("UserCreateForm")
        def create_user():
            form = UserCreateForm(request.form)
            if form.validate():
                # Process form
                pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                forms_logger.info(
                    f"Form processing completed: {form_name or func.__name__}",
                    extra={
                        'extra_fields': {
                            'function_name': func.__name__,
                            'form_name': form_name,
                            'execution_time_ms': round(execution_time, 2),
                            'request_method': request.method if request else 'unknown'
                        }
                    }
                )

                return result

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                forms_logger.error(
                    f"Form processing failed: {form_name or func.__name__}: {str(e)}",
                    extra={
                        'extra_fields': {
                            'function_name': func.__name__,
                            'form_name': form_name,
                            'execution_time_ms': round(execution_time, 2),
                            'exception_type': type(e).__name__
                        }
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_performance(threshold_ms=100, logger=None):
    """
    Decorator to log performance metrics and warn about slow operations.

    Args:
        threshold_ms: Threshold in milliseconds to log performance warnings
        logger: Logger instance to use (defaults to performance_logger)

    Example:
        @log_performance(threshold_ms=500)
        def expensive_calculation():
            # Some expensive operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            perf_logger = logger or performance_logger
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                extra_fields = {
                    'function_name': func.__name__,
                    'execution_time_ms': round(execution_time, 2),
                    'performance_threshold_ms': threshold_ms
                }

                if execution_time > threshold_ms:
                    perf_logger.warning(
                        f"Slow operation detected: {func.__name__} took {execution_time:.2f}ms",
                        extra={'extra_fields': {**extra_fields, 'slow_operation': True}}
                    )
                else:
                    perf_logger.debug(
                        f"Performance: {func.__name__} completed in {execution_time:.2f}ms",
                        extra={'extra_fields': extra_fields}
                    )

                return result

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                perf_logger.error(
                    f"Performance tracking failed for {func.__name__}: {str(e)}",
                    extra={
                        'extra_fields': {
                            'function_name': func.__name__,
                            'execution_time_ms': round(execution_time, 2),
                            'exception_type': type(e).__name__
                        }
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_template_render(template_name=None):
    """
    Decorator to log template rendering operations.

    Args:
        template_name: Name of the template being rendered

    Example:
        @log_template_render("users/index.html")
        def render_users_page():
            return render_template('users/index.html', users=users)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from app.logging_config import templates_logger, log_template_render
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                # Try to extract context keys if available
                context_keys = []
                if len(kwargs) > 0:
                    context_keys = list(kwargs.keys())

                log_template_render(
                    templates_logger,
                    template_name or func.__name__,
                    context_keys,
                    execution_time
                )

                return result

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                templates_logger.error(
                    f"Template rendering failed: {template_name or func.__name__}: {str(e)}",
                    extra={
                        'extra_fields': {
                            'function_name': func.__name__,
                            'template_name': template_name,
                            'execution_time_ms': round(execution_time, 2),
                            'exception_type': type(e).__name__
                        }
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator