// Enhanced Alpine.js interactivity for the dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Persist section states in localStorage
    Alpine.store('dashboard', {
        sections: JSON.parse(localStorage.getItem('dashboard-sections') || JSON.stringify({
            overdue: true,
            today: true,
            thisWeek: false,
            nextWeek: false,
            completedToday: false,
            byCompany: false,
            byPriority: false
        })),
        
        filters: {
            priority: '',
            entity: '',
            search: ''
        },
        
        selectedTasks: [],
        
        toggleSection(section) {
            this.sections[section] = !this.sections[section];
            localStorage.setItem('dashboard-sections', JSON.stringify(this.sections));
        },
        
        expandAll() {
            Object.keys(this.sections).forEach(key => {
                this.sections[key] = true;
            });
            localStorage.setItem('dashboard-sections', JSON.stringify(this.sections));
        },
        
        collapseAll() {
            Object.keys(this.sections).forEach(key => {
                this.sections[key] = false;
            });
            // Keep critical sections expanded
            this.sections.overdue = true;
            this.sections.today = true;
            localStorage.setItem('dashboard-sections', JSON.stringify(this.sections));
        },
        
        toggleTaskSelection(taskId) {
            const index = this.selectedTasks.indexOf(taskId);
            if (index > -1) {
                this.selectedTasks.splice(index, 1);
            } else {
                this.selectedTasks.push(taskId);
            }
        },
        
        selectAllTasks(taskIds) {
            this.selectedTasks = [...new Set([...this.selectedTasks, ...taskIds])];
        },
        
        deselectAllTasks() {
            this.selectedTasks = [];
        }
    });
});

// Task management functions with better error handling and UX feedback
class TaskManager {
    static async completeTask(taskId, showNotification = true) {
        try {
            const response = await fetch(`/tasks/${taskId}/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                if (showNotification) {
                    this.showNotification('Task completed successfully', 'success');
                }
                // Smooth removal animation and dynamic DOM update
                const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
                if (taskCard) {
                    taskCard.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                    taskCard.style.opacity = '0';
                    taskCard.style.transform = 'translateY(-10px)';
                    setTimeout(() => {
                        // Remove the task card from DOM
                        taskCard.remove();
                        
                        // Update section counters dynamically
                        this.updateSectionCounters();
                        
                        // Update parent task progress if needed
                        this.updateParentTaskProgress(taskId);
                    }, 300);
                }
            } else {
                throw new Error('Failed to complete task');
            }
        } catch (error) {
            console.error('Error completing task:', error);
            this.showNotification('Failed to complete task', 'error');
        }
    }

    static async rescheduleTask(taskId, days, showNotification = true) {
        try {
            const response = await fetch(`/tasks/${taskId}/reschedule`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ days })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                if (showNotification) {
                    const dayText = days === 1 ? 'day' : 'days';
                    this.showNotification(`Task rescheduled by ${days} ${dayText}`, 'success');
                }
                
                // Quick refresh to show updated data - simple and reliable
                setTimeout(() => location.reload(), 200);
            } else {
                throw new Error('Failed to reschedule task');
            }
        } catch (error) {
            console.error('Error rescheduling task:', error);
            this.showNotification('Failed to reschedule task', 'error');
        }
    }

    static async updateTask(taskId, updates, showNotification = false) {
        try {
            const response = await fetch(`/tasks/${taskId}/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });
            
            if (response.ok) {
                if (showNotification) {
                    this.showNotification('Task updated successfully', 'success');
                }
            } else {
                throw new Error('Failed to update task');
            }
        } catch (error) {
            console.error('Error updating task:', error);
            this.showNotification('Failed to update task', 'error');
        }
    }

    static async deleteTask(taskId) {
        try {
            const response = await fetch(`/tasks/${taskId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                this.showNotification('Task deleted successfully', 'success');
                const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
                if (taskCard) {
                    taskCard.style.transition = 'opacity 0.3s ease-out';
                    taskCard.style.opacity = '0';
                    setTimeout(() => {
                        taskCard.remove();
                    }, 300);
                }
            } else {
                throw new Error('Failed to delete task');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            this.showNotification('Failed to delete task', 'error');
        }
    }

    static async bulkCompleteTask(taskIds) {
        try {
            const promises = taskIds.map(id => this.completeTask(id, false));
            await Promise.all(promises);
            this.showNotification(`${taskIds.length} tasks completed`, 'success');
            // No need to reload - individual completeTask calls handle DOM updates
        } catch (error) {
            console.error('Error bulk completing tasks:', error);
            this.showNotification('Failed to complete some tasks', 'error');
        }
    }

    static updateSectionCounters() {
        // Update badge counts in section headers after task completion
        // Find badges by their parent section headers to avoid affecting priority badges
        
        // Update section count badges by finding them within section headers
        const sectionHeaderSelectors = [
            // Status sections
            { headerText: 'To Do', selector: '[x-show="expandedSections[\'todo\']"]' },
            { headerText: 'In Progress', selector: '[x-show="expandedSections[\'in-progress\']"]' },
            { headerText: 'Completed', selector: '[x-show="expandedSections[\'complete\']"]' },
            // Priority sections  
            { headerText: 'High Priority', selector: '[x-show="expandedSections[\'high\']"]' },
            { headerText: 'Medium Priority', selector: '[x-show="expandedSections[\'medium\']"]' },
            { headerText: 'Low Priority', selector: '[x-show="expandedSections[\'low\']"]' },
            // Due date sections
            { headerText: 'Overdue', selector: '[x-show="expandedSections[\'overdue\']"]' },
            { headerText: 'Due Today', selector: '[x-show="expandedSections[\'today\']"]' },
            { headerText: 'This Week', selector: '[x-show="expandedSections[\'this_week\']"]' },
            { headerText: 'Later', selector: '[x-show="expandedSections[\'later\']"]' },
            { headerText: 'No Due Date', selector: '[x-show="expandedSections[\'no_date\']"]' },
            // Entity sections
            { headerText: 'Company Tasks', selector: '[x-show="expandedSections[\'company\']"]' },
            { headerText: 'Contact Tasks', selector: '[x-show="expandedSections[\'contact\']"]' },
            { headerText: 'Opportunity Tasks', selector: '[x-show="expandedSections[\'opportunity\']"]' },
            { headerText: 'General Tasks', selector: '[x-show="expandedSections[\'unrelated\']"]' }
        ];
        
        // Update each section's count badge
        sectionHeaderSelectors.forEach(({ headerText, selector }) => {
            const section = document.querySelector(selector);
            if (section) {
                const taskCount = section.querySelectorAll('.task-card').length;
                
                // Find the header with the specific text and update its badge
                const headers = document.querySelectorAll('h3');
                for (const header of headers) {
                    if (header.textContent && header.textContent.includes(headerText)) {
                        const badge = header.querySelector('.badge-standard');
                        if (badge) {
                            badge.textContent = taskCount;
                            break;
                        }
                    }
                }
            }
        });
        
        // Also update the page summary statistics at the top
        this.updatePageSummaryStats();
    }
    
    static updatePageSummaryStats() {
        // Update the summary statistics at the top of the page
        // Count all tasks on the page by their current status
        
        const todoTasks = document.querySelectorAll('[x-show="expandedSections[\'todo\']"] .task-card').length;
        const inProgressTasks = document.querySelectorAll('[x-show="expandedSections[\'in-progress\']"] .task-card').length;
        const completeTasks = document.querySelectorAll('[x-show="expandedSections[\'complete\']"] .task-card').length;
        
        // Count overdue tasks (they can be in any status section but have overdue badges)
        const overdueTasks = document.querySelectorAll('.text-badge-overdue, [class*="overdue"]').length;
        
        // Find summary stat elements - they're in the grid layout within the card
        const summaryGrid = document.querySelector('.grid-cols-2.md\\:grid-cols-4');
        if (summaryGrid) {
            const summaryStats = summaryGrid.querySelectorAll('.text-center');
            
            if (summaryStats.length >= 4) {
                // Update the summary numbers based on the order in the template:
                // To Do, In Progress, Complete, Overdue
                const todoValue = summaryStats[0].querySelector('.text-2xl');
                const inProgressValue = summaryStats[1].querySelector('.text-2xl');
                const completeValue = summaryStats[2].querySelector('.text-2xl');
                const overdueValue = summaryStats[3].querySelector('.text-2xl');
                
                if (todoValue) todoValue.textContent = todoTasks;
                if (inProgressValue) inProgressValue.textContent = inProgressTasks;
                if (completeValue) completeValue.textContent = completeTasks;
                if (overdueValue) overdueValue.textContent = overdueTasks;
            }
        }
    }

    static async updateParentTaskProgress(completedTaskId) {
        // Update parent task progress bars for all parent tasks on the page
        try {
            // Find all task cards and check which ones have progress bars (parent tasks)
            const allTaskCards = document.querySelectorAll('.task-card');
            
            for (const taskCard of allTaskCards) {
                // Check if this task has a progress bar (indicating it's a parent task)
                const progressBar = taskCard.querySelector('.bg-blue-600.h-2.rounded-full');
                if (progressBar) {
                    const parentId = taskCard.dataset.taskId;
                    if (parentId) {
                        // Fetch updated parent task data
                        const response = await fetch(`/api/tasks/${parentId}`);
                        if (response.ok) {
                            const taskData = await response.json();
                            
                            // Update progress bar width
                            progressBar.style.width = `${taskData.completion_percentage}%`;
                            
                            // Find and update the "Tasks: X/Y" text and percentage
                            if (taskData.child_tasks) {
                                const completedCount = taskData.child_tasks.filter(t => t.status === 'complete').length;
                                const totalCount = taskData.child_tasks.length;
                                
                                // Update the "Tasks: X/Y" text - it's a <p> with class text-label-primary
                                const tasksText = taskCard.querySelector('p.text-label-primary');
                                if (tasksText && tasksText.textContent.includes('Tasks:')) {
                                    tasksText.textContent = `Tasks: ${completedCount}/${totalCount}`;
                                }
                                
                                // Update the percentage text - it's a <span> with class text-label-primary next to the progress bar
                                // Look for the percentage span more specifically - it should contain a % sign
                                const percentageSpan = taskCard.querySelector('span.text-label-primary');
                                if (percentageSpan && percentageSpan.textContent.includes('%')) {
                                    percentageSpan.textContent = `${taskData.completion_percentage}%`;
                                }
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error updating parent task progress:', error);
        }
    }

    static showNotification(message, type = 'info') {
        // Simple notification system - can be enhanced
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-md text-white z-50 ${
            type === 'success' ? 'bg-green-500' :
            type === 'error' ? 'bg-red-500' :
            'bg-blue-500'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.transition = 'opacity 0.3s ease-out';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Modal management
class ModalManager {
    static openTaskModal(taskId) {
        // TODO: Implement full task details modal
        console.log('Opening task modal for:', taskId);
    }

    static openNewTaskModal() {
        // Reset modal state before opening
        if (typeof resetTask === 'function') {
            resetTask();
        }
        // Trigger the modal to open
        window.dispatchEvent(new CustomEvent('open-new-task-modal'));
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N: New task
    if ((e.ctrlKey || e.metaKey) && e.key === 'n' && !e.target.matches('input, textarea')) {
        e.preventDefault();
        ModalManager.openNewTaskModal();
    }
    
    // Escape: Close modals/deselect tasks
    if (e.key === 'Escape') {
        // Close any open modals
        window.dispatchEvent(new CustomEvent('close-modal'));
        // Deselect tasks
        Alpine.store('dashboard').deselectAllTasks();
    }
});

// Export for global access
window.TaskManager = TaskManager;
window.ModalManager = ModalManager;

// Global confirmation modal function
window.showConfirmationModal = function(options) {
    window.dispatchEvent(new CustomEvent('open-confirmation-modal', {
        detail: {
            title: options.title || 'Confirm Action',
            message: options.message || '',
            confirmText: options.confirmText || 'Confirm',
            confirmClass: options.confirmClass || 'bg-blue-600 hover:bg-blue-700',
            confirmAction: options.confirmAction
        }
    }));
};

// Global function wrappers with confirmation dialogs
window.completeTask = function(taskId) {
    window.showConfirmationModal({
        title: 'Complete Task',
        message: 'Are you sure you want to mark this task as complete?',
        confirmText: 'Complete',
        confirmClass: 'bg-green-600 hover:bg-green-700',
        confirmAction: () => TaskManager.completeTask(taskId)
    });
};

window.rescheduleTask = function(taskId, days) {
    const dayText = days === 1 ? 'day' : 'days';
    window.showConfirmationModal({
        title: 'Reschedule Task',
        message: `Are you sure you want to reschedule this task by ${days} ${dayText}?`,
        confirmText: 'Reschedule',
        confirmClass: 'bg-blue-600 hover:bg-blue-700',
        confirmAction: () => TaskManager.rescheduleTask(taskId, days)
    });
};

window.editTask = function(taskId) {
    // Use the existing comprehensive task detail modal for editing
    openTaskDetailModal(taskId);
};

window.deleteTask = function(taskId) {
    window.showConfirmationModal({
        title: 'Delete Task',
        message: 'Are you sure you want to delete this task? This action cannot be undone.',
        confirmText: 'Delete',
        confirmClass: 'bg-red-600 hover:bg-red-700',
        confirmAction: () => TaskManager.deleteTask(taskId)
    });
};

window.updateTask = function(taskId, updates) {
    return TaskManager.updateTask(taskId, updates);
};

window.openTaskModal = function(taskId) {
    return ModalManager.openTaskModal(taskId);
};

window.saveReschedule = function(taskId, days) {
    if (days === 0) return; // No changes to save
    
    return TaskManager.rescheduleTask(taskId, days).then(() => {
        // Reset the editing state after successful save
        const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
        if (taskCard) {
            // Trigger Alpine.js data reset
            taskCard.dispatchEvent(new CustomEvent('reschedule-saved'));
        }
    });
};