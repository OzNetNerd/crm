/**
 * Unified Search Widget Handler
 *
 * Handles ALL search functionality - both global search and entity search widgets
 * DRY implementation that works with any search input using HTMX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all search widgets on the page
    initializeSearchWidgets();

    // Re-initialize when new content is loaded via HTMX
    document.addEventListener('htmx:afterSwap', function(event) {
        // If a modal was loaded, initialize any search widgets in it
        if (event.target.classList.contains('modal-overlay')) {
            initializeSearchWidgets();
        }
    });
});

function initializeSearchWidgets() {
    // Find all search inputs - now unified with .search-input class
    const searchInputs = document.querySelectorAll('.search-input');

    searchInputs.forEach(input => {
        // Skip if already initialized
        if (input.dataset.searchInitialized) return;

        const resultsId = input.getAttribute('hx-target');
        const resultsDiv = document.querySelector(resultsId);

        if (!resultsDiv) return;

        // Mark as initialized
        input.dataset.searchInitialized = 'true';

        // Show results when HTMX loads content
        input.addEventListener('htmx:afterSwap', function() {
            if (resultsDiv.children.length > 0) {
                resultsDiv.classList.remove('hidden');
            }
        });

        // Hide results when input is cleared
        input.addEventListener('input', function() {
            if (!this.value.trim()) {
                resultsDiv.classList.add('hidden');
            }
        });

        // Show results when focusing input if there's content
        input.addEventListener('focus', function() {
            if (resultsDiv.children.length > 0) {
                resultsDiv.classList.remove('hidden');
            }
        });
    });

    // Handle click outside to close dropdowns
    document.addEventListener('click', function(event) {
        // Close all search dropdowns when clicking outside
        document.querySelectorAll('.search-results').forEach(resultsDiv => {
            const container = resultsDiv.closest('.search-container');

            // Check if click is outside the search container
            if (container && !container.contains(event.target)) {
                resultsDiv.classList.add('hidden');
            }
        });
    });

    // Handle escape key to close dropdowns
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('.search-results:not(.hidden)').forEach(resultsDiv => {
                resultsDiv.classList.add('hidden');
                // Blur the associated input
                const container = resultsDiv.closest('.search-container');
                if (container) {
                    const input = container.querySelector('.search-input');
                    if (input) input.blur();
                }
            });
        }
    });
}

// Make selectEntity globally available for search results to call
window.selectEntity = function(fieldId, entityId, entityName, entityType) {
    const searchField = document.getElementById(fieldId);
    const dataField = document.getElementById(fieldId + '-data');
    const badgesDiv = document.getElementById(fieldId + '-badges');
    const resultsDiv = document.getElementById(fieldId + '-results');

    if (!dataField || !badgesDiv) return;

    // Parse existing data
    let entities = [];
    try {
        entities = JSON.parse(dataField.value || '[]');
    } catch (e) {
        entities = [];
    }

    // Check if already selected
    if (entities.some(e => e.id == entityId && e.type === entityType)) {
        // Clear search and hide results
        if (searchField) searchField.value = '';
        if (resultsDiv) resultsDiv.classList.add('hidden');
        return;
    }

    // Add new entity
    entities.push({
        id: entityId,
        name: entityName,
        type: entityType
    });

    // Update hidden field
    dataField.value = JSON.stringify(entities);

    // Create badge
    createEntityBadge(fieldId, entityId, entityName, entityType);

    // Clear search and hide results
    if (searchField) {
        searchField.value = '';
        // Trigger input event to ensure HTMX clears results
        searchField.dispatchEvent(new Event('input', { bubbles: true }));
    }
    if (resultsDiv) resultsDiv.classList.add('hidden');
};

window.createEntityBadge = function(fieldId, entityId, entityName, entityType) {
    const badgesDiv = document.getElementById(fieldId + '-badges');
    if (!badgesDiv) return;

    // Check if badge already exists
    if (badgesDiv.querySelector(`[data-entity-id="${entityId}"][data-entity-type="${entityType}"]`)) {
        return;
    }

    const badge = document.createElement('span');
    badge.className = `inline-flex items-center px-2 py-1 rounded-full text-xs font-medium badge badge-entity-${entityType}`;

    // Entity type emoji
    const emoji = {
        'company': '🏢',
        'contact': '👤',
        'stakeholder': '👤',
        'opportunity': '💼',
        'task': '📋'
    }[entityType] || '📄';

    badge.innerHTML = `
        <span class="mr-1">${emoji}</span>
        ${entityName}
        <button type="button" onclick="removeEntityBadge('${fieldId}', '${entityId}', '${entityType}')"
                class="ml-1 text-current hover:text-red-600">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
        </button>
    `;
    badge.dataset.entityId = entityId;
    badge.dataset.entityType = entityType;
    badgesDiv.appendChild(badge);
};

window.removeEntityBadge = function(fieldId, entityId, entityType) {
    const dataField = document.getElementById(fieldId + '-data');
    const badgesDiv = document.getElementById(fieldId + '-badges');

    if (!dataField || !badgesDiv) return;

    // Parse and filter entities
    let entities = [];
    try {
        entities = JSON.parse(dataField.value || '[]');
    } catch (e) {
        entities = [];
    }

    entities = entities.filter(e => !(e.id == entityId && e.type === entityType));
    dataField.value = JSON.stringify(entities);

    // Remove badge from display
    const badge = badgesDiv.querySelector(`[data-entity-id="${entityId}"][data-entity-type="${entityType}"]`);
    if (badge) badge.remove();
};

// Initialize any existing entity data on page load
document.addEventListener('DOMContentLoaded', function() {
    const searchContainers = document.querySelectorAll('.search-container[data-field-id]');
    searchContainers.forEach(container => {
        const fieldId = container.dataset.fieldId;
        const dataField = document.getElementById(fieldId + '-data');
        const badgesDiv = document.getElementById(fieldId + '-badges');

        if (dataField && badgesDiv && dataField.value && dataField.value !== '[]') {
            try {
                const entities = JSON.parse(dataField.value);
                entities.forEach(entity => {
                    createEntityBadge(fieldId, entity.id, entity.name, entity.type);
                });
            } catch (e) {
                console.error('Error loading entity badges:', e);
            }
        }
    });
});

// Function is available globally via window object