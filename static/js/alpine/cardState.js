/**
 * Card State Management - Alpine.js Component
 * 
 * Centralized state management for expandable cards.
 * Separates concerns: UI state in JS, template rendering in Jinja2.
 * 
 * @param {Object} config - Card configuration
 * @param {string} config.cardType - Entity type ('task', 'opportunity', 'stakeholder', etc.)
 * @param {Object} config.entity - Entity data object
 * @param {number} config.entityId - Entity ID
 * @param {boolean} config.expansionEnabled - Enable expansion functionality
 * @param {boolean} config.notesEnabled - Enable notes/comments
 * @param {string} config.groupKey - Group identifier for bulk expand/collapse
 */
window.cardState = (config) => {
    const { cardType, entity, entityId, expansionEnabled = true, notesEnabled = false, groupKey = '' } = config;
    
    return {
        // Entity data (read-only)
        entity: entity || {},
        
        // Core UI state
        expanded: false,
        isEditing: false,
        showSaveButtons: false,
        
        // Notes state
        newComment: '',
        editingCommentId: null,
        editingCommentText: '',
        notes: [],
        notesLoaded: false,
        saving: false,
        
        // Task-specific state (only for task entities)
        ...(cardType === 'task' && {
            pendingDays: 0,
            originalDueDate: entity?.due_date || '',
            
            getNewDueDate() {
                if (!this.originalDueDate || this.pendingDays === 0) return this.originalDueDate;
                const date = new Date(this.originalDueDate);
                date.setDate(date.getDate() + this.pendingDays);
                return date.toLocaleDateString('en-GB');
            },
            
            adjustDays(days) {
                this.pendingDays += days;
                this.isEditing = true;
                this.showSaveButtons = true;
            },
            
            cancelChanges() {
                this.pendingDays = 0;
                this.isEditing = false;
                this.showSaveButtons = false;
            }
        }),
        
        // Expansion methods
        toggle() {
            if (!expansionEnabled) return;
            this.expanded = !this.expanded;
            if (this.expanded && notesEnabled) {
                this.loadNotes();
            }
        },
        
        expandAll(group) {
            if (!expansionEnabled || !groupKey || group !== groupKey) return;
            if (!this.expanded) {
                this.expanded = true;
                if (notesEnabled) this.loadNotes();
            }
        },
        
        collapseAll(group) {
            if (!expansionEnabled || !groupKey || group !== groupKey) return;
            if (this.expanded) {
                this.expanded = false;
            }
        },
        
        // Notes API methods
        async loadNotes() {
            if (!notesEnabled || this.notesLoaded) return;
            
            try {
                const response = await fetch(`/api/${cardType}s/${entityId}/notes`);
                if (response.ok) {
                    this.notes = await response.json();
                    this.notesLoaded = true;
                } else {
                    console.error(`Failed to load notes for ${cardType} ${entityId}`);
                }
            } catch (error) {
                console.error('Error loading notes:', error);
            }
        },
        
        startEditComment(commentId, currentText) {
            if (!notesEnabled) return;
            this.editingCommentId = commentId;
            this.editingCommentText = currentText;
        },
        
        cancelEditComment() {
            if (!notesEnabled) return;
            this.editingCommentId = null;
            this.editingCommentText = '';
        },
        
        async saveEditComment() {
            if (!notesEnabled || !this.editingCommentText.trim()) return;
            
            this.saving = true;
            try {
                const response = await fetch(`/api/notes/${this.editingCommentId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: this.editingCommentText
                    })
                });
                
                if (response.ok) {
                    const noteIndex = this.notes.findIndex(note => note.id === this.editingCommentId);
                    if (noteIndex !== -1) {
                        this.notes[noteIndex].content = this.editingCommentText;
                    }
                    this.editingCommentId = null;
                    this.editingCommentText = '';
                } else {
                    throw new Error('Failed to update comment');
                }
            } catch (error) {
                console.error('Error updating comment:', error);
                alert('Failed to update comment');
            } finally {
                this.saving = false;
            }
        },
        
        async deleteComment(commentId) {
            if (!notesEnabled || !confirm('Are you sure you want to delete this comment?')) return;
            
            try {
                const response = await fetch(`/api/notes/${commentId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    this.notes = this.notes.filter(note => note.id !== commentId);
                } else {
                    throw new Error('Failed to delete comment');
                }
            } catch (error) {
                console.error('Error deleting comment:', error);
                alert('Failed to delete comment');
            }
        },
        
        async submitComment() {
            if (!notesEnabled || !this.newComment.trim()) return;
            
            this.saving = true;
            try {
                const response = await fetch(`/api/${cardType}s/${entityId}/notes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: this.newComment,
                        is_internal: true
                    })
                });
                
                if (response.ok) {
                    const newNote = await response.json();
                    if (!this.notes) this.notes = [];
                    this.notes.unshift(newNote);
                    this.newComment = '';
                } else {
                    throw new Error('Failed to add comment');
                }
            } catch (error) {
                console.error('Error adding comment:', error);
                alert('Failed to add comment');
            } finally {
                this.saving = false;
            }
        },
        
        // Event handlers for external events
        init() {
            // Listen for global expand/collapse events
            if (groupKey && expansionEnabled) {
                this.$watch('$store.expandedGroups.' + groupKey, (value) => {
                    if (value !== undefined) {
                        if (value && !this.expanded) {
                            this.expanded = true;
                            if (notesEnabled) this.loadNotes();
                        } else if (!value && this.expanded) {
                            this.expanded = false;
                        }
                    }
                });
            }
            
            // Listen for task reschedule events
            if (cardType === 'task') {
                this.$watch('$store.taskRescheduled', (value) => {
                    if (value && this.isEditing) {
                        this.cancelChanges();
                    }
                });
            }
        }
    };
};