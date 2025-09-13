"""
Logging API Endpoints
ADR-012: Structured Logging Framework

API endpoints for receiving structured logs from frontend JavaScript.
Integrates with backend structured logging for complete request correlation.
"""

from flask import Blueprint, request, jsonify, g
from app.utils.logging.config import get_logger
import json

logs_bp = Blueprint('logs', __name__)
logger = get_logger(__name__)


@logs_bp.route('/logs', methods=['POST'])
def receive_frontend_log():
    """
    Receive structured log entry from frontend JavaScript.
    ADR-012: Frontend-backend log correlation.
    
    Expected JSON payload:
    {
        "timestamp": "2025-09-13T12:45:30.123Z",
        "level": "ERROR",
        "service": "crm-frontend", 
        "component": "javascript",
        "message": "JavaScript error occurred",
        "request_id": "uuid4-string",
        "session_id": "session-id",
        "user_id": "user-id",
        "custom_fields": {...}
    }
    
    Returns:
        JSON response confirming log receipt
    """
    try:
        # Parse log entry from request
        log_data = request.get_json()
        
        if not log_data:
            return jsonify({'error': 'No log data provided'}), 400
            
        # Extract required fields
        level = log_data.get('level', 'INFO').upper()
        message = log_data.get('message', 'Frontend log entry')
        component = log_data.get('component', 'javascript')
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level not in valid_levels:
            level = 'INFO'
        
        # Create custom fields for structured logging
        custom_fields = {
            'frontend_timestamp': log_data.get('timestamp'),
            'frontend_service': log_data.get('service', 'crm-frontend'),
            'frontend_component': component,
            'url': log_data.get('url'),
            'user_agent': log_data.get('user_agent'),
            'viewport': log_data.get('viewport'),
            'source': 'frontend'
        }
        
        # Add any additional custom fields from frontend
        if 'custom_fields' in log_data:
            custom_fields.update(log_data['custom_fields'])
        
        # Add type-specific fields
        if log_data.get('type') == 'javascript_error':
            custom_fields.update({
                'error_message': log_data.get('error_message'),
                'filename': log_data.get('filename'),
                'line': log_data.get('line'),
                'column': log_data.get('column'),
                'stack': log_data.get('stack')
            })
        elif log_data.get('type') == 'performance':
            custom_fields.update({
                'load_time_ms': log_data.get('load_time_ms'),
                'dom_ready_ms': log_data.get('dom_ready_ms'),
                'dns_lookup_ms': log_data.get('dns_lookup_ms'),
                'connection_ms': log_data.get('connection_ms'),
                'response_ms': log_data.get('response_ms')
            })
        elif log_data.get('type') == 'user_interaction':
            custom_fields.update({
                'action': log_data.get('action'),
                'element': log_data.get('element'),
                'details': log_data.get('details')
            })
        elif log_data.get('type') == 'api_call':
            custom_fields.update({
                'method': log_data.get('method'),
                'api_url': log_data.get('url'),
                'response_time_ms': log_data.get('response_time_ms'),
                'status_code': log_data.get('status_code'),
                'success': log_data.get('success')
            })
        
        # Update request correlation if provided
        frontend_request_id = log_data.get('request_id')
        frontend_session_id = log_data.get('session_id')
        frontend_user_id = log_data.get('user_id')
        
        if frontend_request_id and hasattr(g, 'request_id'):
            # Correlate with backend request ID
            custom_fields['frontend_request_id'] = frontend_request_id
            
        if frontend_session_id:
            custom_fields['frontend_session_id'] = frontend_session_id
            
        if frontend_user_id:
            custom_fields['frontend_user_id'] = frontend_user_id
        
        # Convert level string to logging level
        log_level_map = {
            'DEBUG': 20,
            'INFO': 20,
            'WARNING': 30,
            'ERROR': 40,
            'CRITICAL': 50
        }
        
        numeric_level = log_level_map.get(level, 20)
        
        # Log the frontend message through backend structured logging
        logger.log(
            numeric_level,
            f"Frontend: {message}",
            extra={'custom_fields': custom_fields}
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Log entry received and processed'
        })
        
    except json.JSONDecodeError:
        logger.error(
            "Invalid JSON in frontend log request",
            extra={'custom_fields': {'error': 'json_decode_error'}}
        )
        return jsonify({'error': 'Invalid JSON format'}), 400
        
    except Exception as e:
        logger.error(
            "Error processing frontend log",
            extra={'custom_fields': {'error': str(e)}},
            exc_info=True
        )
        return jsonify({'error': 'Internal server error'}), 500


@logs_bp.route('/logs/health', methods=['GET'])
def logging_health_check():
    """
    Health check endpoint for logging system.
    
    Returns:
        JSON response with logging system status
    """
    try:
        # Test structured logging
        logger.info(
            "Logging health check",
            extra={'custom_fields': {'check_type': 'health'}}
        )
        
        return jsonify({
            'status': 'healthy',
            'service': 'crm-service',
            'logging': 'structured',
            'correlation': 'enabled'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500