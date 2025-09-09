// Companies-specific JavaScript functionality
// Extracted from companies/index.html template

// Company-specific bulk action functions
window.bulkDelete = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    if (!confirm(`Are you sure you want to delete ${selectedIds.length} selected companies?`)) {
        return;
    }
    
    // Delete each selected company
    selectedIds.forEach(async (companyId) => {
        try {
            const response = await fetch(`/api/companies/${companyId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                // Remove company from local data
                window.companiesData = window.companiesData.filter(c => c.id.toString() !== companyId.toString());
            }
        } catch (error) {
            console.error('Error deleting company:', error);
        }
    });
    
    // Refresh the page to show changes
    setTimeout(() => location.reload(), 1000);
};

window.bulkCreateTasks = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    console.log("Creating tasks for companies:", selectedIds);
    // Here you would open a modal to create tasks for selected companies
    // For now, just redirect to task creation page
    window.location.href = `/tasks/multi_new?company_ids=${selectedIds.join(',')}`;
};

// Company-specific functions that extend the centralized modal system
function createTaskForCompany(companyId) {
    createTask('company', companyId);
}

function createContactForCompany(companyId) {
    createContact('company', companyId);
}

function createOpportunityForCompany(companyId) {
    createOpportunity('company', companyId);
}

// Companies use the centralized entity manager system
// All modal functions including deleteCompany are now handled globally