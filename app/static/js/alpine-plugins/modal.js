/**
 * Alpine.js Modal Plugin
 * Unified modal component with consistent behavior
 * Replaces inline Alpine.js code in modal templates
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('modal', (config = {}) => ({
        // Core state
        isOpen: false,
        loading: false,
        saving: false,
        errors: {},

        // Configuration
        id: config.id || 'modal',
        title: config.title || 'Modal',
        size: config.size || 'md', // sm, md, lg, xl, full
        closable: config.closable !== false,
        closeOnBackdrop: config.closeOnBackdrop !== false,
        closeOnEscape: config.closeOnEscape !== false,

        // Callbacks
        onOpen: config.onOpen || null,
        onClose: config.onClose || null,
        onSave: config.onSave || null,

        // Methods
        init() {
            // Setup keyboard listeners
            if (this.closeOnEscape) {
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape' && this.isOpen) {
                        this.close();
                    }
                });
            }

            // Watch for open state changes
            this.$watch('isOpen', (value) => {
                if (value) {
                    this.handleOpen();
                } else {
                    this.handleClose();
                }
            });

            // Listen for custom events
            this.$el.addEventListener('modal:open', () => this.open());
            this.$el.addEventListener('modal:close', () => this.close());
            this.$el.addEventListener('modal:toggle', () => this.toggle());
        },

        open() {
            this.isOpen = true;
        },

        close() {
            if (!this.closable) return;
            this.isOpen = false;
        },

        toggle() {
            this.isOpen = !this.isOpen;
        },

        handleOpen() {
            // Lock body scroll
            document.body.classList.add('modal-open');

            // Focus management
            this.$nextTick(() => {
                const focusable = this.$el.querySelector('[autofocus]') ||
                                  this.$el.querySelector('button, input, select, textarea');
                focusable?.focus();
            });

            // Call open callback
            if (this.onOpen) {
                this.onOpen.call(this);
            }

            // Dispatch open event
            this.$dispatch('modal:opened', { id: this.id });
        },

        handleClose() {
            // Unlock body scroll
            document.body.classList.remove('modal-open');

            // Clear errors
            this.errors = {};

            // Call close callback
            if (this.onClose) {
                this.onClose.call(this);
            }

            // Dispatch close event
            this.$dispatch('modal:closed', { id: this.id });
        },

        async save() {
            if (!this.onSave) return;

            this.saving = true;
            this.errors = {};

            try {
                const result = await this.onSave.call(this);
                if (result !== false) {
                    this.close();
                }
            } catch (error) {
                console.error('Modal save error:', error);
                this.errors = error.errors || { general: 'An error occurred' };
            } finally {
                this.saving = false;
            }
        },

        handleBackdropClick(event) {
            if (this.closeOnBackdrop && event.target === event.currentTarget) {
                this.close();
            }
        },

        // Form handling
        getFormData() {
            const form = this.$el.querySelector('form');
            if (!form) return {};

            const formData = new FormData(form);
            const data = {};
            for (const [key, value] of formData) {
                data[key] = value;
            }
            return data;
        },

        setFormData(data) {
            const form = this.$el.querySelector('form');
            if (!form) return;

            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        },

        clearForm() {
            const form = this.$el.querySelector('form');
            if (form) {
                form.reset();
            }
            this.errors = {};
        },

        // Validation
        validateForm() {
            const form = this.$el.querySelector('form');
            if (!form) return true;

            // HTML5 validation
            if (!form.checkValidity()) {
                form.reportValidity();
                return false;
            }

            return true;
        },

        // Error handling
        hasError(field) {
            return !!this.errors[field];
        },

        getError(field) {
            return this.errors[field] || '';
        },

        setError(field, message) {
            this.errors[field] = message;
        },

        clearError(field) {
            delete this.errors[field];
        }
    }));

    // Global modal manager
    Alpine.store('modals', {
        active: [],

        open(id) {
            const modal = document.querySelector(`[x-data*="modal"][data-modal-id="${id}"]`);
            if (modal) {
                modal.dispatchEvent(new CustomEvent('modal:open'));
                this.active.push(id);
            }
        },

        close(id) {
            const modal = document.querySelector(`[x-data*="modal"][data-modal-id="${id}"]`);
            if (modal) {
                modal.dispatchEvent(new CustomEvent('modal:close'));
                this.active = this.active.filter(m => m !== id);
            }
        },

        closeAll() {
            this.active.forEach(id => this.close(id));
        },

        isOpen(id) {
            return this.active.includes(id);
        }
    });
});