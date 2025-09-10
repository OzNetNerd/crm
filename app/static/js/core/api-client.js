/**
 * Centralized API Client - DRY patterns for fetch operations
 * 
 * Provides standardized API communication with consistent error handling,
 * loading states, and response processing.
 */

class CRMApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Generic fetch wrapper with error handling and loading states
     * @param {string} url - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Response data or error
     */
    async request(url, options = {}) {
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(`${this.baseUrl}${url}`, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    /**
     * GET request
     * @param {string} url - API endpoint
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    async get(url, options = {}) {
        return this.request(url, { method: 'GET', ...options });
    }

    /**
     * POST request
     * @param {string} url - API endpoint
     * @param {Object} data - Request body data
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    async post(url, data = null, options = {}) {
        return this.request(url, {
            method: 'POST',
            body: data ? JSON.stringify(data) : null,
            ...options
        });
    }

    /**
     * PUT request
     * @param {string} url - API endpoint
     * @param {Object} data - Request body data
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    async put(url, data = null, options = {}) {
        return this.request(url, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : null,
            ...options
        });
    }

    /**
     * DELETE request
     * @param {string} url - API endpoint
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    async delete(url, options = {}) {
        return this.request(url, { method: 'DELETE', ...options });
    }

    // Entity-specific methods

    /**
     * Get entities with optional filtering and pagination
     * @param {string} entityType - Type of entity (tasks, contacts, etc.)
     * @param {Object} params - Query parameters
     * @returns {Promise<Array>} List of entities
     */
    async getEntities(entityType, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = `/${entityType}${queryString ? `?${queryString}` : ''}`;
        return this.get(url);
    }

    /**
     * Get single entity by ID
     * @param {string} entityType - Type of entity
     * @param {number} id - Entity ID
     * @returns {Promise<Object>} Entity data
     */
    async getEntity(entityType, id) {
        return this.get(`/${entityType}/${id}`);
    }

    /**
     * Create new entity
     * @param {string} entityType - Type of entity
     * @param {Object} data - Entity data
     * @returns {Promise<Object>} Created entity
     */
    async createEntity(entityType, data) {
        return this.post(`/${entityType}`, data);
    }

    /**
     * Update existing entity
     * @param {string} entityType - Type of entity
     * @param {number} id - Entity ID
     * @param {Object} data - Updated entity data
     * @returns {Promise<Object>} Updated entity
     */
    async updateEntity(entityType, id, data) {
        return this.put(`/${entityType}/${id}`, data);
    }

    /**
     * Delete entity
     * @param {string} entityType - Type of entity
     * @param {number} id - Entity ID
     * @returns {Promise<boolean>} Success status
     */
    async deleteEntity(entityType, id) {
        await this.delete(`/${entityType}/${id}`);
        return true;
    }

    // Task-specific methods

    /**
     * Complete a task
     * @param {number} taskId - Task ID
     * @returns {Promise<Object>} Updated task
     */
    async completeTask(taskId) {
        return this.put(`/tasks/${taskId}/complete`);
    }

    /**
     * Reschedule a task
     * @param {number} taskId - Task ID
     * @param {number} daysAdjustment - Days to adjust (positive or negative)
     * @returns {Promise<Object>} Updated task
     */
    async rescheduleTask(taskId, daysAdjustment) {
        return this.put(`/tasks/${taskId}/reschedule`, { days_adjustment: daysAdjustment });
    }

    /**
     * Get task notes
     * @param {number} taskId - Task ID
     * @returns {Promise<Array>} List of notes
     */
    async getTaskNotes(taskId) {
        return this.get(`/tasks/${taskId}/notes`);
    }

    /**
     * Add note to task
     * @param {number} taskId - Task ID
     * @param {string} content - Note content
     * @param {boolean} isInternal - Whether note is internal
     * @returns {Promise<Object>} Created note
     */
    async addTaskNote(taskId, content, isInternal = true) {
        return this.post(`/tasks/${taskId}/notes`, {
            content,
            is_internal: isInternal
        });
    }

    // Note-specific methods

    /**
     * Update a note
     * @param {number} noteId - Note ID
     * @param {string} content - Updated content
     * @returns {Promise<Object>} Updated note
     */
    async updateNote(noteId, content) {
        return this.put(`/notes/${noteId}`, { content });
    }

    /**
     * Delete a note
     * @param {number} noteId - Note ID
     * @returns {Promise<boolean>} Success status
     */
    async deleteNote(noteId) {
        await this.delete(`/notes/${noteId}`);
        return true;
    }

    // Generic entity notes (for future extensibility)

    /**
     * Get notes for any entity type
     * @param {string} entityType - Type of entity
     * @param {number} entityId - Entity ID
     * @returns {Promise<Array>} List of notes
     */
    async getEntityNotes(entityType, entityId) {
        return this.get(`/${entityType}/${entityId}/notes`);
    }

    /**
     * Add note to any entity type
     * @param {string} entityType - Type of entity
     * @param {number} entityId - Entity ID
     * @param {string} content - Note content
     * @param {boolean} isInternal - Whether note is internal
     * @returns {Promise<Object>} Created note
     */
    async addEntityNote(entityType, entityId, content, isInternal = true) {
        return this.post(`/${entityType}/${entityId}/notes`, {
            content,
            is_internal: isInternal
        });
    }
}

/**
 * API Helper functions for common UI patterns
 */
const ApiHelpers = {
    /**
     * Handle API operation with loading state and error handling
     * @param {Function} apiOperation - API operation to execute
     * @param {Object} loadingState - Alpine.js reactive object with loading property
     * @param {Function} onSuccess - Success callback
     * @param {Function} onError - Error callback
     */
    async withLoadingState(apiOperation, loadingState = null, onSuccess = null, onError = null) {
        try {
            if (loadingState) loadingState.loading = true;
            
            const result = await apiOperation();
            
            if (onSuccess) {
                onSuccess(result);
            }
            
            return result;
        } catch (error) {
            console.error('API operation failed:', error);
            
            if (onError) {
                onError(error);
            } else {
                alert('Operation failed. Please try again.');
            }
            
            throw error;
        } finally {
            if (loadingState) loadingState.loading = false;
        }
    },

    /**
     * Confirm and delete entity with proper feedback
     * @param {string} entityType - Type of entity
     * @param {number} entityId - Entity ID
     * @param {string} entityName - Entity name for confirmation
     * @param {Function} onSuccess - Success callback
     * @returns {Promise<boolean>} Success status
     */
    async confirmAndDelete(entityType, entityId, entityName = '', onSuccess = null) {
        const message = entityName 
            ? `Are you sure you want to delete "${entityName}"?`
            : `Are you sure you want to delete this ${entityType}?`;
            
        if (!confirm(message)) {
            return false;
        }

        try {
            await api.deleteEntity(entityType, entityId);
            
            // Dispatch global event
            window.dispatchEvent(new CustomEvent('entity-deleted', {
                detail: { entityType, entityId, entityName }
            }));
            
            if (onSuccess) {
                onSuccess();
            }
            
            return true;
        } catch (error) {
            console.error(`Failed to delete ${entityType}:`, error);
            alert(`Failed to delete ${entityType}. Please try again.`);
            return false;
        }
    },

    /**
     * Bulk delete entities with progress feedback
     * @param {string} entityType - Type of entity
     * @param {Array} entityIds - Array of entity IDs
     * @param {Function} onProgress - Progress callback (current, total)
     * @param {Function} onComplete - Completion callback
     * @returns {Promise<Object>} Results summary
     */
    async bulkDelete(entityType, entityIds, onProgress = null, onComplete = null) {
        if (!confirm(`Are you sure you want to delete ${entityIds.length} ${entityType}s?`)) {
            return { cancelled: true };
        }

        const results = { succeeded: [], failed: [] };
        
        for (let i = 0; i < entityIds.length; i++) {
            const entityId = entityIds[i];
            
            try {
                await api.deleteEntity(entityType, entityId);
                results.succeeded.push(entityId);
            } catch (error) {
                console.error(`Failed to delete ${entityType} ${entityId}:`, error);
                results.failed.push({ entityId, error });
            }
            
            if (onProgress) {
                onProgress(i + 1, entityIds.length);
            }
        }

        // Dispatch global event for successful deletions
        if (results.succeeded.length > 0) {
            window.dispatchEvent(new CustomEvent('entities-bulk-deleted', {
                detail: { entityType, entityIds: results.succeeded }
            }));
        }

        if (onComplete) {
            onComplete(results);
        }

        return results;
    }
};

// Create global API instance
const api = new CRMApiClient();

// Make available globally
window.api = api;
window.ApiHelpers = ApiHelpers;
window.CRMApiClient = CRMApiClient;