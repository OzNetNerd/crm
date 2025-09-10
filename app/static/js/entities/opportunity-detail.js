// Opportunity detail page JavaScript functionality
// Extracted from opportunities/detail.html template

function createTaskForOpportunity(opportunityId) {
    // TODO: Implement task creation for opportunity
    console.log("Creating task for opportunity:", opportunityId);
    alert("Task creation feature coming soon!");
}

function openOpportunityDetailModal(opportunityId) {
    window.dispatchEvent(new CustomEvent('open-opportunity-detail-modal', { detail: { opportunityId } }));
}

function openCompanyDetailModal(companyId) {
    window.dispatchEvent(new CustomEvent('open-company-detail-modal', { detail: { companyId } }));
}