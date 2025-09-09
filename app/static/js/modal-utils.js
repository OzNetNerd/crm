/**
 * Modal Utilities - Simple helpers to reduce inline code in templates
 * 
 * This file provides common patterns and utilities used across modals
 * without overengineering the solution.
 */

/**
 * Common utility functions for modals
 */
window.ModalUtils = {
    /**
     * Format date for display
     */
    formatDate(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    },
    
    /**
     * Format currency
     */
    formatCurrency(amount) {
        if (!amount) return '$0';
        return '$' + new Intl.NumberFormat().format(amount);
    },
    
    /**
     * Capitalize string
     */
    capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
};

/**
 * Standard validation helper for templates
 */
window.validateAndSave = function(modalInstance, entityType, saveMethod) {
    if (modalInstance.validateEntity && !modalInstance.validateEntity(entityType)) {
        return false;
    }
    return modalInstance[saveMethod]();
};

console.log('Modal utilities loaded');