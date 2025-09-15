/**
 * Entity Actions
 * Handles entity card actions like delete, complete, etc.
 * Extracted from entity_card.html macro
 */

// DRY confirmation function for all confirmable actions
function confirmAction(action, entityType, entityId, title, message, confirmText, confirmClass) {
  window.dispatchEvent(new CustomEvent('open-confirmation-modal', {
    detail: {
      title: title,
      message: message,
      confirmText: confirmText,
      confirmClass: confirmClass,
      confirmAction: () => {
        if (action === 'delete') {
          deleteEntity(entityType, entityId);
        } else if (action === 'complete') {
          completeTask(entityId);
        }
      }
    }
  }));
}

function completeTask(taskId) {
  fetch(`/dashboard/tasks/${taskId}/complete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  })
  .then(response => {
    if (response.ok) {
      // Reload the content area to show updated task
      location.reload();
    }
  });
}

function deleteEntity(entityType, entityId) {
  fetch(`/api/entities/${entityType}/${entityId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    }
  })
  .then(response => {
    if (response.ok) {
      // Reload the content area to show updated list
      location.reload();
    }
  });
}