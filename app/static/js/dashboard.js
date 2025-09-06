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
                // Smooth removal animation
                const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
                if (taskCard) {
                    taskCard.style.transition = 'opacity 0.3s ease-out';
                    taskCard.style.opacity = '0';
                    setTimeout(() => {
                        location.reload(); // TODO: Replace with dynamic update
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
                if (showNotification) {
                    const dayText = days === 1 ? 'day' : 'days';
                    this.showNotification(`Task rescheduled by ${days} ${dayText}`, 'success');
                }
                setTimeout(() => location.reload(), 500);
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
            location.reload();
        } catch (error) {
            console.error('Error bulk completing tasks:', error);
            this.showNotification('Failed to complete some tasks', 'error');
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