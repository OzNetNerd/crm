// Initialize tasks data from server
function initTasksData(companiesData, contactsData, opportunitiesData, tasksData) {
    window.companiesData = companiesData;
    window.contactsData = contactsData;
    window.opportunitiesData = opportunitiesData;
    window.tasksData = tasksData;
}

// Bulk action functions for tasks
window.bulkUpdateTaskStatus = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    const newStatus = prompt('Enter new status (todo, in-progress, complete):');
    if (!newStatus) return;
    
    if (!['todo', 'in-progress', 'complete'].includes(newStatus)) {
        alert('Invalid status. Please use: todo, in-progress, or complete');
        return;
    }
    
    // Update each selected task
    selectedIds.forEach(async (taskId) => {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus })
            });
            
            if (response.ok) {
                // Update task in local data
                const taskIndex = window.tasksData.findIndex(t => t.id.toString() === taskId.toString());
                if (taskIndex !== -1) {
                    window.tasksData[taskIndex].status = newStatus;
                }
            }
        } catch (error) {
            console.error('Error updating task:', error);
        }
    });
    
    // Refresh the page to show changes
    setTimeout(() => location.reload(), 1000);
};

window.bulkDeleteTasks = function(selectedIds) {
    if (selectedIds.length === 0) return;
    
    if (!confirm(`Are you sure you want to delete ${selectedIds.length} selected tasks?`)) {
        return;
    }
    
    // Delete each selected task
    selectedIds.forEach(async (taskId) => {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                // Remove task from local data
                window.tasksData = window.tasksData.filter(t => t.id.toString() !== taskId.toString());
            }
        } catch (error) {
            console.error('Error deleting task:', error);
        }
    });
    
    // Refresh the page to show changes
    setTimeout(() => location.reload(), 1000);
};
// Tasks use the centralized modal system from modal-manager.js
// All modal functions including deleteTask are now handled globally