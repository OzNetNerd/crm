/**
 * Main Application JavaScript
 * Consolidates all initialization and utility functions
 */

// Disable autocomplete on all form fields
document.addEventListener('DOMContentLoaded', () => {
    // Disable autocomplete
    document.querySelectorAll('input, textarea, select').forEach(el => {
        el.setAttribute('autocomplete', 'off');
    });

    // Initialize modal handlers
    initializeModals();

    // Initialize dropdown handlers
    initializeDropdowns();

    // Initialize search functionality
    initializeSearch();
});

// Modal Functions
function initializeModals() {
    // Close modal on backdrop click
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-backdrop')) {
            const modal = e.target.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        }
    });

    // Close modal on close button click
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-close') || e.target.closest('.modal-close')) {
            const modal = e.target.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Dropdown Functions
function initializeDropdowns() {
    // Close dropdowns on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });

    // Toggle dropdown on trigger click
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('dropdown-trigger') || e.target.closest('.dropdown-trigger')) {
            e.preventDefault();
            const dropdown = e.target.closest('.dropdown');
            if (dropdown) {
                const menu = dropdown.querySelector('.dropdown-menu');
                if (menu) {
                    menu.classList.toggle('show');
                }
            }
        }
    });
}

function toggleDropdown(dropdownId) {
    const menu = document.getElementById(dropdownId);
    if (menu) {
        menu.classList.toggle('show');
    }
}

// Search Functions
function initializeSearch() {
    // Initialize search widgets
    document.querySelectorAll('.search-widget').forEach(widget => {
        const input = widget.querySelector('input');
        const button = widget.querySelector('button');
        const results = widget.querySelector('.search-results');

        if (input && button) {
            button.addEventListener('click', () => {
                performSearch(input.value, results);
            });

            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    performSearch(input.value, results);
                }
            });
        }
    });
}

function performSearch(query, resultsContainer) {
    // Implement search logic here
    console.log('Searching for:', query);
}

// Entity Selection (for search results)
document.addEventListener('click', (e) => {
    if (e.target.dataset.entitySelect) {
        e.preventDefault();
        const fieldId = e.target.dataset.entitySelect;
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = e.target.dataset.entityTitle;
            field.dataset.entityId = e.target.dataset.entityId;
            field.dataset.entityType = e.target.dataset.entityType;
        }
        // Close search results
        const results = field?.closest('.search-widget')?.querySelector('.search-results');
        if (results) {
            results.innerHTML = '';
        }
    }
});

// Advanced Search Modal
function closeAdvancedSearchModal() {
    closeModal('advanced-search-modal');
}

// Confirmation Modal
function confirmAction(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        // Trigger confirmation event
        modal.dispatchEvent(new CustomEvent('confirm'));
        closeModal(modalId);
    }
}

// Note: selectEntity and selectChoice functions are now handled by search-widget.js

// Export functions for global use
window.openModal = openModal;
window.closeModal = closeModal;
window.toggleDropdown = toggleDropdown;
window.closeAdvancedSearchModal = closeAdvancedSearchModal;
window.confirmAction = confirmAction;