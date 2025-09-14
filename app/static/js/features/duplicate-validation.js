/**
 * Universal duplicate validation for all entity forms
 * Simple, DRY approach using existing validation API
 */

function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Validate field for duplicates using the existing API endpoint
 */
async function validateField(fieldName, fieldValue, entityType = 'company') {
    if (!fieldValue.trim()) {
        return null; // Empty values are handled by required validation
    }

    try {
        const response = await fetch(`/api/validate/${entityType}/${fieldName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ value: fieldValue })
        });

        if (response.ok) {
            const result = await response.text();
            return result.trim() || null; // Return HTML error or null if valid
        }
    } catch (error) {
        console.warn('Validation check failed:', error);
    }

    return null; // On error, don't block user
}

/**
 * Initialize duplicate validation for form fields
 */
function initializeDuplicateValidation() {
    // Target name fields in all entity forms
    const nameFields = document.querySelectorAll('input[name="name"]');

    nameFields.forEach(field => {
        // Detect entity type from form action
        const form = field.closest('form');
        if (!form || !form.action) {
            return;
        }

        // Extract entity type from form action (e.g., /modals/Company/create -> company)
        const actionMatch = form.action.match(/\/modals\/(\w+)\//);
        if (!actionMatch) {
            return;
        }

        const entityType = actionMatch[1].toLowerCase();

        // Create validation message container
        let messageContainer = field.parentElement.querySelector('.validation-message');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.className = 'validation-message mt-1';
            field.parentElement.appendChild(messageContainer);
        }

        // Debounced validation function
        const debouncedValidate = debounce(async (value) => {
            const errorHtml = await validateField('name', value, entityType);

            if (errorHtml) {
                messageContainer.innerHTML = errorHtml;
                messageContainer.classList.add('text-red-600');
                field.style.borderColor = '#dc2626';
            } else {
                messageContainer.innerHTML = '';
                messageContainer.classList.remove('text-red-600');
                field.style.borderColor = '';
            }
        }, 500);

        // Add event listeners
        field.addEventListener('input', (e) => {
            debouncedValidate(e.target.value);
        });

        field.addEventListener('blur', (e) => {
            debouncedValidate(e.target.value);
        });
    });
}

// Initialize on DOM ready with delay to prevent race conditions
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initializeDuplicateValidation, 150); // Wait for modal-validation.js
});

// Initialize on HTMX content swap (for modals) with delay
document.addEventListener('htmx:afterSwap', (event) => {
    setTimeout(() => {
        console.debug('Duplicate validation: Initializing after HTMX swap');
        initializeDuplicateValidation();
    }, 200); // Wait for modal-validation.js initialization
});

// Export for module usage
export { initializeDuplicateValidation, validateField };