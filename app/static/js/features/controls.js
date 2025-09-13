/**
 * UI Controls functionality
 * Handles expand/collapse all functionality and other UI controls
 */

/**
 * Expand all details/accordion elements
 */
function expandAll() {
    document.querySelectorAll('details').forEach(d => d.open = true);
}

/**
 * Collapse all details/accordion elements
 */
function collapseAll() {
    document.querySelectorAll('details').forEach(d => d.open = false);
}

/**
 * Clear all checkbox selections
 */
function clearSelection() {
    document.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => cb.checked = false);
}

/**
 * Initialize controls event handlers
 */
function initializeControls() {
    // Handle expand all buttons
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-action="expand-all"]')) {
            event.preventDefault();
            const section = event.target.getAttribute('data-section');
            if (section) {
                // Section-specific expand
                document.querySelectorAll(`[data-group="${section}"] details`).forEach(d => d.open = true);
            } else {
                // Global expand
                expandAll();
            }
        }
    });

    // Handle collapse all buttons
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-action="collapse-all"]')) {
            event.preventDefault();
            const section = event.target.getAttribute('data-section');
            if (section) {
                // Section-specific collapse
                document.querySelectorAll(`[data-group="${section}"] details`).forEach(d => d.open = false);
            } else {
                // Global collapse
                collapseAll();
            }
        }
    });

    // Handle checkboxes that need event propagation stopped
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-stop-propagation]')) {
            event.stopPropagation();
        }
    });

    // Handle clear selection buttons
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-action="clear-selection"]')) {
            event.preventDefault();
            clearSelection();
        }
    });

    // Handle modal close buttons
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-action="close-modal"]')) {
            event.preventDefault();
            const modal = event.target.closest('.modal-overlay');
            if (modal) {
                modal.remove();
            }
        }
    });
}

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', initializeControls);

// Export functions for module usage
export { expandAll, collapseAll, initializeControls };