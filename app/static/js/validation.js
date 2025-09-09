/**
 * Centralized Validation Module
 * 
 * This module consolidates all validation logic to eliminate duplication
 * across modal templates and provides consistent validation patterns.
 */

/**
 * Validation Rules - Common validation functions
 */
const ValidationRules = {
    /**
     * Check if value is not empty
     */
    required: (value, fieldName = 'Field') => {
        if (!value || !value.toString().trim()) {
            return { isValid: false, message: `${fieldName} is required` };
        }
        return { isValid: true };
    },

    /**
     * Validate email format
     */
    email: (value, fieldName = 'Email') => {
        if (!value) return { isValid: true }; // Allow empty unless required
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            return { isValid: false, message: `${fieldName} must be a valid email address` };
        }
        return { isValid: true };
    },

    /**
     * Validate URL format
     */
    url: (value, fieldName = 'URL') => {
        if (!value) return { isValid: true }; // Allow empty unless required
        const urlRegex = /^https?:\/\/.+\..+/;
        if (!urlRegex.test(value)) {
            return { isValid: false, message: `${fieldName} must be a valid URL (http:// or https://)` };
        }
        return { isValid: true };
    },

    /**
     * Validate phone number format
     */
    phone: (value, fieldName = 'Phone') => {
        if (!value) return { isValid: true }; // Allow empty unless required
        const phoneRegex = /^[\+]?[\d\s\-\(\)]{7,15}$/;
        if (!phoneRegex.test(value)) {
            return { isValid: false, message: `${fieldName} must be a valid phone number` };
        }
        return { isValid: true };
    },

    /**
     * Validate date format
     */
    date: (value, fieldName = 'Date') => {
        if (!value) return { isValid: true }; // Allow empty unless required
        const date = new Date(value);
        if (isNaN(date.getTime())) {
            return { isValid: false, message: `${fieldName} must be a valid date` };
        }
        return { isValid: true };
    },

    /**
     * Validate numeric value
     */
    number: (value, fieldName = 'Value') => {
        if (!value) return { isValid: true }; // Allow empty unless required
        if (isNaN(value)) {
            return { isValid: false, message: `${fieldName} must be a number` };
        }
        return { isValid: true };
    },

    /**
     * Validate minimum length
     */
    minLength: (minLen) => (value, fieldName = 'Field') => {
        if (!value) return { isValid: true }; // Allow empty unless required
        if (value.toString().length < minLen) {
            return { isValid: false, message: `${fieldName} must be at least ${minLen} characters long` };
        }
        return { isValid: true };
    },

    /**
     * Validate maximum length
     */
    maxLength: (maxLen) => (value, fieldName = 'Field') => {
        if (!value) return { isValid: true }; // Allow empty unless required
        if (value.toString().length > maxLen) {
            return { isValid: false, message: `${fieldName} must be no more than ${maxLen} characters long` };
        }
        return { isValid: true };
    },

    /**
     * Validate range for numbers
     */
    range: (min, max) => (value, fieldName = 'Value') => {
        if (!value) return { isValid: true }; // Allow empty unless required
        const num = parseFloat(value);
        if (isNaN(num) || num < min || num > max) {
            return { isValid: false, message: `${fieldName} must be between ${min} and ${max}` };
        }
        return { isValid: true };
    }
};

/**
 * Entity-specific validation schemas
 */
const ValidationSchemas = {
    task: {
        description: [ValidationRules.required, ValidationRules.minLength(3)],
        due_date: [ValidationRules.date],
        priority: [ValidationRules.required],
        next_step_type: [], // Optional field
        status: [] // Optional field, defaults are provided
    },

    contact: {
        name: [ValidationRules.required, ValidationRules.minLength(2)],
        role: [ValidationRules.maxLength(100)],
        email: [ValidationRules.email],
        phone: [ValidationRules.phone],
        company_id: [] // Optional field
    },

    company: {
        name: [ValidationRules.required, ValidationRules.minLength(2)],
        industry: [ValidationRules.maxLength(100)],
        size: [],
        website: [ValidationRules.url],
        phone: [ValidationRules.phone],
        address: [ValidationRules.maxLength(255)]
    },

    opportunity: {
        name: [ValidationRules.required, ValidationRules.minLength(3)],
        company_id: [ValidationRules.required],
        value: [ValidationRules.number, ValidationRules.range(0, 999999999)],
        probability: [ValidationRules.number, ValidationRules.range(0, 100)],
        expected_close_date: [ValidationRules.date],
        stage: [ValidationRules.required]
    }
};

/**
 * Field Display Names - Prettier field names for error messages
 */
const FieldDisplayNames = {
    // Common fields
    name: 'Name',
    description: 'Description',
    due_date: 'Due Date',
    priority: 'Priority',
    status: 'Status',
    created_at: 'Created Date',
    updated_at: 'Updated Date',
    
    // Contact fields
    role: 'Role/Title',
    email: 'Email Address',
    phone: 'Phone Number',
    company_id: 'Company',
    
    // Company fields
    industry: 'Industry',
    size: 'Company Size',
    website: 'Website',
    address: 'Address',
    
    // Opportunity fields
    value: 'Value',
    probability: 'Probability',
    expected_close_date: 'Expected Close Date',
    stage: 'Stage',
    
    // Task fields
    next_step_type: 'Next Step Type',
    entity_type: 'Related To',
    entity_id: 'Related Item'
};

/**
 * Validation Engine - Main validation logic
 */
class ValidationEngine {
    /**
     * Validate a single field against its rules
     * @param {any} value - Value to validate
     * @param {Array} rules - Array of validation rule functions
     * @param {string} fieldName - Display name for the field
     * @returns {Object} { isValid: boolean, message: string }
     */
    static validateField(value, rules = [], fieldName = 'Field') {
        for (const rule of rules) {
            const result = rule(value, fieldName);
            if (!result.isValid) {
                return result;
            }
        }
        return { isValid: true };
    }

    /**
     * Validate an entire entity object
     * @param {Object} entity - Entity object to validate
     * @param {string} entityType - Type of entity (task, contact, etc.)
     * @returns {Object} { isValid: boolean, errors: Object }
     */
    static validateEntity(entity, entityType) {
        const schema = ValidationSchemas[entityType];
        if (!schema) {
            console.warn(`No validation schema found for entity type: ${entityType}`);
            return { isValid: true, errors: {} };
        }

        const errors = {};
        let isValid = true;

        for (const [field, rules] of Object.entries(schema)) {
            const displayName = FieldDisplayNames[field] || field;
            const value = entity[field];
            const result = this.validateField(value, rules, displayName);
            
            if (!result.isValid) {
                errors[field] = result.message;
                isValid = false;
            }
        }

        return { isValid, errors };
    }

    /**
     * Show validation errors to user
     * @param {Object} errors - Errors object from validateEntity
     * @param {string} containerId - ID of container to show errors in
     */
    static displayErrors(errors, containerId = 'modal-errors') {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Clear existing errors
        container.innerHTML = '';

        if (Object.keys(errors).length === 0) {
            container.style.display = 'none';
            return;
        }

        // Create error list
        const errorList = document.createElement('ul');
        errorList.className = 'list-disc list-inside space-y-1 text-sm text-red-600';

        for (const message of Object.values(errors)) {
            const errorItem = document.createElement('li');
            errorItem.textContent = message;
            errorList.appendChild(errorItem);
        }

        container.appendChild(errorList);
        container.style.display = 'block';
    }

    /**
     * Add visual indicators to invalid fields
     * @param {Object} errors - Errors object from validateEntity
     */
    static highlightErrorFields(errors) {
        // Remove existing error highlights
        document.querySelectorAll('.border-red-500').forEach(field => {
            field.classList.remove('border-red-500');
            field.classList.add('border-gray-300');
        });

        // Add error highlights to invalid fields
        for (const field of Object.keys(errors)) {
            const input = document.querySelector(`[x-model*="${field}"]`);
            if (input) {
                input.classList.remove('border-gray-300');
                input.classList.add('border-red-500');
            }
        }
    }

    /**
     * Custom validation for complex scenarios
     * @param {Object} entity - Entity object
     * @param {string} entityType - Type of entity
     * @returns {Object} { isValid: boolean, errors: Object }
     */
    static customValidation(entity, entityType) {
        const errors = {};
        let isValid = true;

        // Task-specific validation
        if (entityType === 'task') {
            // If task has a next_step_type, it should have a due_date
            if (entity.next_step_type && !entity.due_date) {
                errors.due_date = 'Due date is required when a next step is specified';
                isValid = false;
            }

            // Multi-task validation
            if (entity.task_type === 'multi' && entity.child_tasks) {
                if (entity.child_tasks.length === 0) {
                    errors.child_tasks = 'Multi-tasks must have at least one sub-task';
                    isValid = false;
                } else {
                    // Validate each child task
                    entity.child_tasks.forEach((childTask, index) => {
                        if (!childTask.description || !childTask.description.trim()) {
                            errors[`child_task_${index}`] = `Sub-task ${index + 1} description is required`;
                            isValid = false;
                        }
                    });
                }
            }
        }

        // Opportunity-specific validation
        if (entityType === 'opportunity') {
            // Closed opportunities should have probability of 0 or 100
            if ((entity.stage === 'closed_won' && entity.probability !== 100) ||
                (entity.stage === 'closed_lost' && entity.probability !== 0)) {
                errors.probability = 'Closed opportunities should have probability of 0% (lost) or 100% (won)';
                isValid = false;
            }

            // Value should be provided for qualified opportunities
            if (['qualified', 'proposal', 'negotiation'].includes(entity.stage) && 
                (!entity.value || entity.value <= 0)) {
                errors.value = 'Value should be specified for qualified opportunities';
                isValid = false;
            }
        }

        return { isValid, errors };
    }

    /**
     * Complete validation including custom rules
     * @param {Object} entity - Entity object to validate
     * @param {string} entityType - Type of entity
     * @returns {Object} { isValid: boolean, errors: Object }
     */
    static validateComplete(entity, entityType) {
        // Run standard validation
        const standardResult = this.validateEntity(entity, entityType);
        
        // Run custom validation
        const customResult = this.customValidation(entity, entityType);
        
        // Combine results
        const errors = { ...standardResult.errors, ...customResult.errors };
        const isValid = standardResult.isValid && customResult.isValid;
        
        return { isValid, errors };
    }
}

/**
 * Validation Mixin for Alpine.js components
 * Use this in modal components to add validation functionality
 */
const ValidationMixin = {
    // Validation state
    validationErrors: {},
    isValidating: false,
    
    /**
     * Validate the current entity
     * @param {string} entityType - Type of entity to validate
     * @returns {boolean} True if valid, false otherwise
     */
    validateEntity(entityType) {
        this.isValidating = true;
        const entityData = this[entityType] || this.entity;
        
        const result = ValidationEngine.validateComplete(entityData, entityType);
        this.validationErrors = result.errors;
        
        if (!result.isValid) {
            ValidationEngine.displayErrors(result.errors);
            ValidationEngine.highlightErrorFields(result.errors);
        } else {
            ValidationEngine.displayErrors({});
        }
        
        this.isValidating = false;
        return result.isValid;
    },
    
    /**
     * Clear validation errors
     */
    clearValidationErrors() {
        this.validationErrors = {};
        ValidationEngine.displayErrors({});
        ValidationEngine.highlightErrorFields({});
    },
    
    /**
     * Check if a specific field has an error
     * @param {string} fieldName - Name of the field
     * @returns {boolean} True if field has error
     */
    hasFieldError(fieldName) {
        return !!this.validationErrors[fieldName];
    },
    
    /**
     * Get error message for a specific field
     * @param {string} fieldName - Name of the field
     * @returns {string} Error message or empty string
     */
    getFieldError(fieldName) {
        return this.validationErrors[fieldName] || '';
    }
};

// Global availability
window.ValidationRules = ValidationRules;
window.ValidationSchemas = ValidationSchemas;
window.ValidationEngine = ValidationEngine;
window.ValidationMixin = ValidationMixin;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Validation system initialized');
});