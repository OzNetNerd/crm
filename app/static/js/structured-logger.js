/**
 * Structured JavaScript Logging
 * ADR-012: Frontend Logging Integration
 * 
 * Provides structured logging for frontend with correlation to backend logs.
 * Supports error tracking, performance monitoring, and user interaction logging.
 */

class StructuredLogger {
    constructor() {
        this.requestId = this.getRequestId();
        this.sessionId = this.getSessionId();
        this.userId = this.getUserId();
        this.serviceName = 'crm-frontend';
        
        // Initialize automatic error logging
        this.setupErrorHandling();
        this.setupPerformanceLogging();
    }
    
    /**
     * Extract request ID from meta tag or generate new one
     */
    getRequestId() {
        const metaTag = document.querySelector('meta[name="request-id"]');
        if (metaTag && metaTag.content) {
            return metaTag.content;
        }
        
        // Generate new UUID if not found
        return this.generateUUID();
    }
    
    /**
     * Extract session ID from meta tag
     */
    getSessionId() {
        const metaTag = document.querySelector('meta[name="session-id"]');
        return metaTag ? metaTag.content : null;
    }
    
    /**
     * Extract user ID from meta tag
     */
    getUserId() {
        const metaTag = document.querySelector('meta[name="user-id"]');
        return metaTag ? metaTag.content : null;
    }
    
    /**
     * Generate UUID v4
     */
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    /**
     * Create structured log entry
     */
    createLogEntry(level, message, context = {}) {
        return {
            timestamp: new Date().toISOString(),
            level: level,
            service: this.serviceName,
            component: 'javascript',
            message: message,
            request_id: this.requestId,
            session_id: this.sessionId,
            user_id: this.userId,
            url: window.location.pathname,
            user_agent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            ...context
        };
    }
    
    /**
     * Log structured message
     */
    log(level, message, context = {}) {
        const logEntry = this.createLogEntry(level, message, context);
        
        // Send to backend for ERROR and WARNING levels
        if (level === 'ERROR' || level === 'WARNING') {
            this.sendToBackend(logEntry);
        }
        
        // Also log to console for development
        if (this.isDevelopment()) {
            console.log(JSON.stringify(logEntry, null, 2));
        }
    }
    
    /**
     * Log info level message
     */
    info(message, context = {}) {
        this.log('INFO', message, context);
    }
    
    /**
     * Log warning level message
     */
    warning(message, context = {}) {
        this.log('WARNING', message, context);
    }
    
    /**
     * Log error level message
     */
    error(message, context = {}) {
        this.log('ERROR', message, context);
    }
    
    /**
     * Log debug level message
     */
    debug(message, context = {}) {
        if (this.isDevelopment()) {
            this.log('DEBUG', message, context);
        }
    }
    
    /**
     * Send log entry to backend
     */
    async sendToBackend(logEntry) {
        try {
            await fetch('/api/logs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Request-ID': this.requestId,
                    'X-Session-ID': this.sessionId || '',
                },
                body: JSON.stringify(logEntry)
            });
        } catch (error) {
            // Fallback: log to console if backend logging fails
            console.error('Failed to send log to backend:', error);
            console.log('Original log entry:', logEntry);
        }
    }
    
    /**
     * Check if running in development mode
     */
    isDevelopment() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' ||
               window.location.search.includes('debug=true');
    }
    
    /**
     * Setup automatic error handling
     */
    setupErrorHandling() {
        // Global error handler
        window.addEventListener('error', (event) => {
            this.error('JavaScript Error', {
                error_message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno,
                stack: event.error?.stack,
                type: 'javascript_error'
            });
        });
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.error('Unhandled Promise Rejection', {
                reason: event.reason?.toString(),
                stack: event.reason?.stack,
                type: 'promise_rejection'
            });
        });
    }
    
    /**
     * Setup performance logging
     */
    setupPerformanceLogging() {
        // Log page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                const navigation = performance.getEntriesByType('navigation')[0];
                if (navigation) {
                    this.info('Page Load Performance', {
                        load_time_ms: navigation.loadEventEnd - navigation.fetchStart,
                        dom_ready_ms: navigation.domContentLoadedEventEnd - navigation.fetchStart,
                        dns_lookup_ms: navigation.domainLookupEnd - navigation.domainLookupStart,
                        connection_ms: navigation.connectEnd - navigation.connectStart,
                        response_ms: navigation.responseEnd - navigation.responseStart,
                        type: 'performance'
                    });
                }
            }, 100);
        });
    }
    
    /**
     * Log user interaction
     */
    logInteraction(action, element, details = {}) {
        this.info('User Interaction', {
            action: action,
            element: element,
            details: details,
            type: 'user_interaction'
        });
    }
    
    /**
     * Log API call
     */
    logApiCall(method, url, responseTime, statusCode, success = true) {
        const level = success ? 'INFO' : 'ERROR';
        this.log(level, 'API Call', {
            method: method,
            url: url,
            response_time_ms: responseTime,
            status_code: statusCode,
            success: success,
            type: 'api_call'
        });
    }
    
    /**
     * Log form submission
     */
    logFormSubmission(formName, success = true, errors = []) {
        const level = success ? 'INFO' : 'WARNING';
        this.log(level, 'Form Submission', {
            form_name: formName,
            success: success,
            errors: errors,
            type: 'form_submission'
        });
    }
    
    /**
     * Log entity operation
     */
    logEntityOperation(operation, entityType, entityId, success = true) {
        const level = success ? 'INFO' : 'ERROR';
        this.log(level, `Entity ${operation}`, {
            operation: operation,
            entity_type: entityType,
            entity_id: entityId,
            success: success,
            type: 'entity_operation'
        });
    }
}

// Global logger instance
window.structuredLogger = new StructuredLogger();

// Convenience methods for global access
window.logInfo = (message, context) => window.structuredLogger.info(message, context);
window.logWarning = (message, context) => window.structuredLogger.warning(message, context);
window.logError = (message, context) => window.structuredLogger.error(message, context);
window.logDebug = (message, context) => window.structuredLogger.debug(message, context);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StructuredLogger;
}