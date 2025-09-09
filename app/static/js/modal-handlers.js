// Modal-specific JavaScript handlers
// Extracted from templates to maintain clean separation

// Task modal handlers
async function toggleChildTask(childTaskId) {
    // Custom method for task-specific functionality
    console.log("Toggle child task:", childTaskId);
    
    // TODO: Implement actual toggle logic
    // This would typically make an API call to update the task status
}

// Contact modal handlers
function initializeContactModal() {
    // Contact-specific modal initialization
    console.log("Contact modal initialized");
}

// Company modal handlers  
function initializeCompanyModal() {
    // Company-specific modal initialization
    console.log("Company modal initialized");
}

// Opportunity modal handlers
function initializeOpportunityModal() {
    // Opportunity-specific modal initialization
    console.log("Opportunity modal initialized");
}

// Bulk task creation handlers
window.bulkCreateTasks = function(selectedIds, entityType = 'unknown') {
    if (selectedIds.length === 0) return;
    
    console.log("Creating tasks for " + entityType + ":", selectedIds);
    
    // Route based on entity type
    let baseUrl = '/tasks/multi_new';
    let param = '';
    
    switch(entityType) {
        case 'companies':
            param = `company_ids=${selectedIds.join(',')}`;
            break;
        case 'contacts':
            param = `contact_ids=${selectedIds.join(',')}`;
            break;
        case 'opportunities':
            param = `opportunity_ids=${selectedIds.join(',')}`;
            break;
        default:
            console.warn("Unknown entity type:", entityType);
            return;
    }
    
    window.location.href = `${baseUrl}?${param}`;
};

// Task creation for single opportunities
function createTaskForOpportunity(opportunityId) {
    console.log("Creating task for opportunity:", opportunityId);
    alert("Task creation feature coming soon!");
}

// Modal event handlers
function openOpportunityDetailModal(opportunityId) {
    window.dispatchEvent(new CustomEvent('open-opportunity-detail-modal', { 
        detail: { opportunityId } 
    }));
}

// Generic modal utilities
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function openModal(modalId, data = {}) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        // Populate modal with data if provided
        if (data && typeof data === 'object') {
            Object.keys(data).forEach(key => {
                const element = modal.querySelector(`[name="${key}"]`);
                if (element) {
                    element.value = data[key];
                }
            });
        }
    }
}

// Export functions for use in other modules
window.modalHandlers = {
    toggleChildTask,
    initializeContactModal,
    initializeCompanyModal, 
    initializeOpportunityModal,
    createTaskForOpportunity,
    openOpportunityDetailModal,
    closeModal,
    openModal
};