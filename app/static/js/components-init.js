/**
 * Component Initialization System
 * Loads and registers all Alpine.js plugins and components
 * Single entry point for all component JavaScript
 */

// Import Alpine plugins
import './alpine-plugins/dropdown.js';
import './alpine-plugins/modal.js';

// Component registry for auto-initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing CRM components...');

    // Auto-initialize components with data attributes
    initializeComponents();

    // Setup global event listeners
    setupGlobalListeners();

    console.log('CRM components initialized');
});

/**
 * Auto-initialize components based on data attributes
 */
function initializeComponents() {
    // Initialize dropdowns with data-dropdown attribute
    document.querySelectorAll('[data-dropdown]').forEach(el => {
        const config = {
            name: el.dataset.dropdownName || 'dropdown',
            multi: el.dataset.dropdownMulti === 'true',
            searchable: el.dataset.dropdownSearchable === 'true',
            placeholder: el.dataset.dropdownPlaceholder || 'Select option',
            selected: el.dataset.dropdownSelected ?
                (el.dataset.dropdownMulti === 'true' ?
                    JSON.parse(el.dataset.dropdownSelected) :
                    el.dataset.dropdownSelected) :
                null
        };

        // Set Alpine data if not already set
        if (!el._x_dataStack) {
            Alpine.data('dropdown-' + config.name, () => Alpine.$data('dropdown')(config));
        }
    });

    // Initialize modals with data-modal attribute
    document.querySelectorAll('[data-modal]').forEach(el => {
        const config = {
            id: el.dataset.modalId || 'modal',
            title: el.dataset.modalTitle || '',
            size: el.dataset.modalSize || 'md',
            closable: el.dataset.modalClosable !== 'false',
            closeOnBackdrop: el.dataset.modalCloseOnBackdrop !== 'false',
            closeOnEscape: el.dataset.modalCloseOnEscape !== 'false'
        };

        // Set Alpine data if not already set
        if (!el._x_dataStack) {
            Alpine.data('modal-' + config.id, () => Alpine.$data('modal')(config));
        }
    });
}

/**
 * Setup global event listeners for dynamic content
 */
function setupGlobalListeners() {
    // Listen for HTMX content swaps to reinitialize components
    document.body.addEventListener('htmx:afterSwap', (event) => {
        // Reinitialize components in the swapped content
        const target = event.detail.target;
        if (target) {
            initializeComponentsInElement(target);
        }
    });

    // Listen for dynamic modal opens
    document.body.addEventListener('open:modal', (event) => {
        const modalId = event.detail.id;
        if (modalId && Alpine.store('modals')) {
            Alpine.store('modals').open(modalId);
        }
    });

    // Listen for dynamic modal closes
    document.body.addEventListener('close:modal', (event) => {
        const modalId = event.detail.id;
        if (modalId && Alpine.store('modals')) {
            Alpine.store('modals').close(modalId);
        }
    });
}

/**
 * Initialize components within a specific element
 */
function initializeComponentsInElement(element) {
    // Find and initialize dropdowns
    element.querySelectorAll('[data-dropdown]').forEach(el => {
        if (!el._x_dataStack) {
            initializeDropdown(el);
        }
    });

    // Find and initialize modals
    element.querySelectorAll('[data-modal]').forEach(el => {
        if (!el._x_dataStack) {
            initializeModal(el);
        }
    });
}

/**
 * Helper function to initialize a dropdown element
 */
function initializeDropdown(element) {
    const config = parseDropdownConfig(element);
    Alpine.initTree(element);
}

/**
 * Helper function to initialize a modal element
 */
function initializeModal(element) {
    const config = parseModalConfig(element);
    Alpine.initTree(element);
}

/**
 * Parse dropdown configuration from element attributes
 */
function parseDropdownConfig(element) {
    return {
        name: element.dataset.dropdownName || 'dropdown',
        multi: element.dataset.dropdownMulti === 'true',
        searchable: element.dataset.dropdownSearchable === 'true',
        placeholder: element.dataset.dropdownPlaceholder || 'Select option',
        options: element.dataset.dropdownOptions ?
            JSON.parse(element.dataset.dropdownOptions) : [],
        selected: element.dataset.dropdownSelected ?
            (element.dataset.dropdownMulti === 'true' ?
                JSON.parse(element.dataset.dropdownSelected) :
                element.dataset.dropdownSelected) :
            null
    };
}

/**
 * Parse modal configuration from element attributes
 */
function parseModalConfig(element) {
    return {
        id: element.dataset.modalId || 'modal',
        title: element.dataset.modalTitle || '',
        size: element.dataset.modalSize || 'md',
        closable: element.dataset.modalClosable !== 'false',
        closeOnBackdrop: element.dataset.modalCloseOnBackdrop !== 'false',
        closeOnEscape: element.dataset.modalCloseOnEscape !== 'false'
    };
}

// Export for use in other scripts
window.CRMComponents = {
    initializeComponents,
    initializeComponentsInElement,
    initializeDropdown,
    initializeModal
};