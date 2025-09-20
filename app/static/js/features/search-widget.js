/**
 * Unified Search Widget Handler
 *
 * Handles ALL search functionality - both global search and entity search widgets
 * DRY implementation that works with any search input using HTMX
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded - initializing search widgets');
    // Initialize ALL search inputs using unified approach
    initializeAllSearchInputs();

    // Re-initialize when new content is loaded via HTMX
    document.addEventListener('htmx:afterSwap', function(event) {
        console.log('htmx:afterSwap event on:', event.target.id || event.target.className);
        // If a modal was loaded, initialize any search widgets in it
        if (event.target.classList.contains('modal-overlay')) {
            console.log('Modal loaded, re-initializing search inputs');
            initializeAllSearchInputs();
        }
    });

    // Add input event listener to all search inputs to log when user types
    document.addEventListener('input', function(event) {
        if (event.target.classList.contains('search-input')) {
            console.log('User typed in search input:', event.target.id, 'Value:', event.target.value, 'Length:', event.target.value.length);
        }
    });

    // Log when HTMX makes a request
    document.addEventListener('htmx:beforeRequest', function(event) {
        if (event.target.classList.contains('search-input')) {
            console.log('HTMX request triggered from:', event.target.id, 'Value:', event.target.value);
        }
    });
});

// Helper functions for robust visibility control
function showElement(element) {
    console.log('showElement called for:', element.id);
    element.classList.remove('hidden');
    element.removeAttribute('hidden');  // Remove HTML hidden attribute
    element.style.display = '';
    element.style.visibility = 'visible';
    element.style.opacity = '1';
    console.log('After showElement - classList:', element.classList.toString(), 'display:', element.style.display, 'visibility:', element.style.visibility);
}

function hideElement(element) {
    console.log('hideElement called for:', element.id);
    element.classList.add('hidden');
    element.setAttribute('hidden', '');  // Add HTML hidden attribute
    element.style.display = 'none';
    console.log('After hideElement - classList:', element.classList.toString(), 'display:', element.style.display);
}

// Unified function that handles ALL search inputs using global search's working pattern
function initializeAllSearchInputs() {
    console.log('initializeAllSearchInputs called');

    // Find all search inputs with the .search-input class
    const searchInputs = document.querySelectorAll('.search-input');
    console.log('Found search inputs:', searchInputs.length);

    searchInputs.forEach(input => {
        console.log('Processing input:', input.id, 'Already initialized?', input.dataset.searchInitialized);

        // Skip if already initialized
        if (input.dataset.searchInitialized) return;

        const resultsId = input.getAttribute('hx-target');
        const resultsDiv = document.querySelector(resultsId);

        if (!resultsDiv) {
            console.log('No results div found for:', input.id);
            return;
        }

        // Mark as initialized
        input.dataset.searchInitialized = 'true';
        console.log('Initialized input:', input.id);
    });

    // Add HTMX listener ONCE at document level, not per input
    // This handles ALL search results containers
    document.addEventListener('htmx:afterSwap', function(event) {
        // Check if the swapped element is a search results container
        if (event.target.id && event.target.id.endsWith('-results')) {
            console.log('HTMX afterSwap for results container:', event.target.id);
            console.log('Results container children count:', event.target.children.length);
            console.log('Results container innerHTML length:', event.target.innerHTML.length);
            console.log('Results container classList BEFORE:', event.target.classList.toString());
            console.log('Results container hidden BEFORE?', event.target.classList.contains('hidden'));
            console.log('Results container style.display BEFORE:', event.target.style.display);

            if (event.target.children.length > 0) {
                console.log('Removing hidden class from results');
                event.target.classList.remove('hidden');
                event.target.removeAttribute('hidden');
                event.target.style.display = '';
                event.target.style.visibility = 'visible';
                event.target.style.opacity = '1';
            } else {
                console.log('Adding hidden class to results (no children)');
                event.target.classList.add('hidden');
            }

            console.log('Results container classList AFTER:', event.target.classList.toString());
            console.log('Results container hidden AFTER?', event.target.classList.contains('hidden'));
            console.log('Results container style.display AFTER:', event.target.style.display);

            // Force check after a short delay to see if something else is hiding it
            setTimeout(() => {
                console.log('DELAYED CHECK (100ms) - hidden?', event.target.classList.contains('hidden'));
                console.log('DELAYED CHECK (100ms) - display:', event.target.style.display);
                console.log('DELAYED CHECK (100ms) - classList:', event.target.classList.toString());
            }, 100);
        }
    });

    // Handle clicks outside to close all dropdowns
    document.addEventListener('click', function(event) {
        // Close all search results that end with -results
        document.querySelectorAll('[id$="-results"]').forEach(resultsDiv => {
            const container = resultsDiv.parentElement;
            if (container && !container.contains(event.target)) {
                resultsDiv.classList.add('hidden');
            }
        });
    });

    // Handle escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('[id$="-results"]:not(.hidden)').forEach(resultsDiv => {
                resultsDiv.classList.add('hidden');
            });
        }
    });

    // Close search dropdowns when modals are opened
    document.addEventListener('htmx:afterSwap', function(event) {
        // If content was swapped into modal-container, close all search dropdowns
        if (event.target.id === 'modal-container') {
            document.querySelectorAll('[id$="-results"]:not(.hidden)').forEach(resultsDiv => {
                resultsDiv.classList.add('hidden');
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
    const resultsDiv = document.getElementById(fieldId + '_search-results');

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

        // Update selected field for HTMX
        const selectedField = document.getElementById(fieldId + '-selected');
        if (selectedField) {
            selectedField.value = entities.map(e => e.id).join(',');
        }

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
            // Manually trigger HTMX to recognize the change
            htmx.trigger(searchField, 'input');
        }

        // Hide the results dropdown for single select
        if (resultsDiv) {
            hideElement(resultsDiv);
        }
    }
};

// Make selectChoice globally available for choice search results
window.selectChoice = function(fieldName, choiceKey, choiceLabel) {
    console.log('selectChoice called with:', { fieldName, choiceKey, choiceLabel });

    const searchField = document.getElementById(fieldName + '_search');
    const multipleDataField = document.getElementById(fieldName + '-data');  // Multi-select choice field
    const singleHiddenField = document.getElementById(fieldName);  // Single-select choice field
    const badgesDiv = document.getElementById(fieldName + '-badges');
    const resultsDiv = document.getElementById(fieldName + '_search-results');

    console.log('Elements found:', {
        searchField: searchField ? 'YES' : 'NO',
        multipleDataField: multipleDataField ? 'YES' : 'NO',
        singleHiddenField: singleHiddenField ? 'YES' : 'NO',
        badgesDiv: badgesDiv ? 'YES' : 'NO',
        resultsDiv: resultsDiv ? 'YES' : 'NO'
    });

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

        // Update selected field for HTMX
        const selectedField = document.getElementById(fieldName + '-selected');
        if (selectedField) {
            selectedField.value = choices.map(c => c.id).join(',');
        }

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
        console.log('Single selection mode');
        // Single selection mode
        // Set the hidden field value
        singleHiddenField.value = choiceKey;
        console.log('Set hidden field value to:', choiceKey);

        // Show the choice label in the search field
        if (searchField) {
            console.log('Setting search field value to:', choiceLabel);
            searchField.value = choiceLabel;
            console.log('Search field value is now:', searchField.value);

            // Manually trigger HTMX to recognize the change
            console.log('About to trigger HTMX input event');
            htmx.trigger(searchField, 'input');
            console.log('HTMX input event triggered');

            // Log HTMX attributes on the search field
            console.log('Search field HTMX attributes:', {
                'hx-get': searchField.getAttribute('hx-get'),
                'hx-trigger': searchField.getAttribute('hx-trigger'),
                'hx-target': searchField.getAttribute('hx-target'),
                'data-search-initialized': searchField.getAttribute('data-search-initialized')
            });
        }

        // Hide results for single select
        if (resultsDiv) {
            console.log('Hiding results div:', resultsDiv.id);
            console.log('Results div classList before hide:', resultsDiv.classList.toString());
            hideElement(resultsDiv);
            console.log('Results div classList after hide:', resultsDiv.classList.toString());
            console.log('Results div style.display:', resultsDiv.style.display);
        }
    }
    console.log('selectChoice completed');
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
    const searchField = document.getElementById(fieldId + '_search');

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

    // Update selected field for HTMX
    const selectedField = document.getElementById(fieldId + '-selected');
    if (selectedField) {
        selectedField.value = entities.map(e => e.id).join(',');
    }

    // Remove badge from display
    const badge = badgesDiv.querySelector(`[data-entity-id="${entityId}"][data-entity-type="${entityType}"]`);
    if (badge) badge.remove();

    // Trigger search refresh if search field is focused or has value
    if (searchField && (document.activeElement === searchField || searchField.value)) {
        // Trigger HTMX to refresh the results
        htmx.trigger(searchField, 'input');
    }
};

window.removeChoiceBadge = function(fieldName, choiceKey) {
    const dataField = document.getElementById(fieldName + '-data');
    const badgesDiv = document.getElementById(fieldName + '-badges');
    const searchField = document.getElementById(fieldName + '_search');

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

    // Update selected field for HTMX
    const selectedField = document.getElementById(fieldName + '-selected');
    if (selectedField) {
        selectedField.value = choices.map(c => c.id).join(',');
    }

    // Remove badge from display
    const badge = badgesDiv.querySelector(`[data-choice-key="${choiceKey}"]`);
    if (badge) badge.remove();

    // Trigger search refresh if search field is focused or has value
    if (searchField && (document.activeElement === searchField || searchField.value)) {
        // Trigger HTMX to refresh the results
        htmx.trigger(searchField, 'input');
    }
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

// Global Search Handler (consolidated from search-htmx.js)
// Old initializeGlobalSearch() function deleted - now handled by unified initializeAllSearchInputs()

// Function is available globally via window object