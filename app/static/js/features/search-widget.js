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

// Helper functions for robust visibility control
function showElement(element) {
    element.classList.remove('hidden');
    element.style.display = '';
}

function hideElement(element) {
    element.classList.add('hidden');
    element.style.display = 'none';
}

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
                showElement(resultsDiv);
            }
        });

        // Hide results when input is cleared
        input.addEventListener('input', function() {
            if (!this.value.trim()) {
                hideElement(resultsDiv);
            }
        });

        // Show results when focusing input if there's content
        input.addEventListener('focus', function() {
            if (resultsDiv.children.length > 0) {
                showElement(resultsDiv);
            }
        });
    });

    // Handle click outside to close dropdowns (but not for multi-select)
    document.addEventListener('click', function(event) {
        // Don't close if clicking on a search result
        if (event.target.closest('[data-search-result]')) {
            return;
        }

        // Close all search dropdowns when clicking outside
        document.querySelectorAll('.search-results').forEach(resultsDiv => {
            const container = resultsDiv.closest('.search-container');

            // Check if click is outside the search container
            if (container && !container.contains(event.target)) {
                hideElement(resultsDiv);
            }
        });
    });

    // Handle escape key to close dropdowns
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('.search-results:not(.hidden)').forEach(resultsDiv => {
                hideElement(resultsDiv);
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
    const searchField = document.getElementById(fieldId + '_search');
    const multipleDataField = document.getElementById(fieldId + '-data');  // Note: -data suffix for multi-select
    const singleDataField = document.getElementById(fieldId);  // No suffix for single-select
    const badgesDiv = document.getElementById(fieldId + '-badges');
    const selectedDiv = document.getElementById(fieldId + '_selected');
    const resultsDiv = document.getElementById(fieldId + '_results');

    // Determine if this is multiple or single selection mode
    const isMultipleSelection = multipleDataField !== null && badgesDiv !== null;

    if (isMultipleSelection) {
        // Multiple selection mode (used for entity multi-select if any)
        // Parse existing data
        let entities = [];
        try {
            entities = JSON.parse(multipleDataField.value || '[]');
        } catch (e) {
            entities = [];
        }

        // Check if already selected
        if (entities.some(e => e.id == entityId && e.type === entityType)) {
            return; // Already selected, don't add again
        }

        // Add new entity
        entities.push({
            id: entityId,
            name: entityName,
            type: entityType
        });

        // Update hidden field
        multipleDataField.value = JSON.stringify(entities);

        // Create badge
        createEntityBadge(fieldId, entityId, entityName, entityType);

        // Clear search but keep dropdown open for more selections
        if (searchField) {
            searchField.value = '';
            // Trigger input event to clear results but don't hide dropdown
            searchField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        // Note: Don't hide results for multi-select - user might want to select more

    } else if (singleDataField) {
        // Single selection mode (company, stakeholder, etc.)
        // Set the hidden field value to the entity ID
        singleDataField.value = entityId;

        // Show the entity title in the search field
        if (searchField) {
            searchField.value = entityName;
        }

        // Show selected entity info below the field
        if (selectedDiv) {
            selectedDiv.innerHTML = `Selected: ${entityName}`;
            selectedDiv.classList.remove('hidden');
        }

        // Hide the results dropdown for single select
        if (resultsDiv) {
            hideElement(resultsDiv);
        }
    }
};

// Make selectChoice globally available for choice search results
window.selectChoice = function(fieldName, choiceKey, choiceLabel) {
    const searchField = document.getElementById(fieldName + '_search');
    const multipleDataField = document.getElementById(fieldName + '-data');  // Multi-select choice field
    const singleHiddenField = document.getElementById(fieldName);  // Single-select choice field
    const badgesDiv = document.getElementById(fieldName + '-badges');
    const selectedDiv = document.getElementById(fieldName + '_selected');
    const resultsDiv = document.getElementById(fieldName + '_results');

    // Determine if this is multiple or single selection mode
    const isMultipleSelection = multipleDataField !== null && badgesDiv !== null;

    if (isMultipleSelection) {
        // Multiple selection mode (MEDDPICC roles, etc.)
        // Parse existing data
        let choices = [];
        try {
            choices = JSON.parse(multipleDataField.value || '[]');
        } catch (e) {
            choices = [];
        }

        // Check if already selected
        if (choices.some(c => c.id === choiceKey)) {
            return; // Already selected, don't add again
        }

        // Add new choice
        choices.push({
            id: choiceKey,
            name: choiceLabel,
            type: 'choice'
        });

        // Update hidden field
        multipleDataField.value = JSON.stringify(choices);

        // Create badge for choice
        createChoiceBadge(fieldName, choiceKey, choiceLabel);

        // Clear search but keep dropdown open for more selections
        if (searchField) {
            searchField.value = '';
            // Trigger input event to refresh results
            searchField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        // Note: Don't hide results for multi-select - user might want to select more

    } else if (singleHiddenField) {
        // Single selection mode
        // Set the hidden field value
        singleHiddenField.value = choiceKey;

        // Update the selected display
        if (selectedDiv) {
            selectedDiv.innerHTML = `
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    ${choiceLabel}
                </span>
            `;
            selectedDiv.classList.remove('hidden');
        }

        // Clear search and hide results for single select
        if (searchField) {
            searchField.value = '';
            // Trigger input event to ensure HTMX clears results
            searchField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        if (resultsDiv) {
            hideElement(resultsDiv);
        }
    }
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

window.createChoiceBadge = function(fieldName, choiceKey, choiceLabel) {
    const badgesDiv = document.getElementById(fieldName + '-badges');
    if (!badgesDiv) return;

    // Check if badge already exists
    if (badgesDiv.querySelector(`[data-choice-key="${choiceKey}"]`)) {
        return;
    }

    const badge = document.createElement('span');
    badge.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800';

    badge.innerHTML = `
        <span class="mr-1">📄</span>
        ${choiceLabel}
        <button type="button" onclick="removeChoiceBadge('${fieldName}', '${choiceKey}')"
                class="ml-1 text-current hover:text-red-600">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
        </button>
    `;
    badge.dataset.choiceKey = choiceKey;
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

window.removeChoiceBadge = function(fieldName, choiceKey) {
    const dataField = document.getElementById(fieldName + '-data');
    const badgesDiv = document.getElementById(fieldName + '-badges');

    if (!dataField || !badgesDiv) return;

    // Parse and filter choices
    let choices = [];
    try {
        choices = JSON.parse(dataField.value || '[]');
    } catch (e) {
        choices = [];
    }

    choices = choices.filter(c => c.id !== choiceKey);
    dataField.value = JSON.stringify(choices);

    // Remove badge from display
    const badge = badgesDiv.querySelector(`[data-choice-key="${choiceKey}"]`);
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
                const items = JSON.parse(dataField.value);
                items.forEach(item => {
                    if (item.type === 'choice') {
                        createChoiceBadge(fieldId, item.id, item.name);
                    } else {
                        createEntityBadge(fieldId, item.id, item.name, item.type);
                    }
                });
            } catch (e) {
                console.error('Error loading badges:', e);
            }
        }
    });
});

// Function is available globally via window object