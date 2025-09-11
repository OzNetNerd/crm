/**
 * Essential Entity Manager - Event delegation for dynamic content
 * 
 * Minimal functionality for HTMX-based application.
 * Filtering, sorting, and grouping now handled server-side.
 * Only keeps event delegation for dynamically rendered entity cards.
 */

/**
 * Setup event delegation for entity actions
 * @param {string} containerSelector - CSS selector for content container
 * @param {string} entityName - Entity type name for data attributes
 * @param {Object} actions - Action mapping { 'Action Name': 'handlerFunction' }
 */
function setupEntityEventDelegation(containerSelector, entityName, actions = {}) {
    const contentContainer = document.querySelector(containerSelector);
    if (!contentContainer) return;

    // Event delegation for all entity card buttons
    contentContainer.addEventListener('click', (e) => {
        const button = e.target.closest('button[title]');
        if (!button) return;

        const entityCard = button.closest(`[data-${entityName}-id]`);
        if (!entityCard) return;

        const entityId = parseInt(entityCard.getAttribute(`data-${entityName}-id`));
        if (!entityId) return;

        e.stopPropagation();

        // Route to appropriate action based on button title
        const title = button.getAttribute('title');
        const handler = actions[title];
        
        if (handler && window[handler]) {
            window[handler](entityId);
        } else {
            console.warn(`No handler found for action: ${title}`);
        }
    });
}

// Global availability
window.setupEntityEventDelegation = setupEntityEventDelegation;