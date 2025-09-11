/**
 * Modal JavaScript Mixins - Essential base functionality for Alpine.js modals
 * 
 * Reduced to minimal functionality needed for HTMX-based application.
 * Most CRUD operations now handled server-side via HTMX forms.
 */

/**
 * Base modal mixin - common state and behavior for all modals
 * @param {Object} options - Configuration options
 * @returns {Object} Alpine.js data object with base modal functionality
 */
function createModalMixin(options = {}) {
    return {
        show: false,
        loading: false,
        
        // Basic modal control
        openModal() {
            this.show = true;
            if (this.onModalOpen) this.onModalOpen();
        },
        
        closeModal() {
            this.show = false;
            if (this.onModalClose) this.onModalClose();
        },
        
        // Loading state management
        setLoading(state) {
            this.loading = state;
        },
        
        // Basic error handling
        handleError(error) {
            console.error('Modal error:', error);
            if (this.onError) {
                this.onError(error);
            } else {
                alert('An error occurred. Please try again.');
            }
        },
        
        // Merge with custom options
        ...options
    };
}

// Global availability
window.createModalMixin = createModalMixin;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Essential modal mixins initialized');
});