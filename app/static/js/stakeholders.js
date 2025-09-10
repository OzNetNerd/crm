// Contacts-specific JavaScript functionality
// Extracted from contacts/index.html template

// Contact-specific bulk action functions
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
                window.contactsData = window.contactsData.filter(c => c.id.toString() !== contactId.toString());
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

// Contact-specific functions that extend the centralized modal system
function createTaskForContact(contactId) {
    createTask('contact', contactId);
}

function createOpportunityForContact(contactId) {
    createOpportunity('contact', contactId);
}

// Contacts use the centralized entity manager system
// All modal functions including deleteContact are now handled globally