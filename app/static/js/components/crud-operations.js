/**
 * CRUD Operations - Clean JavaScript implementation for entity operations
 * Replaces the crud_operations.html Jinja2 macro with proper JavaScript
 */

/**
 * Create CRUD operations for a specific entity type
 * @param {string} entityType - The entity type (e.g., 'company', 'contact')
 * @param {string} apiEndpoint - The API endpoint for this entity type
 * @returns {object} Object containing CRUD operation functions
 */
function createCRUDOperations(entityType, apiEndpoint) {
    return {
        async saveEntityDetails(entityData, entityId) {
            if (!entityData) return;
            
            try {
                const response = await fetch(`${apiEndpoint}/${entityId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(entityData)
                });
                
                if (response.ok) {
                    // Return success so calling code can handle UI updates
                    return { success: true, data: await response.json() };
                } else {
                    console.error(`Failed to save ${entityType} details`);
                    return { success: false, error: 'Save failed' };
                }
            } catch (error) {
                console.error(`Error saving ${entityType} details:`, error);
                return { success: false, error: error.message };
            }
        },

        async loadEntityDetails(id) {
            if (!id) return { success: false, error: 'No ID provided' };
            
            try {
                const [entityResponse, notesResponse] = await Promise.all([
                    fetch(`${apiEndpoint}/${id}`),
                    fetch(`/api/${entityType}s/${id}/notes`)
                ]);
                
                const result = { success: true };
                
                if (entityResponse.ok) {
                    result.entity = await entityResponse.json();
                }
                
                if (notesResponse.ok) {
                    result.notes = await notesResponse.json();
                } else {
                    result.notes = [];
                }
                
                return result;
            } catch (error) {
                console.error(`Error loading ${entityType} details:`, error);
                return { success: false, error: error.message };
            }
        }
    };
}

/**
 * Create notes operations for a specific entity type
 * @param {string} entityType - The entity type (e.g., 'company', 'contact')
 * @returns {object} Object containing notes operation functions
 */
function createNotesOperations(entityType) {
    return {
        async addNote(entityId, noteContent) {
            if (!noteContent.trim() || !entityId) {
                return { success: false, error: 'Note content and entity ID required' };
            }
            
            try {
                const response = await fetch(`/api/${entityType}s/${entityId}/notes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: noteContent })
                });
                
                if (response.ok) {
                    const note = await response.json();
                    return { success: true, note: note };
                } else {
                    return { success: false, error: 'Failed to add note' };
                }
            } catch (error) {
                console.error('Error adding note:', error);
                return { success: false, error: error.message };
            }
        },

        async deleteNote(noteId) {
            if (!noteId) {
                return { success: false, error: 'Note ID required' };
            }
            
            try {
                const response = await fetch(`/api/notes/${noteId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    return { success: true };
                } else {
                    return { success: false, error: 'Failed to delete note' };
                }
            } catch (error) {
                console.error('Error deleting note:', error);
                return { success: false, error: error.message };
            }
        }
    };
}

// Global factory functions for backward compatibility with existing Alpine.js mixins
window.createCRUDOperations = createCRUDOperations;
window.createNotesOperations = createNotesOperations;