/**
 * Modal Handlers for Alpine.js
 * Provides modal functionality for HTMX-based forms
 */

// Alpine.js modal component
function modal(config = {}) {
    return {
        id: config.id || 'modal',
        title: config.title || '',
        type: config.type || 'info',
        autoShow: config.autoShow !== false,
        open: false,

        init() {
            // Auto-show modal on initialization if configured
            if (this.autoShow) {
                this.$nextTick(() => {
                    this.show();
                });
            }
        },

        show() {
            this.open = true;
            document.body.style.overflow = 'hidden';
        },

        hide() {
            this.open = false;
            document.body.style.overflow = '';

            // If it's a success modal, reload the page content
            if (this.id === 'success-modal') {
                if (typeof htmx !== 'undefined') {
                    // Trigger HTMX reload of content
                    const contentEl = document.querySelector('[hx-trigger="load"]');
                    if (contentEl) {
                        htmx.trigger(contentEl, 'load');
                    }
                }
            }
        },

        handleEscape(event) {
            if (event.key === 'Escape' && this.open) {
                this.hide();
            }
        },

        handleOutsideClick(event) {
            if (event.target === event.currentTarget && this.open) {
                this.hide();
            }
        }
    };
}

// Register as Alpine.js magic helper
if (typeof Alpine !== 'undefined') {
    document.addEventListener('alpine:init', () => {
        Alpine.data('modal', modal);
    });
}

// Also make it available globally
window.modal = modal;