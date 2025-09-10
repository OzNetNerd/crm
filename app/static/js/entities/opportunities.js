// Opportunities-specific JavaScript functionality
// Entity-specific functions for opportunities management

// Opportunity-specific bulk action functions
window.bulkDelete = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    if (!confirm(`Are you sure you want to delete ${selectedIds.length} selected opportunities?`)) {
        return;
    }
    
    // Delete each selected opportunity
    selectedIds.forEach(async (opportunityId) => {
        try {
            const response = await fetch(`/opportunities/${opportunityId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                // Remove opportunity from local data
                window.opportunitiesData = window.opportunitiesData.filter(o => o.id.toString() !== opportunityId.toString());
            }
        } catch (error) {
            console.error('Error deleting opportunity:', error);
        }
    });
    
    // Refresh the page to show changes
    setTimeout(() => location.reload(), 1000);
};

window.bulkCreateTasks = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    console.log("Creating tasks for opportunities:", selectedIds);
    // Here you would open a modal to create tasks for selected opportunities
    // For now, just redirect to task creation page
    window.location.href = `/tasks/multi_new?opportunity_ids=${selectedIds.join(',')}`;
};

// Opportunity-specific functions that extend the centralized modal system
function createTaskForOpportunity(opportunityId) {
    createTask('opportunity', opportunityId);
}

// Opportunities use the centralized entity manager system
// All modal functions including deleteOpportunity are now handled globally