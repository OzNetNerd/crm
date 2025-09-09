/**
 * Card State Manager - Manage expandable cards with notes
 * Extracted from template macro for clean separation
 */

/**
 * Create card state manager for entity cards
 * @param {string} cardType - Type of card (company, contact, etc.)
 * @param {number} entityId - ID of the entity
 * @param {boolean} initialExpanded - Whether card starts expanded
 */
function createCardStateManager(cardType, entityId, initialExpanded = false) {
    return {
        expanded: initialExpanded,
        notes: [],
        newComment: '',
        editingCommentId: null,
        editingCommentText: '',
        loading: false,
        cardType: cardType,
        entityId: entityId,

        async toggleExpanded() {
            this.expanded = !this.expanded;
            if (this.expanded && this.notes.length === 0) {
                await this.loadNotes();
            }
        },

        async loadNotes() {
            if (!this.entityId) return;
            
            this.loading = true;
            try {
                const response = await fetch(`/api/${this.cardType}s/${this.entityId}/notes`);
                if (response.ok) {
                    this.notes = await response.json();
                } else {
                    console.error('Failed to load notes');
                }
            } catch (error) {
                console.error('Error loading notes:', error);
            } finally {
                this.loading = false;
            }
        },

        startEditComment(comment) {
            this.editingCommentId = comment.id;
            this.editingCommentText = comment.content;
        },

        cancelEditComment() {
            this.editingCommentId = null;
            this.editingCommentText = '';
        },

        async saveEditComment() {
            if (!this.editingCommentText.trim()) return;

            try {
                const response = await fetch(`/api/notes/${this.editingCommentId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: this.editingCommentText
                    })
                });

                if (response.ok) {
                    // Update the note in our local array
                    const noteIndex = this.notes.findIndex(n => n.id === this.editingCommentId);
                    if (noteIndex !== -1) {
                        this.notes[noteIndex].content = this.editingCommentText;
                    }
                    this.editingCommentId = null;
                    this.editingCommentText = '';
                }
            } catch (error) {
                console.error('Error updating comment:', error);
            }
        },

        async deleteComment(commentId) {
            if (!confirm('Are you sure you want to delete this comment?')) return;

            try {
                const response = await fetch(`/api/notes/${commentId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.notes = this.notes.filter(note => note.id !== commentId);
                }
            } catch (error) {
                console.error('Error deleting comment:', error);
            }
        },

        async submitComment() {
            if (!this.newComment.trim()) return;

            try {
                const response = await fetch(`/api/${this.cardType}s/${this.entityId}/notes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: this.newComment
                    })
                });

                if (response.ok) {
                    const newNote = await response.json();
                    this.notes.push(newNote);
                    this.newComment = '';
                } else {
                    console.error('Failed to add comment');
                }
            } catch (error) {
                console.error('Error adding comment:', error);
            }
        },

        // Formatting helpers
        formatDate(dateString) {
            if (!dateString) return '';
            return new Date(dateString).toLocaleDateString();
        },

        formatDateTime(dateString) {
            if (!dateString) return '';
            return new Date(dateString).toLocaleString();
        }
    };
}

// Global factory function
window.createCardStateManager = createCardStateManager;