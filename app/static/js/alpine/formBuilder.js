/**
 * Alpine.js Dynamic Form Builder
 *
 * Replaces modal_configs.py server-side form generation with client-side Alpine.js
 * Provides dynamic form rendering, validation, and submission.
 */
window.formBuilder = (config) => {
    const { modelName, entityId = null, formType = 'create' } = config;

    return {
        // Form state
        formData: {},
        errors: {},
        loading: false,
        saving: false,

        // Form configuration (loaded dynamically)
        formConfig: null,
        fields: [],

        // Modal state
        isOpen: false,
        title: '',

        async init() {
            if (this.isOpen) {
                await this.loadFormConfig();
            }
        },

        async openModal(type = 'create', id = null) {
            this.formType = type;
            this.entityId = id;
            this.isOpen = true;
            await this.loadFormConfig();
        },

        closeModal() {
            this.isOpen = false;
            this.resetForm();
        },

        async loadFormConfig() {
            this.loading = true;
            try {
                const endpoint = `/api/forms/${this.modelName}/config?type=${this.formType}`;
                const response = await fetch(endpoint);

                if (!response.ok) {
                    throw new Error(`Failed to load form config: ${response.statusText}`);
                }

                this.formConfig = await response.json();
                this.setupForm();

                // Load existing data for edit forms
                if (this.formType === 'edit' && this.entityId) {
                    await this.loadEntityData();
                }

            } catch (error) {
                console.error('Error loading form config:', error);
                this.errors.general = 'Failed to load form configuration';
            } finally {
                this.loading = false;
            }
        },

        setupForm() {
            const config = this.formConfig;
            this.title = config.title;
            this.fields = config.fields || [];

            // Initialize form data with default values
            this.formData = {};
            this.fields.forEach(field => {
                if (field.type === 'grid') {
                    field.fields.forEach(subField => {
                        this.formData[subField.name] = subField.default || '';
                    });
                } else {
                    this.formData[field.name] = field.default || '';
                }
            });
        },

        async loadEntityData() {
            try {
                const response = await fetch(`/api/${this.modelName}/${this.entityId}`);
                if (response.ok) {
                    const entityData = await response.json();
                    Object.assign(this.formData, entityData);
                }
            } catch (error) {
                console.error('Error loading entity data:', error);
            }
        },

        validateField(fieldName) {
            const field = this.findField(fieldName);
            if (!field) return true;

            const value = this.formData[fieldName];

            // Clear previous error
            delete this.errors[fieldName];

            // Required validation
            if (field.required && (!value || value.toString().trim() === '')) {
                this.errors[fieldName] = `${field.label} is required`;
                return false;
            }

            // Email validation
            if (field.type === 'email' && value && !this.isValidEmail(value)) {
                this.errors[fieldName] = 'Please enter a valid email address';
                return false;
            }

            // URL validation
            if (field.type === 'url' && value && !this.isValidUrl(value)) {
                this.errors[fieldName] = 'Please enter a valid URL';
                return false;
            }

            return true;
        },

        validateForm() {
            this.errors = {};
            let isValid = true;

            this.fields.forEach(field => {
                if (field.type === 'grid') {
                    field.fields.forEach(subField => {
                        if (!this.validateField(subField.name)) {
                            isValid = false;
                        }
                    });
                } else if (!this.validateField(field.name)) {
                    isValid = false;
                }
            });

            return isValid;
        },

        async submitForm() {
            if (!this.validateForm()) {
                return;
            }

            this.saving = true;
            try {
                const endpoint = this.formType === 'edit'
                    ? `/api/${this.modelName}/${this.entityId}`
                    : `/api/${this.modelName}`;

                const method = this.formType === 'edit' ? 'PUT' : 'POST';

                const response = await fetch(endpoint, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify(this.formData)
                });

                if (response.ok) {
                    const result = await response.json();
                    this.handleSuccess(result);
                } else {
                    const errorData = await response.json();
                    this.handleErrors(errorData);
                }

            } catch (error) {
                console.error('Form submission error:', error);
                this.errors.general = 'Failed to save. Please try again.';
            } finally {
                this.saving = false;
            }
        },

        handleSuccess(result) {
            // Close modal
            this.closeModal();

            // Refresh page or trigger HTMX update
            if (window.htmx) {
                // Trigger HTMX refresh of relevant sections
                htmx.trigger(document.body, 'entity-updated', {
                    modelName: this.modelName,
                    entityId: result.id,
                    formType: this.formType
                });
            } else {
                // Fallback: reload page
                window.location.reload();
            }

            // Show success message
            this.showNotification(`${this.modelName} ${this.formType === 'edit' ? 'updated' : 'created'} successfully!`, 'success');
        },

        handleErrors(errorData) {
            if (errorData.field_errors) {
                Object.assign(this.errors, errorData.field_errors);
            }
            if (errorData.message) {
                this.errors.general = errorData.message;
            }
        },

        resetForm() {
            this.formData = {};
            this.errors = {};
            this.loading = false;
            this.saving = false;
            this.formConfig = null;
            this.fields = [];
        },

        // Utility methods
        findField(fieldName) {
            for (const field of this.fields) {
                if (field.type === 'grid') {
                    const subField = field.fields.find(f => f.name === fieldName);
                    if (subField) return subField;
                } else if (field.name === fieldName) {
                    return field;
                }
            }
            return null;
        },

        isValidEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },

        isValidUrl(url) {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        },

        getCsrfToken() {
            const tokenMeta = document.querySelector('meta[name="csrf-token"]');
            return tokenMeta ? tokenMeta.getAttribute('content') : '';
        },

        showNotification(message, type = 'info') {
            // Simple notification - could be enhanced with a proper notification system
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 p-4 rounded-md z-50 ${
                type === 'success' ? 'bg-green-500 text-white' :
                type === 'error' ? 'bg-red-500 text-white' :
                'bg-blue-500 text-white'
            }`;
            notification.textContent = message;

            document.body.appendChild(notification);

            setTimeout(() => {
                notification.remove();
            }, 5000);
        },

        // Field type helpers for templates
        isTextField(field) {
            return ['text', 'email', 'url', 'tel'].includes(field.type);
        },

        isSelectField(field) {
            return field.type === 'select';
        },

        isTextareaField(field) {
            return field.type === 'textarea';
        },

        isCheckboxField(field) {
            return field.type === 'checkbox';
        },

        isGridField(field) {
            return field.type === 'grid';
        }
    };
};