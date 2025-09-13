/**
 * Multi-task creation functionality
 * Handles showing/hiding child task forms in the multi-create interface
 */

/**
 * Shows the next hidden child task form
 */
function showNextChildTask() {
    const hiddenTask = document.querySelector('.child-task.hidden');
    if (hiddenTask) {
        hiddenTask.classList.remove('hidden');
    }
}

// Export functions for module usage
export { showNextChildTask };