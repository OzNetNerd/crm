// Stakeholders-specific JavaScript functionality
// Extracted from contacts/index.html template

// Stakeholder-specific bulk action functions
window.bulkDelete = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    if (!confirm(`Are you sure you want to delete ${selectedIds.length} selected contacts?`)) {
        return;
    }
    
    // Delete each selected contact
    selectedIds.forEach(async (contactId) => {
        try {
            const response = await fetch(`/api/contacts/${contactId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                // Remove contact from local data
                window.stakeholdersData = window.stakeholdersData.filter(c => c.id.toString() !== contactId.toString());
            }
        } catch (error) {
            console.error('Error deleting contact:', error);
        }
    });
    
    // Refresh the page to show changes
    setTimeout(() => location.reload(), 1000);
};

window.bulkCreateTasks = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    console.log("Creating tasks for contacts:", selectedIds);
    // Here you would open a modal to create tasks for selected contacts
    // For now, just redirect to task creation page
    window.location.href = `/tasks/multi_new?contact_ids=${selectedIds.join(',')}`;
};

// Stakeholder-specific functions that extend the centralized modal system
function createTaskForStakeholder(contactId) {
    createTask('contact', contactId);
}

function createOpportunityForStakeholder(contactId) {
    createOpportunity('contact', contactId);
}

// Stakeholders use the centralized entity manager system
// All modal functions including deleteStakeholder are now handled globally