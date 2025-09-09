/**
 * Modal JavaScript Mixins - DRY patterns for Alpine.js modals
 * 
 * Provides reusable functionality for modals to eliminate code duplication
 * while maintaining flexibility for entity-specific customizations.
 */

/**
 * Base modal mixin - common state and behavior for all modals
 * @param {Object} options - Configuration options
 * @returns {Object} Alpine.js data object with base modal functionality
 */
function createModalMixin(options = {}) {
    return {
        show: false,
        loading: false,
        saving: false,
        
        // Generic event handlers
        openModal() {
            this.show = true;
            if (this.onModalOpen) this.onModalOpen();
        },
        
        closeModal() {
            this.show = false;
            if (this.onModalClose) this.onModalClose();
        },
        
        // Loading states
        setLoading(state) {
            this.loading = state;
        },
        
        setSaving(state) {
            this.saving = state;
        },
        
        // Error handling
        handleError(error) {
            console.error('Modal error:', error);
            if (this.onError) {
                this.onError(error);
            } else {
                alert('An error occurred. Please try again.');
            }
        },
        
        // Generic API call wrapper
        async apiCall(url, options = {}) {
            try {
                const response = await fetch(url, {
                    headers: { 'Content-Type': 'application/json' },
                    ...options
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                this.handleError(error);
                throw error;
            }
        },
        
        // Merge with custom options
        ...options
    };
}

/**
 * CRUD mixin for entity creation and editing modals
 * @param {string} entityType - Type of entity (task, contact, etc.)
 * @param {Object} defaultEntity - Default entity structure
 * @param {Object} options - Additional options
 * @returns {Object} CRUD functionality mixin
 */
function createCRUDMixin(entityType, defaultEntity = {}, options = {}) {
    const entityKey = entityType.toLowerCase();
    const apiEndpoint = `/api/${entityKey}s`;
    
    return createModalMixin({
        // Entity data
        [entityKey]: { ...defaultEntity },
        [`${entityKey}Id`]: null,
        
        // CRUD Operations
        async loadEntity(id) {
            if (!id) return;
            
            this.setLoading(true);
            this[`${entityKey}Id`] = id;
            
            try {
                const data = await this.apiCall(`${apiEndpoint}/${id}`);
                this[entityKey] = data;
                
                // Load notes if present
                if (data.notes) {
                    this.notes = data.notes;
                }
                
                if (this.onEntityLoaded) {
                    this.onEntityLoaded(data);
                }
            } catch (error) {
                // Error already handled by apiCall
            } finally {
                this.setLoading(false);
            }
        },
        
        async saveEntity() {
            if (!this.validateEntity()) return;
            
            this.setSaving(true);
            
            try {
                const isUpdate = !!this[`${entityKey}Id`];
                const url = isUpdate ? `${apiEndpoint}/${this[`${entityKey}Id`]}` : apiEndpoint;
                const method = isUpdate ? 'PUT' : 'POST';
                
                const response = await this.apiCall(url, {
                    method,
                    body: JSON.stringify(this[entityKey])
                });
                
                if (this.onEntitySaved) {
                    this.onEntitySaved(response, isUpdate);
                } else {
                    // Default behavior - close modal and reload
                    this.closeModal();
                    window.location.reload();
                }
            } catch (error) {
                // Error already handled by apiCall
            } finally {
                this.setSaving(false);
            }
        },
        
        resetForm() {
            this[entityKey] = { ...defaultEntity };
            this[`${entityKey}Id`] = null;
            
            if (this.onFormReset) {
                this.onFormReset();
            }
        },
        
        // Validation - override in specific modals
        validateEntity() {
            if (this.customValidation) {
                return this.customValidation();
            }
            
            // Basic validation - entity should have some required field
            const requiredFields = this.getRequiredFields ? this.getRequiredFields() : [];
            for (const field of requiredFields) {
                if (!this[entityKey][field] || !this[entityKey][field].toString().trim()) {
                    this.handleError(`${field} is required`);
                    return false;
                }
            }
            
            return true;
        },
        
        // Event handlers for modals to override
        onEntityLoaded: null,
        onEntitySaved: null,
        onFormReset: null,
        customValidation: null,
        getRequiredFields: null,
        
        ...options
    });
}

/**
 * Notes mixin for modals that support notes
 * @param {string} entityType - Type of entity that has notes
 * @param {Object} options - Additional options
 * @returns {Object} Notes functionality mixin
 */
function createNotesMixin(entityType, options = {}) {
    return {
        notes: [],
        newNote: '',
        
        async addNote() {
            if (!this.newNote.trim() || !this[`${entityType}Id`]) return;
            
            try {
                const response = await this.apiCall(`/api/${entityType}s/${this[`${entityType}Id`]}/notes`, {
                    method: 'POST',
                    body: JSON.stringify({ content: this.newNote })
                });
                
                this.notes.push(response);
                this.newNote = '';
                
                if (this.onNoteAdded) {
                    this.onNoteAdded(response);
                }
            } catch (error) {
                // Error already handled by apiCall
            }
        },
        
        async deleteNote(noteId) {
            if (!confirm('Delete this note?')) return;
            
            try {
                await this.apiCall(`/api/notes/${noteId}`, {
                    method: 'DELETE'
                });
                
                this.notes = this.notes.filter(note => note.id !== noteId);
                
                if (this.onNoteDeleted) {
                    this.onNoteDeleted(noteId);
                }
            } catch (error) {
                // Error already handled by apiCall
            }
        },
        
        // Event handlers
        onNoteAdded: null,
        onNoteDeleted: null,
        
        ...options
    };
}

/**
 * Form validation utilities
 */
const FormValidation = {
    // Common validation rules
    rules: {
        required: (value) => value && value.toString().trim() !== '',
        email: (value) => !value || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        url: (value) => !value || /^https?:\/\/.+/.test(value),
        date: (value) => !value || !isNaN(Date.parse(value))
    },
    
    // Validate a field against rules
    validateField(value, rules = []) {
        for (const rule of rules) {
            if (typeof rule === 'string' && this.rules[rule]) {
                if (!this.rules[rule](value)) {
                    return { valid: false, message: `Invalid ${rule}` };
                }
            } else if (typeof rule === 'function') {
                const result = rule(value);
                if (!result) {
                    return { valid: false, message: 'Validation failed' };
                }
            }
        }
        return { valid: true };
    },
    
    // Validate entire object
    validateObject(obj, schema) {
        const errors = {};
        
        for (const [field, rules] of Object.entries(schema)) {
            const validation = this.validateField(obj[field], rules);
            if (!validation.valid) {
                errors[field] = validation.message;
            }
        }
        
        return {
            valid: Object.keys(errors).length === 0,
            errors
        };
    }
};

// Global availability
window.createModalMixin = createModalMixin;
window.createCRUDMixin = createCRUDMixin;
window.createNotesMixin = createNotesMixin;
window.FormValidation = FormValidation;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Modal mixins initialized');
});