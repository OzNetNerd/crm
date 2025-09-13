# Architecture Decision Record (ADR)

## ADR-012: Structured Logging Framework with Cross-Service Correlation

**Status:** Accepted  
**Date:** 13-09-25-12h-45m-00s  
**Session:** /home/will/.claude/projects/-home-will-code-crm--worktrees-adr-check/afc3ed2f-fdb0-4480-b02c-ea658e7d7589.jsonl  
**Todo:** /home/will/.claude/todos/afc3ed2f-fdb0-4480-b02c-ea658e7d7589-agent-*.json  
**Deciders:** Will Robinson, Development Team

### Context

The CRM application uses a microservices architecture (Flask CRM service + FastAPI chatbot service) but lacks comprehensive logging strategy. Current issues:

- **Inconsistent Logging**: Different services use different logging patterns and formats
- **No Correlation**: Cannot trace requests across CRM and chatbot services
- **Poor Debugging**: Difficult to troubleshoot issues spanning multiple services
- **No Structured Data**: Log messages are plain text, making analysis difficult
- **Missing JavaScript Logging**: Frontend errors and interactions not captured
- **No Log Aggregation**: Logs scattered across different service outputs

The microservices architecture requires coordinated logging to maintain system observability and enable effective debugging.

### Decision

**We will implement a comprehensive structured logging framework with cross-service correlation:**

1. **Structured JSON Logging**: All services output JSON logs with consistent schema
2. **Request Correlation**: Unique request IDs traced across all services and components
3. **Standardized Log Levels**: Consistent DEBUG, INFO, WARNING, ERROR, CRITICAL usage
4. **JavaScript Logging Integration**: Frontend logging correlated with backend requests
5. **Service Context**: Each log entry identifies originating service and component
6. **Performance Logging**: Request timing and performance metrics in structured format

**Logging Architecture:**
```
Frontend JS → Request ID → CRM Service → Chatbot Service → Shared Log Format
     ↓              ↓           ↓              ↓              ↓
Browser Console  Session ID  Flask Logs  FastAPI Logs  JSON Structure
```

### Rationale

**Primary drivers:**

- **System Observability**: Understand behavior across distributed CRM services
- **Debugging Efficiency**: Trace issues from frontend through all backend services  
- **Performance Monitoring**: Structured metrics for optimization identification
- **Production Support**: Effective troubleshooting of live system issues
- **Compliance**: Structured logs enable audit trails and security monitoring

**Technical benefits:**

- JSON logs enable automated parsing and analysis tools
- Request correlation allows full request lifecycle tracking
- Structured data supports log aggregation and dashboard creation
- Consistent format reduces cognitive load when debugging across services
- Performance metrics enable data-driven optimization decisions

### Alternatives Considered

- **Option A: Plain text logging** - Rejected due to analysis difficulty and poor structure
- **Option B: Service-specific logging** - Rejected due to lack of cross-service correlation
- **Option C: External logging service** - Rejected due to data privacy and complexity
- **Option D: Minimal logging approach** - Rejected due to debugging and monitoring requirements

### Consequences

**Positive:**

- ✅ **Enhanced Debugging**: Full request tracing across CRM and chatbot services
- ✅ **Performance Visibility**: Structured timing data for optimization opportunities
- ✅ **System Monitoring**: Automated log analysis and alerting capabilities
- ✅ **Audit Compliance**: Complete audit trails for security and compliance requirements
- ✅ **Developer Productivity**: Faster issue resolution with correlated logs
- ✅ **Production Support**: Effective troubleshooting of live system issues

**Negative:**

- ➖ **Log Volume**: Structured logging increases storage requirements
- ➖ **Performance Overhead**: JSON serialization adds minimal processing cost
- ➖ **Complexity**: Need to manage correlation IDs across service boundaries
- ➖ **Implementation Effort**: Requires updating all services and frontend code

**Neutral:**

- 🔄 **Log Analysis Tools**: May need tools for JSON log parsing and analysis
- 🔄 **Storage Management**: Need log rotation and archival strategy
- 🔄 **Team Training**: Developers must understand structured logging patterns

### Implementation Notes

**Python Logging Configuration:**
```python
# app/utils/logging/config.py
import logging
import json
import uuid
from datetime import datetime
from flask import request, g

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'service': 'crm-service',
            'component': record.name,
            'message': record.getMessage(),
            'request_id': getattr(g, 'request_id', None),
            'user_id': getattr(g, 'user_id', None),
            'session_id': getattr(g, 'session_id', None),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add custom fields
        if hasattr(record, 'custom_fields'):
            log_entry.update(record.custom_fields)
            
        return json.dumps(log_entry)

def setup_logging(app):
    """Configure structured logging for Flask app"""
    formatter = StructuredFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    
    # Add request ID to all requests
    @app.before_request
    def before_request():
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.session_id = request.headers.get('X-Session-ID')
        g.user_id = getattr(request, 'user_id', None)
```

**FastAPI Chatbot Service Logging:**
```python
# services/chatbot/logging_config.py
import logging
import json
import uuid
from datetime import datetime
from fastapi import Request
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar('request_id')

class ChatbotFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'service': 'chatbot-service',
            'component': record.name,
            'message': record.getMessage(),
            'request_id': request_id_var.get(None),
        }
        
        if hasattr(record, 'ai_model'):
            log_entry['ai_model'] = record.ai_model
        if hasattr(record, 'response_time'):
            log_entry['response_time_ms'] = record.response_time
            
        return json.dumps(log_entry)

async def log_requests(request: Request, call_next):
    """Middleware to add request correlation"""
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    request_id_var.set(request_id)
    
    start_time = datetime.utcnow()
    response = await call_next(request)
    end_time = datetime.utcnow()
    
    logging.info(
        "Request processed",
        extra={
            'custom_fields': {
                'request_id': request_id,
                'method': request.method,
                'url': str(request.url),
                'status_code': response.status_code,
                'response_time_ms': (end_time - start_time).total_seconds() * 1000
            }
        }
    )
    
    response.headers['X-Request-ID'] = request_id
    return response
```

**JavaScript Logging Integration:**
```javascript
// app/static/js/logging.js
class StructuredLogger {
    constructor() {
        this.requestId = this.getRequestId();
        this.sessionId = this.getSessionId();
    }
    
    getRequestId() {
        // Extract from meta tag or generate
        return document.querySelector('meta[name="request-id"]')?.content || 
               crypto.randomUUID();
    }
    
    getSessionId() {
        return document.querySelector('meta[name="session-id"]')?.content;
    }
    
    log(level, message, context = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            level: level,
            service: 'crm-frontend',
            component: 'javascript',
            message: message,
            request_id: this.requestId,
            session_id: this.sessionId,
            url: window.location.pathname,
            user_agent: navigator.userAgent,
            ...context
        };
        
        // Send to backend logging endpoint
        if (level === 'ERROR' || level === 'WARNING') {
            this.sendToBackend(logEntry);
        }
        
        console.log(JSON.stringify(logEntry));
    }
    
    async sendToBackend(logEntry) {
        try {
            await fetch('/api/logs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Request-ID': this.requestId
                },
                body: JSON.stringify(logEntry)
            });
        } catch (error) {
            console.error('Failed to send log to backend:', error);
        }
    }
    
    info(message, context) { this.log('INFO', message, context); }
    warning(message, context) { this.log('WARNING', message, context); }
    error(message, context) { this.log('ERROR', message, context); }
}

// Global logger instance
window.logger = new StructuredLogger();

// Automatic error logging
window.addEventListener('error', (event) => {
    logger.error('JavaScript Error', {
        error_message: event.message,
        filename: event.filename,
        line: event.lineno,
        column: event.colno,
        stack: event.error?.stack
    });
});
```

**Log Schema Definition:**
```json
{
    "timestamp": "2025-09-13T12:45:30.123Z",
    "level": "INFO|DEBUG|WARNING|ERROR|CRITICAL",
    "service": "crm-service|chatbot-service|crm-frontend",
    "component": "routes.companies|rag_engine|javascript",
    "message": "Human readable message",
    "request_id": "uuid4-string",
    "session_id": "session-identifier",
    "user_id": "authenticated-user-id",
    "custom_fields": {
        "entity_type": "company",
        "entity_id": 123,
        "response_time_ms": 45.2,
        "ai_model": "llama2"
    }
}
```

**Performance Logging Pattern:**
```python
import time
import logging

def log_performance(func):
    """Decorator for performance logging"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            end_time = time.time()
            logging.info(
                f"Function {func.__name__} completed",
                extra={
                    'custom_fields': {
                        'function_name': func.__name__,
                        'execution_time_ms': (end_time - start_time) * 1000,
                        'success': success,
                        'error': error
                    }
                }
            )
        return result
    return wrapper
```

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 13-09-25-12h-45m-00s | afc3ed2f-fdb0-4480-b02c-ea658e7d7589.jsonl | ADR gap analysis | Initial creation | Document logging framework strategy | Establish system observability and debugging standards |

---

**Impact Assessment:** High - This affects all services and enables comprehensive system monitoring.

**Review Required:** Mandatory - All developers must understand structured logging patterns and correlation.

**Next Steps:**
1. Implement structured logging configuration in both CRM and chatbot services
2. Add JavaScript logging integration to frontend templates
3. Create log analysis and monitoring dashboard
4. Establish log rotation and storage management strategy
5. Train team on structured logging patterns and debugging workflows