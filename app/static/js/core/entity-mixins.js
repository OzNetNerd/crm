/**
 * Alpine.js Entity Card Mixins - DRY patterns for entity cards
 * 
 * Provides reusable functionality for entity cards to eliminate code duplication
 * while maintaining flexibility for entity-specific customizations.
 */

/**
 * Base entity card mixin - common state and behavior for all entity cards
 * @param {string} entityType - Type of entity ('task', 'opportunity', 'contact', 'company')
 * @param {Object} entity - Entity data object
 * @param {Object} options - Configuration options
 * @returns {Object} Alpine.js data object with base entity card functionality
 */
function createEntityCardMixin(entityType, entity, options = {}) {
    return {
        // Core expansion state
        expanded: false,
        
        // Generic editing state
        isEditing: false,
        showSaveButtons: false,
        
        // Notes functionality (for tasks and extensible to other entities)
        notes: options.enableNotes ? [] : undefined,
        newNote: '',
        showNotesInput: false,
        notesLoaded: false,
        editingNoteId: null,
        editingNoteText: '',
        
        // Entity data
        entityType: entityType,
        entity: entity,
        
        // Toggle expansion
        toggleExpansion() {
            this.expanded = !this.expanded;
            if (this.expanded && this.notes !== undefined && !this.notesLoaded) {
                this.loadNotes();
            }
        },
        
        // Generic editing controls
        startEditing() {
            this.isEditing = true;
            this.showSaveButtons = true;
        },
        
        cancelEditing() {
            this.isEditing = false;
            this.showSaveButtons = false;
            // Reset any pending changes
            if (this.resetPendingChanges) {
                this.resetPendingChanges();
            }
        },
        
        // Notes functionality
        async loadNotes() {
            if (!this.notes || this.notesLoaded) return;
            
            try {
                const response = await fetch(`/api/${this.entityType}s/${this.entity.id}/notes`);
                if (response.ok) {
                    this.notes = await response.json();
                    this.notesLoaded = true;
                } else {
                    console.error('Failed to load notes');
                }
            } catch (error) {
                console.error('Error loading notes:', error);
            }
        },
        
        async submitNote() {
            if (!this.newNote.trim()) return;
            
            try {
                const response = await fetch(`/api/${this.entityType}s/${this.entity.id}/notes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: this.newNote,
                        is_internal: true
                    })
                });
                
                if (response.ok) {
                    const newNote = await response.json();
                    if (!this.notes) this.notes = [];
                    this.notes.unshift(newNote);
                    this.newNote = '';
                } else {
                    alert('Failed to add note');
                }
            } catch (error) {
                console.error('Error adding note:', error);
                alert('Failed to add note');
            }
        },
        
        startEditNote(noteId, currentText) {
            this.editingNoteId = noteId;
            this.editingNoteText = currentText;
        },
        
        cancelEditNote() {
            this.editingNoteId = null;
            this.editingNoteText = '';
        },
        
        async saveEditNote() {
            if (!this.editingNoteText.trim()) return;
            
            try {
                const response = await fetch(`/api/notes/${this.editingNoteId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: this.editingNoteText
                    })
                });
                
                if (response.ok) {
                    const noteIndex = this.notes.findIndex(note => note.id === this.editingNoteId);
                    if (noteIndex !== -1) {
                        this.notes[noteIndex].content = this.editingNoteText;
                    }
                    this.editingNoteId = null;
                    this.editingNoteText = '';
                } else {
                    alert('Failed to update note');
                }
            } catch (error) {
                console.error('Error updating note:', error);
                alert('Failed to update note');
            }
        },
        
        async deleteNote(noteId) {
            if (!confirm('Are you sure you want to delete this note?')) return;
            
            try {
                const response = await fetch(`/api/notes/${noteId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    this.notes = this.notes.filter(note => note.id !== noteId);
                } else {
                    alert('Failed to delete note');
                }
            } catch (error) {
                console.error('Error deleting note:', error);
                alert('Failed to delete note');
            }
        }
    };
}

/**
 * Task card specific mixin - extends base entity card with task-specific functionality
 * @param {Object} task - Task data object
 * @param {Object} options - Configuration options
 * @returns {Object} Alpine.js data object with task-specific functionality
 */
function createTaskCardMixin(task, options = {}) {
    const baseMixin = createEntityCardMixin('task', task, { enableNotes: true, ...options });
    
    return {
        ...baseMixin,
        
        // Task-specific reschedule state
        pendingDays: 0,
        originalDueDate: task.due_date ? task.due_date.toLocaleDateString('en-GB') : '',
        
        // Task-specific methods
        getNewDueDate() {
            if (!this.originalDueDate || this.pendingDays === 0) return this.originalDueDate;
            const date = new Date(task.due_date);
            date.setDate(date.getDate() + this.pendingDays);
            return date.toLocaleDateString('en-GB');
        },
        
        adjustDays(days) {
            this.pendingDays += days;
            this.startEditing();
        },
        
        resetPendingChanges() {
            this.pendingDays = 0;
        },
        
        async saveReschedule() {
            if (this.pendingDays === 0) return;
            
            try {
                const response = await fetch(`/api/tasks/${this.entity.id}/reschedule`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        days_adjustment: this.pendingDays
                    })
                });
                
                if (response.ok) {
                    // Update the entity's due date
                    const newDate = new Date(this.entity.due_date);
                    newDate.setDate(newDate.getDate() + this.pendingDays);
                    this.entity.due_date = newDate;
                    this.originalDueDate = newDate.toLocaleDateString('en-GB');
                    
                    // Reset state
                    this.cancelEditing();
                    
                    // Dispatch event for external listeners
                    window.dispatchEvent(new CustomEvent('reschedule-saved', {
                        detail: { taskId: this.entity.id, newDate: newDate }
                    }));
                } else {
                    alert('Failed to reschedule task');
                }
            } catch (error) {
                console.error('Error rescheduling task:', error);
                alert('Failed to reschedule task');
            }
        }
    };
}

/**
 * Multiselect dropdown mixin - common functionality for dropdowns
 * @param {Array} options - Available options
 * @param {Object} config - Configuration options
 * @returns {Object} Alpine.js data object with multiselect functionality
 */
function createMultiselectMixin(options, config = {}) {
    return {
        open: false,
        searchTerm: config.enableSearch ? '' : undefined,
        selectedValues: config.multiple ? [] : null,
        
        toggleDropdown() {
            this.open = !this.open;
        },
        
        closeDropdown() {
            this.open = false;
        },
        
        selectOption(value) {
            if (config.multiple) {
                const index = this.selectedValues.indexOf(value);
                if (index === -1) {
                    this.selectedValues.push(value);
                } else {
                    this.selectedValues.splice(index, 1);
                }
            } else {
                this.selectedValues = value;
                this.closeDropdown();
            }
            
            if (config.onChange) {
                config.onChange(this.selectedValues);
            }
        },
        
        selectAll() {
            if (config.multiple) {
                this.selectedValues = options.map(opt => opt.value || opt);
                if (config.onChange) {
                    config.onChange(this.selectedValues);
                }
            }
        },
        
        deselectAll() {
            if (config.multiple) {
                this.selectedValues = [];
            } else {
                this.selectedValues = null;
            }
            if (config.onChange) {
                config.onChange(this.selectedValues);
            }
        },
        
        isSelected(value) {
            if (config.multiple) {
                return this.selectedValues.includes(value);
            }
            return this.selectedValues === value;
        },
        
        getDisplayText() {
            if (config.multiple) {
                if (this.selectedValues.length === 0) {
                    return config.placeholder || 'Select...';
                }
                return `${this.selectedValues.length} selected`;
            } else {
                if (!this.selectedValues) {
                    return config.placeholder || 'Select...';
                }
                const option = options.find(opt => (opt.value || opt) === this.selectedValues);
                return option ? (option.label || option) : this.selectedValues;
            }
        },
        
        filterOptions() {
            if (!config.enableSearch || !this.searchTerm) {
                return options;
            }
            return options.filter(option => {
                const label = option.label || option;
                return label.toLowerCase().includes(this.searchTerm.toLowerCase());
            });
        }
    };
}

/**
 * API helper functions for common patterns
 */
const EntityCardAPI = {
    /**
     * Generic delete function for entities
     * @param {string} entityType - Type of entity
     * @param {number} entityId - Entity ID
     * @returns {Promise<boolean>} Success status
     */
    async deleteEntity(entityType, entityId) {
        if (!confirm(`Are you sure you want to delete this ${entityType}?`)) {
            return false;
        }
        
        try {
            const response = await fetch(`/api/${entityType}s/${entityId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                // Dispatch event for UI updates
                window.dispatchEvent(new CustomEvent('entity-deleted', {
                    detail: { entityType, entityId }
                }));
                return true;
            } else {
                alert(`Failed to delete ${entityType}`);
                return false;
            }
        } catch (error) {
            console.error(`Error deleting ${entityType}:`, error);
            alert(`Failed to delete ${entityType}`);
            return false;
        }
    },
    
    /**
     * Generic complete function for tasks
     * @param {number} taskId - Task ID
     * @returns {Promise<boolean>} Success status
     */
    async completeTask(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}/complete`, {
                method: 'PUT'
            });
            
            if (response.ok) {
                // Dispatch event for UI updates
                window.dispatchEvent(new CustomEvent('task-completed', {
                    detail: { taskId }
                }));
                return true;
            } else {
                alert('Failed to complete task');
                return false;
            }
        } catch (error) {
            console.error('Error completing task:', error);
            alert('Failed to complete task');
            return false;
        }
    }
};

// Global helper functions for templates
window.createEntityCardMixin = createEntityCardMixin;
window.createTaskCardMixin = createTaskCardMixin;
window.createMultiselectMixin = createMultiselectMixin;
window.EntityCardAPI = EntityCardAPI;