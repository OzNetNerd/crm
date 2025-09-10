// Teams-specific JavaScript functionality
// Account team management and interactions

// Team-specific bulk action functions
window.bulkDelete = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    if (!confirm(`Are you sure you want to remove ${selectedIds.length} selected team members?`)) {
        return;
    }
    
    // Remove each selected team member
    selectedIds.forEach(async (memberId) => {
        try {
            const response = await fetch(`/api/teams/${memberId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                // Remove member from local data
                window.teamData = window.teamData.filter(m => m.id.toString() !== memberId.toString());
            }
        } catch (error) {
            console.error('Error removing team member:', error);
        }
    });
    
    // Refresh the page to show changes
    setTimeout(() => location.reload(), 1000);
};

window.bulkAssignToCompany = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    console.log("Assigning team members to company:", selectedIds);
    // Open a modal to select company for bulk assignment
    openBulkCompanyAssignmentModal(selectedIds);
};

// Team-specific functions for account team interactions
window.assignToCompany = function(memberId) {
    console.log("Assigning team member to company:", memberId);
    openCompanyAssignmentModal(memberId);
};

window.assignToOpportunity = function(memberId) {
    console.log("Assigning team member to opportunity:", memberId);
    openOpportunityAssignmentModal(memberId);
};

window.assignAccountTeam = function(companyId) {
    console.log("Assigning account team to company:", companyId);
    openAccountTeamAssignmentModal(companyId);
};

window.assignAccountTeamToOpportunity = function(opportunityId) {
    console.log("Assigning account team to opportunity:", opportunityId);
    openOpportunityAccountTeamModal(opportunityId);
};

window.viewTeamMemberDetails = function(memberId) {
    console.log("Viewing team member details:", memberId);
    // Navigate to team member detail page or open modal
    window.location.href = `/teams/${memberId}`;
};

// Modal functions for team management
function openCompanyAssignmentModal(memberId) {
    // Create a modal to select which company to assign the team member to
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-container">
            <div class="modal-header">
                <h3>Assign to Company</h3>
                <button onclick="closeModal()" class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <p>Select a company to assign this team member:</p>
                <select id="company-select" class="w-full p-2 border rounded">
                    <option value="">Select a company...</option>
                    ${window.companiesData ? window.companiesData.map(c => 
                        `<option value="${c.id}">${c.name}</option>`
                    ).join('') : ''}
                </select>
            </div>
            <div class="modal-footer">
                <button onclick="closeModal()" class="btn-secondary">Cancel</button>
                <button onclick="confirmCompanyAssignment(${memberId})" class="btn-primary">Assign</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function openOpportunityAssignmentModal(memberId) {
    // Create a modal to select which opportunity to assign the team member to
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-container">
            <div class="modal-header">
                <h3>Assign to Opportunity</h3>
                <button onclick="closeModal()" class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <p>Select an opportunity to assign this team member:</p>
                <select id="opportunity-select" class="w-full p-2 border rounded">
                    <option value="">Select an opportunity...</option>
                    ${window.opportunitiesData ? window.opportunitiesData.map(o => 
                        `<option value="${o.id}">${o.name} (${o.company_name || 'Unknown Company'})</option>`
                    ).join('') : ''}
                </select>
            </div>
            <div class="modal-footer">
                <button onclick="closeModal()" class="btn-secondary">Cancel</button>
                <button onclick="confirmOpportunityAssignment(${memberId})" class="btn-primary">Assign</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function openAccountTeamAssignmentModal(companyId) {
    // Create a modal to assign team members to a company
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-container">
            <div class="modal-header">
                <h3>Assign Account Team</h3>
                <button onclick="closeModal()" class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <p>Select team members to assign to this company:</p>
                <div class="space-y-2 max-h-64 overflow-y-auto">
                    ${window.teamData ? window.teamData.map(member => `
                        <label class="flex items-center space-x-2">
                            <input type="checkbox" value="${member.id}" name="team-members" class="rounded">
                            <span>${member.name} (${member.job_title})</span>
                        </label>
                    `).join('') : ''}
                </div>
            </div>
            <div class="modal-footer">
                <button onclick="closeModal()" class="btn-secondary">Cancel</button>
                <button onclick="confirmAccountTeamAssignment(${companyId})" class="btn-primary">Assign Team</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function confirmCompanyAssignment(memberId) {
    const companyId = document.getElementById('company-select').value;
    if (!companyId) {
        alert('Please select a company');
        return;
    }
    
    // Make API call to assign team member to company
    fetch('/api/company-account-teams', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: memberId,
            company_id: companyId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            location.reload(); // Refresh to show changes
        } else {
            alert('Error assigning team member: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error assigning team member');
    });
}

function confirmOpportunityAssignment(memberId) {
    const opportunityId = document.getElementById('opportunity-select').value;
    if (!opportunityId) {
        alert('Please select an opportunity');
        return;
    }
    
    // Make API call to assign team member to opportunity
    fetch('/api/opportunity-account-teams', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: memberId,
            opportunity_id: opportunityId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            location.reload(); // Refresh to show changes
        } else {
            alert('Error assigning team member: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error assigning team member');
    });
}

function confirmAccountTeamAssignment(companyId) {
    const selectedMembers = Array.from(document.querySelectorAll('input[name="team-members"]:checked'))
        .map(checkbox => checkbox.value);
    
    if (selectedMembers.length === 0) {
        alert('Please select at least one team member');
        return;
    }
    
    // Make API calls to assign multiple team members to company
    Promise.all(selectedMembers.map(memberId => 
        fetch('/api/company-account-teams', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: memberId,
                company_id: companyId
            })
        })
    ))
    .then(responses => Promise.all(responses.map(r => r.json())))
    .then(results => {
        const failures = results.filter(r => !r.success);
        if (failures.length === 0) {
            closeModal();
            location.reload(); // Refresh to show changes
        } else {
            alert(`Some assignments failed: ${failures.map(f => f.message).join(', ')}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error assigning team members');
    });
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}

// Team-specific functions that extend the centralized modal system
function createTaskForTeamMember(memberId) {
    createTask('user', memberId);
}

// Initialize team-specific data when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Get team data from the template
    const appData = document.getElementById('app-data');
    if (appData) {
        window.teamData = JSON.parse(appData.getAttribute('data-team-members') || '[]');
        window.companiesData = JSON.parse(appData.getAttribute('data-companies') || '[]');
        window.opportunitiesData = JSON.parse(appData.getAttribute('data-opportunities') || '[]');
    }
});