/**
 * Modal form validation functionality
 * Handles auto-focus, escape key handling, and required field validation
 */

/**
 * Simple debounce function to limit validation frequency
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Initialize modal validation for a given modal element
 * @param {HTMLElement} modal - The modal element to initialize
 */
function initializeModalValidation(modal) {
    const form = modal.querySelector('form');
    const saveButton = modal.querySelector('#modal-save-button');

    if (!form || !saveButton) return;

    // Enhanced field detection: get all required fields including hidden inputs from dropdowns
    function getRequiredFields() {
        const allRequired = [];

        // Direct required fields
        const directRequired = form.querySelectorAll('input[required], select[required], textarea[required]');
        allRequired.push(...directRequired);

        // Hidden required fields (from styled dropdowns)
        const hiddenRequired = form.querySelectorAll('input[type="hidden"][required]');
        allRequired.push(...hiddenRequired);


        return allRequired;
    }

    // Function to check if a field has a valid value
    function isFieldFilled(field) {
        if (field.type === 'checkbox') {
            return field.checked;
        } else if (field.type === 'hidden') {
            // Hidden inputs from dropdowns should have non-empty values
            return field.value && field.value.trim() !== '';
        } else {
            return field.value && field.value.trim() !== '';
        }
    }

    // Function to check if all required fields are filled
    function checkRequiredFields() {
        const requiredFields = getRequiredFields();
        let allFilled = true;

        requiredFields.forEach(field => {
            if (!isFieldFilled(field)) {
                allFilled = false;
            }
        });


        saveButton.disabled = !allFilled;

    }

    // Add event listeners with enhanced selector to catch all form changes
    function addValidationListeners() {
        const allInputs = form.querySelectorAll('input, select, textarea');
        allInputs.forEach(input => {
            input.addEventListener('input', debouncedCheck);
            input.addEventListener('change', checkRequiredFields);
        });

        // Also listen for custom events from Alpine.js dropdowns
        form.addEventListener('dropdown:change', checkRequiredFields);
        form.addEventListener('alpine:change', checkRequiredFields);
    }

    // Create debounced validation function
    const debouncedCheck = debounce(checkRequiredFields, 150);

    // Progressive enhancement: disable save button only if JavaScript is working
    if (saveButton.hasAttribute('data-initial-disabled')) {
        saveButton.disabled = true;
        saveButton.removeAttribute('data-initial-disabled');
    }

    // Initial setup with delay to allow Alpine.js to initialize
    setTimeout(() => {
        addValidationListeners();
        checkRequiredFields(); // Initial check after components load
    }, 100);

    // Also run immediate validation for quick setup
    addValidationListeners();
    checkRequiredFields();

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