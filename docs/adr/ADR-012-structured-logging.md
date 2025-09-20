# ADR-012: Structured Logging Framework Implementation

## Status
Accepted

## Context

The CRM application requires comprehensive logging for troubleshooting, monitoring, and debugging complex form operations like MEDDPICC dropdown processing. The existing basic Flask logging is insufficient for:

1. **Request Correlation**: Tracking user actions across multiple requests
2. **Form Processing Debugging**: Understanding validation failures and data transformation issues
3. **Performance Monitoring**: Identifying slow operations and bottlenecks
4. **Error Context**: Capturing detailed state information when errors occur
5. **Cross-Service Consistency**: Matching the structured logging already implemented in the chatbot service

## Decision

We will implement a comprehensive structured logging framework across all CRM services using JSON-formatted logs with standardized fields for correlation and analysis.

### Core Principles

1. **Structured JSON Format**: All logs use consistent JSON structure
2. **Request Correlation**: Every request gets a unique ID that tracks across all operations
3. **Service Consistency**: Same logging format across CRM and chatbot services
4. **Detailed Context**: Capture sufficient context for debugging without exposing sensitive data
5. **Performance Tracking**: Include timing information for operations
6. **Error Context**: Comprehensive error information with call stacks

### Standard Log Structure

```json
{
  "timestamp": "2025-09-20T08:58:00.123Z",
  "level": "INFO",
  "service": "crm-service",
  "component": "forms.stakeholder",
  "message": "MEDDPICC roles processing completed",
  "request_id": "req-123456789",
  "session_id": "sess-abc123",
  "user_id": "user-456",
  "request_method": "POST",
  "request_path": "/modals/stakeholder/5/edit",
  "entity_type": "stakeholder",
  "entity_id": 5,
  "form_operation": "meddpicc_roles_update",
  "database_operation": "update",
  "response_time_ms": 45.6,
  "custom_fields": {
    "operation": "meddpicc_roles_assignment",
    "previous_roles": ["user"],
    "new_roles": ["economic_buyer", "champion"],
    "roles_added": ["economic_buyer", "champion"],
    "roles_removed": ["user"],
    "success": true
  }
}
```

## Implementation

### 1. Core Logging Infrastructure

- **CRMStructuredFormatter**: JSON formatter for consistent log structure
- **request_logging_middleware**: Flask middleware for request correlation
- **Context Management**: Thread-safe request context using Flask's `g` object

### 2. Specialized Loggers

- **FormLogger**: Form validation, submission, and processing
- **MEDDPICCLogger**: MEDDPICC role assignment operations
- **TemplateRenderLogger**: Template rendering and form display
- **DatabaseLogger**: Entity CRUD operations and relationship changes

### 3. Integration Points

- **Flask Application**: Setup during app initialization
- **Route Handlers**: Automatic request/response logging
- **Form Processing**: Detailed validation and processing logs
- **Database Operations**: Entity change tracking
- **Error Handlers**: Enhanced error context capture

### 4. Key Features

#### Request Correlation
- Unique request ID for each HTTP request
- Session ID tracking for user sessions
- User ID when authenticated
- Correlation headers in responses

#### Form Operation Logging
- Form submission attempts with complete field data
- Validation failures with specific field errors
- Data transformation tracking (especially for SelectMultipleField)
- MEDDPICC role processing steps

#### Database Operation Logging
- Entity creation, updates, and deletions
- Relationship changes (many-to-many assignments)
- Query execution timing
- Transaction state tracking

#### Error Context Logging
- Complete exception stack traces
- Request state at time of error
- Form data that caused the error (sanitized)
- Database transaction state

## Benefits

### Current MEDDPICC Issue Debugging
- **Form Submission Tracking**: See exactly what data is submitted from the dropdown
- **Validation Detail**: Understand why SelectMultipleField validation fails
- **Data Transformation**: Track JSON to field conversion
- **Template Rendering**: Debug form field display issues

### Future Troubleshooting
- **Performance Monitoring**: Identify slow form operations
- **Error Pattern Analysis**: Detect recurring issues across users
- **User Behavior Tracking**: Understand how users interact with forms
- **System Health**: Monitor overall application performance

### Operational Benefits
- **Centralized Logging**: All services use same format for log aggregation
- **Debugging Efficiency**: Faster issue resolution with detailed context
- **Monitoring Integration**: Easy integration with log analysis tools
- **Audit Trail**: Complete history of entity changes

## Configuration

### Log Levels
- **DEBUG**: Detailed execution flow and variable states
- **INFO**: Normal operations, form submissions, entity changes
- **WARNING**: Validation failures, recoverable errors
- **ERROR**: Exceptions, failed operations, system errors

### Sensitive Data Handling
- Password fields are redacted
- Large text fields are truncated
- PII is masked when configured
- Token and secret values are redacted

### Performance Considerations
- Asynchronous logging for high-throughput operations
- Log level filtering to control verbosity
- Structured data size limits to prevent memory issues
- Optional fields for non-critical information

## Migration Strategy

### Phase 1: Core Infrastructure
1. Implement CRMStructuredFormatter and middleware
2. Initialize structured logging in Flask app
3. Update error handlers for enhanced context

### Phase 2: Form Operations
1. Add form processing logs to modal handlers
2. Implement MEDDPICC-specific logging
3. Add template rendering logs

### Phase 3: Database Operations
1. Add entity operation logging
2. Implement relationship change tracking
3. Add query performance monitoring

### Phase 4: Enhancement
1. Add user behavior analytics
2. Implement log aggregation and analysis
3. Create operational dashboards

## Compliance and Standards

### Data Privacy
- No sensitive user data in logs (passwords, tokens)
- Configurable PII redaction
- Log retention policies
- Access control for log data

### Performance Standards
- Logging overhead < 5% of request processing time
- Non-blocking log operations
- Graceful degradation if logging fails

### Consistency Standards
- Same JSON schema across all services
- Standardized field names and types
- Common correlation mechanisms
- Unified timestamp formats

## Files Created/Modified

### New Files
- `app/utils/logging_config.py` - Core logging infrastructure
- `app/utils/form_logger.py` - Form-specific logging utilities
- `docs/adr/ADR-012-structured-logging.md` - This documentation

### Modified Files
- `app/main.py` - Initialize structured logging
- `app/routes/web/modals.py` - Add form processing logs
- `app/forms/entities/stakeholder.py` - Add validation logging
- `app/models/base.py` - Add database operation logging

## Success Criteria

1. **Debugging Efficiency**: Reduce time to identify form processing issues by 75%
2. **Error Context**: 100% of errors include request correlation and sufficient context
3. **Performance Visibility**: All form operations include timing information
4. **MEDDPICC Transparency**: Complete visibility into role assignment process
5. **Service Consistency**: Same logging format across CRM and chatbot services

## Consequences

### Positive
- Dramatically improved debugging and troubleshooting capabilities
- Better system monitoring and performance insights
- Consistent logging across all services
- Detailed audit trail for compliance

### Negative
- Increased log volume and storage requirements
- Additional complexity in application code
- Potential performance overhead (mitigated by async logging)
- Learning curve for developers unfamiliar with structured logging

## Related ADRs
- ADR-009: Zero Duplicate Systems Policy (ensures logging utilities are reused)
- ADR-014: Ultra DRY Architecture (logging follows DRY principles)
- ADR-015: Python Code Standards (logging code follows standards)