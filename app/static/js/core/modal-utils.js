/**
 * Modal Utilities - Centralized modal functionality
 * 
 * Replaces inline script duplication across modal templates
 */

/**
 * Close modal by ID
 * @param {string} modalId - The modal element ID
 */
function closeModalById(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
    }
}

/**
 * Open modal by ID  
 * @param {string} modalId - The modal element ID
 */
function openModalById(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
    }
}

/**
 * Toggle modal by ID
 * @param {string} modalId - The modal element ID
 */
function toggleModalById(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.toggle('hidden');
    }
}

// Global modal event handlers
document.addEventListener('DOMContentLoaded', function() {
    // Close modal on backdrop click (for modals with backdrop_click_close=true)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-backdrop') && e.target.dataset.closable !== 'false') {
            const modal = e.target.closest('.modal-overlay');
            if (modal) {
                modal.classList.add('hidden');
            }
        }
    });
    
    // Close modal on X button click
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-close-button') || e.target.closest('.modal-close-button')) {
            const modal = e.target.closest('.modal-overlay');
            if (modal) {
                modal.classList.add('hidden');
            }
        }
    });
    
    // Global escape key handling for all modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Find the currently visible modal
            const visibleModal = document.querySelector('.modal-overlay:not(.hidden)');
            if (visibleModal) {
                visibleModal.classList.add('hidden');
            }
        }
    });
});