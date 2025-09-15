/**
 * Entity Card Component
 * Handles all entity card interactions without inline event handlers
 */

document.addEventListener('DOMContentLoaded', () => {
    // Handle entity card clicks
    document.addEventListener('click', (e) => {
        // Card click - open detail modal
        const card = e.target.closest('[data-entity-card]');
        if (card && !e.target.closest('button') && !e.target.closest('input')) {
            e.stopPropagation();
            const { entityType, entityId } = card.dataset;

            window.dispatchEvent(new CustomEvent(`open-detail-${entityType}-modal`, {
                detail: { id: parseInt(entityId), readOnly: true }
            }));
        }

        // Complete task button
        const completeBtn = e.target.closest('[data-action="complete"]');
        if (completeBtn) {
            e.stopPropagation();
            const { entityType, entityId } = completeBtn.dataset;

            confirmAction('complete', entityType, entityId,
                'Complete Task',
                'Are you sure you want to mark this task as complete?',
                'Complete',
                'btn-success'
            );
        }

        // Edit button
        const editBtn = e.target.closest('[data-action="edit"]');
        if (editBtn) {
            e.stopPropagation();
            const { entityType, entityId } = editBtn.dataset;

            window.dispatchEvent(new CustomEvent(`open-detail-${entityType}-modal`, {
                detail: { id: parseInt(entityId) }
            }));
        }

        // Delete button
        const deleteBtn = e.target.closest('[data-action="delete"]');
        if (deleteBtn) {
            e.stopPropagation();
            const { entityType, entityId } = deleteBtn.dataset;
            const entityTitle = entityType.charAt(0).toUpperCase() + entityType.slice(1);

            confirmAction('delete', entityType, entityId,
                `Delete ${entityTitle}`,
                `Are you sure you want to delete this ${entityType}?`,
                'Delete',
                'btn-danger'
            );
        }

        // View details button
        const viewBtn = e.target.closest('[data-action="view"]');
        if (viewBtn) {
            e.stopPropagation();
            const { entityType, entityId } = viewBtn.dataset;

            window.dispatchEvent(new CustomEvent(`open-detail-${entityType}-modal`, {
                detail: { id: parseInt(entityId), readOnly: true }
            }));
        }

        // Generic action button with custom event
        const actionBtn = e.target.closest('[data-action][data-event]');
        if (actionBtn && !actionBtn.dataset.action.match(/^(complete|edit|delete|view)$/)) {
            e.stopPropagation();
            const { event: eventName, ...data } = actionBtn.dataset;

            window.dispatchEvent(new CustomEvent(eventName, { detail: data }));
        }
    });

    // Handle create buttons
    document.addEventListener('click', (e) => {
        const createBtn = e.target.closest('[data-create-entity]');
        if (createBtn) {
            const { createEntity } = createBtn.dataset;
            window.dispatchEvent(new CustomEvent(`open-create-${createEntity}-modal`));
        }
    });

    // Handle search result selections
    document.addEventListener('click', (e) => {
        const searchResult = e.target.closest('[data-search-result]');
        if (searchResult) {
            e.preventDefault();
            const { fieldId, resultId, resultTitle, resultType } = searchResult.dataset;

            if (window.selectEntity) {
                selectEntity(fieldId, resultId, resultTitle, resultType);
            }
        }
    });
});