/**
 * Centralized Modal Management System
 * 
 * This file consolidates all modal-related JavaScript functions to eliminate
 * duplicate modal functions across multiple templates.
 * 
 * Replaces 12+ individual modal functions with a centralized system.
 */

// Modal state management
window.modalManager = {
    openModals: new Set(),
    
    /**
     * Generic modal opener
     * @param {string} modalType - Type of modal to open ('task', 'contact', 'company', 'opportunity')
     * @param {string} action - Action type ('new', 'detail', 'edit')  
     * @param {number|null} entityId - ID of entity for detail/edit modals
     */
    openModal(modalType, action = 'new', entityId = null) {
        // Standardize event names: 'detail' becomes just the entity name
        const eventName = action === 'detail' || action === 'edit' 
            ? `open-${modalType}-modal` 
            : `open-${action}-${modalType}-modal`;
        const eventData = entityId ? { [`${modalType}Id`]: entityId } : {};
        
        // Track open modals
        const modalKey = `${modalType}-${action}${entityId ? `-${entityId}` : ''}`;
        this.openModals.add(modalKey);
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent(eventName, { detail: eventData }));
        
        console.log(`Opening ${modalType} ${action} modal${entityId ? ` for ID ${entityId}` : ''}`);
    },
    
    /**
     * Close modal and remove from tracking
     * @param {string} modalKey - Key identifying the modal
     */
    closeModal(modalKey) {
        this.openModals.delete(modalKey);
        console.log(`Closed modal: ${modalKey}`);
    },
    
    /**
     * Check if any modals are currently open
     * @returns {boolean}
     */
    hasOpenModals() {
        return this.openModals.size > 0;
    }
};

// Task-related modal functions
function openNewTaskModal() {
    window.modalManager.openModal('task', 'new');
}

function openTaskModal(taskId) {
    window.modalManager.openModal('task', 'detail', taskId);
}

function openTaskDetailModal(taskId) {
    window.modalManager.openModal('task', 'detail', taskId);
}

function openEditTaskModal(taskId) {
    window.modalManager.openModal('task', 'edit', taskId);
}

// Contact-related modal functions
function openNewContactModal() {
    window.modalManager.openModal('contact', 'new');
}

function openContactModal(contactId) {
    window.modalManager.openModal('contact', 'detail', contactId);
}

function openContactDetailModal(contactId) {
    window.modalManager.openModal('contact', 'detail', contactId);
}

function openEditContactModal(contactId) {
    window.modalManager.openModal('contact', 'edit', contactId);
}

// Company-related modal functions  
function openNewCompanyModal() {
    window.modalManager.openModal('company', 'new');
}

function openCompanyModal(companyId) {
    window.modalManager.openModal('company', 'detail', companyId);
}

function openCompanyDetailModal(companyId) {
    window.modalManager.openModal('company', 'detail', companyId);
}

function openEditCompanyModal(companyId) {
    window.modalManager.openModal('company', 'edit', companyId);
}

// Opportunity-related modal functions
function openNewOpportunityModal() {
    window.modalManager.openModal('opportunity', 'new');
}

function openOpportunityModal(opportunityId) {
    window.modalManager.openModal('opportunity', 'detail', opportunityId);
}

function openOpportunityDetailModal(opportunityId) {
    window.modalManager.openModal('opportunity', 'detail', opportunityId);
}

function openEditOpportunityModal(opportunityId) {
    window.modalManager.openModal('opportunity', 'edit', opportunityId);
}

// Entity action functions (create tasks/opportunities for entities)
function createTask(entityType, entityId) {
    // Pre-populate task creation with entity relationship
    const eventData = {
        entityType: entityType,
        entityId: entityId
    };
    window.dispatchEvent(new CustomEvent('open-new-task-modal', { detail: eventData }));
    console.log(`Creating task for ${entityType} ${entityId}`);
}

function createOpportunity(entityType, entityId) {
    // Pre-populate opportunity creation with entity relationship
    const eventData = {
        entityType: entityType,
        entityId: entityId
    };
    window.dispatchEvent(new CustomEvent('open-new-opportunity-modal', { detail: eventData }));
    console.log(`Creating opportunity for ${entityType} ${entityId}`);
}

// Delete confirmation functions
async function deleteEntity(entityType, entityId, confirmMessage = null) {
    const defaultMessage = `Are you sure you want to delete this ${entityType}?`;
    const message = confirmMessage || defaultMessage;
    
    if (confirm(message)) {
        try {
            const response = await fetch(`/${entityType}s/${entityId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                // Refresh page or update UI
                location.reload();
            } else {
                const error = await response.json();
                alert(`Error deleting ${entityType}: ${error.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error(`Error deleting ${entityType}:`, error);
            alert(`Error deleting ${entityType}. Please try again.`);
        }
    }
}

// Specific delete functions for backward compatibility
function deleteTask(taskId) {
    return deleteEntity('task', taskId, 'Are you sure you want to delete this task?');
}

function deleteContact(contactId) {
    return deleteEntity('contact', contactId, 'Are you sure you want to delete this contact?');
}

function deleteCompany(companyId) {
    return deleteEntity('company', companyId, 'Are you sure you want to delete this company?');
}

function deleteOpportunity(opportunityId) {
    return deleteEntity('opportunity', opportunityId, 'Are you sure you want to delete this opportunity? This action cannot be undone.');
}

// Initialize modal management system
document.addEventListener('DOMContentLoaded', function() {
    console.log('Modal management system initialized');
    
    // Add global error handling for modal operations
    window.addEventListener('error', function(event) {
        if (event.error && event.error.message.includes('modal')) {
            console.error('Modal error:', event.error);
        }
    });
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        window.modalManager.openModals.clear();
    });
});