/**
 * Modal form validation functionality
 * Handles auto-focus, escape key handling, and required field validation
 */

/**
 * Initialize modal validation for a given modal element
 * @param {HTMLElement} modal - The modal element to initialize
 */
function initializeModalValidation(modal) {
    const form = modal.querySelector('form');
    const saveButton = modal.querySelector('#modal-save-button');

    if (!form || !saveButton) return;

    // Get all required fields
    const requiredFields = form.querySelectorAll('input[required], select[required], textarea[required]');

    // Function to check if all required fields are filled
    function checkRequiredFields() {
        let allFilled = true;

        requiredFields.forEach(field => {
            if (field.type === 'checkbox') {
                if (!field.checked) allFilled = false;
            } else {
                if (!field.value.trim()) allFilled = false;
            }
        });

        saveButton.disabled = !allFilled;
    }

    // Initial check
    checkRequiredFields();

    // Add event listeners to all form inputs
    const allInputs = form.querySelectorAll('input, select, textarea');
    allInputs.forEach(input => {
        input.addEventListener('input', checkRequiredFields);
        input.addEventListener('change', checkRequiredFields);
    });
}

/**
 * Auto-focus modal and initialize validation on DOM content loaded
 */
function initializeModalFocus() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.focus();
        initializeModalValidation(modal);
    }
}

/**
 * Handle HTMX after swap events to focus and validate new modals
 */
function handleModalAfterSwap(event) {
    const modal = event.target.querySelector('.modal-overlay');
    if (modal) {
        modal.focus();
        initializeModalValidation(modal);
    }
}

// Initialize when document loads
document.addEventListener('DOMContentLoaded', initializeModalFocus);

// Handle HTMX swapped content
document.addEventListener('htmx:afterSwap', handleModalAfterSwap);

// Export functions for module usage
export { initializeModalValidation, initializeModalFocus, handleModalAfterSwap };