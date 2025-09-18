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
        if (event.target.id === 'modal-container' || event.target.classList.contains('modal')) {
            initializeSearchWidgets();
        }
    });
});

// Helper functions for robust visibility control
function showElement(element) {
    element.classList.remove('hidden');
    element.removeAttribute('hidden');  // Remove HTML hidden attribute
    element.style.display = '';
}

function hideElement(element) {
    element.classList.add('hidden');
    element.setAttribute('hidden', '');  // Add HTML hidden attribute
    element.style.display = 'none';
}

// Position dropdown using fixed positioning to escape stacking contexts
function positionDropdown(inputElement, dropdownElement) {
    const rect = inputElement.getBoundingClientRect();

    // Set fixed positioning
    dropdownElement.style.position = 'fixed';
    dropdownElement.style.top = (rect.bottom + 2) + 'px';  // 2px gap below input
    dropdownElement.style.left = rect.left + 'px';
    dropdownElement.style.width = rect.width + 'px';
    dropdownElement.style.maxHeight = '240px';  // Same as max-h-60 in Tailwind
    dropdownElement.style.overflowY = 'auto';
    dropdownElement.style.zIndex = '99999';  // Ensure it's above everything
}

// Hide all other dropdowns except the specified one
function hideOtherDropdowns(exceptDropdown) {
    document.querySelectorAll('.search-results').forEach(dropdown => {
        if (dropdown !== exceptDropdown) {
            hideElement(dropdown);
        }
    });
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


        // Add event to include selected items in HTMX request
        input.addEventListener('htmx:configRequest', function(event) {
            // Get the field name from the search input ID (remove '_search' suffix)
            const fieldId = this.id.replace('_search', '');

            // Check for multi-select data field
            const dataField = document.getElementById(fieldId + '-data');
            const selectedField = document.getElementById(fieldId + '-selected');

            if (dataField && dataField.value) {
                try {
                    const selectedItems = JSON.parse(dataField.value);
                    // Add selected item IDs to the request
                    if (selectedItems.length > 0) {
                        const selectedIds = selectedItems.map(item => item.id).join(',');
                        event.detail.parameters.selected = selectedIds;
                        // Also update the hidden field for HTMX to pick up
                        if (selectedField) {
                            selectedField.value = selectedIds;
                        }
                    }
                } catch (e) {
                    // If not JSON, might be single-select, ignore
                }
            }

            // Include entity type if available (for dropdown searches)
            if (this.dataset.entityType) {
                event.detail.parameters.entity_type = this.dataset.entityType;
            }
        });

        // Show results when HTMX loads content
        input.addEventListener('htmx:afterSwap', function() {
            // Always show results if there's content
            if (resultsDiv.children.length > 0) {
                hideOtherDropdowns(resultsDiv);  // Hide all other dropdowns first
                positionDropdown(this, resultsDiv);
                showElement(resultsDiv);
            }
        });

        // Also listen for HTMX afterSettle to ensure dropdown shows
        input.addEventListener('htmx:afterSettle', function() {
            // Always show results if there's content
            if (resultsDiv.children.length > 0) {
                hideOtherDropdowns(resultsDiv);  // Hide all other dropdowns first
                positionDropdown(this, resultsDiv);
                showElement(resultsDiv);
            }
        });

        // Listen for HTMX beforeRequest to track that we're loading
        input.addEventListener('htmx:beforeRequest', function() {
            // Mark that we're expecting results
            this.dataset.loadingResults = 'true';
        });

        // After content loads, check if we should show
        input.addEventListener('htmx:afterOnLoad', function() {
            // If we were loading and got content, show it
            if (this.dataset.loadingResults === 'true' && resultsDiv.children.length > 0) {
                hideOtherDropdowns(resultsDiv);  // Hide all other dropdowns first
                positionDropdown(this, resultsDiv);
                showElement(resultsDiv);
                this.dataset.loadingResults = 'false';
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
                hideOtherDropdowns(resultsDiv);  // Hide all other dropdowns first
                positionDropdown(this, resultsDiv);
                showElement(resultsDiv);
            }
            // HTMX will trigger on focus and load content
        });
    });

    // Handle click outside to close dropdowns (but not for multi-select)
    document.addEventListener('click', function(event) {
        // Don't close if clicking on a search result
        if (event.target.closest('[data-search-result]')) {
            return;
        }

        // Close all search dropdowns when clicking outside
        // Find all results divs by looking for the hx-target attribute pattern
        document.querySelectorAll('[id$="_results"]').forEach(resultsDiv => {
            // Get the parent relative container
            const container = resultsDiv.parentElement;

            // Check if click is outside the container
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

    // Reposition dropdowns on scroll/resize
    let repositionTimeout;
    function handleRepositioning() {
        clearTimeout(repositionTimeout);
        repositionTimeout = setTimeout(() => {
            document.querySelectorAll('.search-results:not(.hidden)').forEach(resultsDiv => {
                const inputId = resultsDiv.id.replace('_results', '_search');
                const input = document.getElementById(inputId);
                if (input) {
                    positionDropdown(input, resultsDiv);
                }
            });
        }, 10);
    }

    window.addEventListener('scroll', handleRepositioning, true);
    window.addEventListener('resize', handleRepositioning);
}

// Universal selection function for ALL dropdowns (entities, choices, etc.)
window.selectItem = function(fieldName, itemId, itemLabel) {
    // Get the search input field
    const searchField = document.getElementById(fieldName + '_search');
    // Get the hidden value field
    const hiddenField = document.getElementById(fieldName);
    // Get the results dropdown
    const resultsDiv = document.getElementById(fieldName + '_results');

    // Set the value
    if (hiddenField) {
        hiddenField.value = itemId;
    }

    // Show the label to the user
    if (searchField) {
        searchField.value = itemLabel;
    }

    // Hide the dropdown
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
};

// Unified badge creation function
window.createBadge = function(fieldId, itemId, itemLabel, itemType) {
    const badgesDiv = document.getElementById(fieldId + '-badges');
    if (!badgesDiv) return;

    // Check if badge already exists
    const existingBadge = badgesDiv.querySelector(`[data-item-id="${itemId}"][data-item-type="${itemType}"]`);
    if (existingBadge) return;

    const badge = document.createElement('span');

    // Determine badge styling based on type
    const isChoice = itemType === 'choice' || itemType.startsWith('choice:');
    if (isChoice) {
        badge.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800';
    } else {
        badge.className = `inline-flex items-center px-2 py-1 rounded-full text-xs font-medium badge badge-entity-${itemType}`;
    }

    // Determine emoji based on type
    const emoji = isChoice ? '📄' : {
        'company': '🏢',
        'contact': '👤',
        'stakeholder': '👤',
        'opportunity': '💼',
        'task': '📋'
    }[itemType] || '📄';

    badge.innerHTML = `
        <span class="mr-1">${emoji}</span>
        ${itemLabel}
        <button type="button" onclick="removeBadge('${fieldId}', '${itemId}', '${itemType}')"
                class="ml-1 text-current hover:text-red-600">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
        </button>
    `;
    badge.dataset.itemId = itemId;
    badge.dataset.itemType = itemType;
    badgesDiv.appendChild(badge);
};

// Unified badge removal function
window.removeBadge = function(fieldId, itemId, itemType) {
    const dataField = document.getElementById(fieldId + '-data');
    const badgesDiv = document.getElementById(fieldId + '-badges');
    const searchField = document.getElementById(fieldId + '_search');

    if (!dataField || !badgesDiv) return;

    // Parse and filter items
    let items = [];
    try {
        items = JSON.parse(dataField.value || '[]');
    } catch (e) {
        items = [];
    }

    items = items.filter(item => !(item.id == itemId && (item.type === itemType || itemType === 'choice')));
    dataField.value = JSON.stringify(items);

    // Update selected field for HTMX
    const selectedField = document.getElementById(fieldId + '-selected');
    if (selectedField) {
        selectedField.value = items.map(item => item.id).join(',');
    }

    // Remove badge from display
    const badge = badgesDiv.querySelector(`[data-item-id="${itemId}"][data-item-type="${itemType}"]`);
    if (badge) badge.remove();

    // Trigger search refresh if search field is focused or has value
    if (searchField && (document.activeElement === searchField || searchField.value)) {
        htmx.trigger(searchField, 'input');
    }
};

// Legacy function names for backwards compatibility
window.selectEntity = window.selectItem;
window.selectChoice = window.selectItem;
window.createEntityBadge = function(fieldId, entityId, entityName, entityType) {
    return window.createBadge(fieldId, entityId, entityName, entityType);
};
window.createChoiceBadge = function(fieldName, choiceKey, choiceLabel) {
    return window.createBadge(fieldName, choiceKey, choiceLabel, 'choice');
};
window.removeEntityBadge = function(fieldId, entityId, entityType) {
    return window.removeBadge(fieldId, entityId, entityType);
};
window.removeChoiceBadge = function(fieldName, choiceKey) {
    return window.removeBadge(fieldName, choiceKey, 'choice');
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
                    // Use unified createBadge function
                    createBadge(fieldId, item.id, item.name, item.type || 'choice');
                });
            } catch (e) {
                console.error('Error loading badges:', e);
            }
        }
    });
});

// Function is available globally via window object

/**
 * Handle Company-Opportunity linking logic for Task forms
 */
function handleCompanyOpportunityLinking(fieldName, entityId, entityTitle, entityType) {
    // Only handle linking logic for company_id and opportunity_id fields
    if (fieldName !== 'company_id' && fieldName !== 'opportunity_id') return;

    const companySearchInput = document.getElementById('company_id_search');
    const companyHiddenField = document.getElementById('company_id');
    const companySelectedDiv = document.getElementById('company_id_selected');

    const opportunitySearchInput = document.getElementById('opportunity_id_search');
    const opportunityHiddenField = document.getElementById('opportunity_id');
    const opportunitySelectedDiv = document.getElementById('opportunity_id_selected');

    // If a company was selected, update opportunity search to filter by this company
    if (fieldName === 'company_id' && entityType === 'company') {
        if (opportunitySearchInput) {
            // Clear current opportunity selection
            if (opportunityHiddenField) opportunityHiddenField.value = '';
            if (opportunitySearchInput) opportunitySearchInput.value = '';
            if (opportunitySelectedDiv) opportunitySelectedDiv.innerHTML = '';

            // Update the opportunity search to include company filter
            const currentHxVals = opportunitySearchInput.getAttribute('hx-vals');
            let hxValsObj;
            try {
                hxValsObj = JSON.parse(currentHxVals);
            } catch (e) {
                hxValsObj = {};
            }

            // Add company filter to opportunity search
            hxValsObj.company_id = entityId;
            opportunitySearchInput.setAttribute('hx-vals', JSON.stringify(hxValsObj));
        }
    }

    // If an opportunity was selected, auto-populate the company field
    if (fieldName === 'opportunity_id' && entityType === 'opportunity') {
        // Fetch the opportunity details to get the company info
        fetch(`/api/opportunities/${entityId}`)
            .then(response => response.json())
            .then(data => {
                if (data.company && data.company.id) {
                    // Auto-populate company field
                    if (companyHiddenField) companyHiddenField.value = data.company.id;
                    if (companySearchInput) companySearchInput.value = data.company.name;
                    if (companySelectedDiv) {
                        companySelectedDiv.innerHTML = `Selected: ${data.company.name}`;
                        companySelectedDiv.classList.remove('hidden');
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching opportunity details:', error);
            });
    }
}