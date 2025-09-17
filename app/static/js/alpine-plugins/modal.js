/**
 * Alpine.js Modal Plugin
 * Minimal modal component for x-data="modal()"
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('modal', (config = {}) => ({
        id: config.id || 'modal',
        title: config.title || '',
        closable: config.closable !== false,

        handleBackdropClick(event) {
            if (this.closable && event.target.classList.contains('modal-backdrop')) {
                this.$el.style.display = 'none';
            }
        }
    }));
});