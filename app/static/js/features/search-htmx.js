/**
 * Simple HTMX Search Handler
 * Replaces the complex 653-line search.js with minimal functionality
 * HTMX handles the search logic, this just manages UI interactions
 */

// Helper function to position dropdown for modal contexts
function positionDropdownForModal(dropdown, inputElement) {
    const inModal = inputElement.closest('.modal');
    if (inModal) {
        // Use fixed positioning to escape modal overflow constraints
        const rect = inputElement.getBoundingClientRect();
        dropdown.style.position = 'fixed';
        dropdown.style.left = rect.left + 'px';
        dropdown.style.top = (rect.bottom + 2) + 'px';
        // Set minimum width to 350px or input width, whichever is larger
        dropdown.style.width = Math.max(350, rect.width) + 'px';
        dropdown.style.zIndex = '100001';
        return true;
    }
    return false;
}

// Helper function to hide and clear dropdown
function hideDropdown(dropdown) {
    if (dropdown) {
        dropdown.style.display = 'none';
        setTimeout(() => {
            dropdown.innerHTML = '';
        }, 100);
    }
}

// Helper function to find and hide dropdowns with entity selects
function hideEntityDropdowns(parentElement) {
    if (parentElement) {
        const divs = parentElement.querySelectorAll('div');
        divs.forEach(div => {
            if (div.querySelector('[data-entity-select]')) {
                hideDropdown(div);
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('global-search');
    const searchResults = document.getElementById('global-search-results');

    if (!searchInput || !searchResults) return;

    // Show results when HTMX content loads
    document.addEventListener('htmx:afterSwap', function(event) {
        if (event.target === searchResults) {
            // Always show results after swap if there's content
            if (searchResults.children.length > 0) {
                searchResults.classList.remove('hidden');
            }
        }
    });

    // Hide results when input is cleared
    searchInput.addEventListener('input', function() {
        if (!this.value.trim()) {
            searchResults.classList.add('hidden');
        }
    });

    // Hide results when clicking outside
    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target) &&
            !searchResults.contains(event.target)) {
            searchResults.classList.add('hidden');
        }
    });

    // Show results when focusing input (HTMX will populate with help text)
    searchInput.addEventListener('focus', function() {
        // HTMX focus trigger will fetch content, then afterSwap will show it
        // No need to check children.length since HTMX handles the content
    });

    // Hide results on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && !searchResults.classList.contains('hidden')) {
            searchResults.classList.add('hidden');
            searchInput.blur();
        }
    });

    // Handle search result clicks
    searchResults.addEventListener('click', function(event) {
        const resultLink = event.target.closest('a[data-search-result]');
        if (resultLink) {
            // Let the link work normally, just hide the dropdown
            searchResults.classList.add('hidden');
        }
    });
});

/**
 * Handle entity selection for form fields (single selection)
 * Used by company, stakeholder, and other entity reference fields
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize entity search inputs
    function initializeEntitySearchInputs() {
        const entitySearchInputs = document.querySelectorAll('[id$="_search"].form-input');

        entitySearchInputs.forEach(input => {
            if (input.dataset.entitySearchInitialized) return;
            input.dataset.entitySearchInitialized = 'true';

            const fieldName = input.id.replace('_search', '');
            const resultsDiv = document.getElementById(fieldName + '_results');

            if (!resultsDiv) return;

            // Show results when HTMX loads content
            document.addEventListener('htmx:afterSwap', function(event) {
                if (event.target.id === fieldName + '_results') {
                    if (resultsDiv.children.length > 0) {
                        // Check if we're in a modal
                        const inModal = input.closest('.modal');
                        if (inModal) {
                            // Use fixed positioning to escape modal overflow
                            const rect = input.getBoundingClientRect();
                            resultsDiv.style.position = 'fixed';
                            resultsDiv.style.left = rect.left + 'px';
                            resultsDiv.style.top = (rect.bottom + 2) + 'px';
                            // Set minimum width to 350px or input width, whichever is larger
                            resultsDiv.style.width = Math.max(350, rect.width) + 'px';
                            resultsDiv.style.zIndex = '100001';
                        }
                        resultsDiv.style.display = 'block';
                    }
                }
            });

            // Hide results when input is cleared
            input.addEventListener('input', function() {
                if (!this.value.trim()) {
                    resultsDiv.style.display = 'none';
                    resultsDiv.innerHTML = '';
                }
            });

            // Show results when focusing input if there's content
            input.addEventListener('focus', function() {
                if (resultsDiv.children.length > 0 && this.value.trim()) {
                    // Check if we're in a modal
                    const inModal = input.closest('.modal');
                    if (inModal) {
                        // Use fixed positioning to escape modal overflow
                        const rect = input.getBoundingClientRect();
                        resultsDiv.style.position = 'fixed';
                        resultsDiv.style.left = rect.left + 'px';
                        resultsDiv.style.top = (rect.bottom + 2) + 'px';
                        // Set minimum width to 350px or input width, whichever is larger
                        resultsDiv.style.width = Math.max(350, rect.width) + 'px';
                        resultsDiv.style.zIndex = '100001';
                    }
                    resultsDiv.style.display = 'block';
                }
            });
        });
    }

    // Initialize on page load and after HTMX swaps
    initializeEntitySearchInputs();
    document.addEventListener('htmx:afterSwap', function(event) {
        if (event.target.classList.contains('modal') || event.target.id === 'modal-container') {
            initializeEntitySearchInputs();
        }
    });

    // Handle clicks on entity select results
    document.addEventListener('click', function(event) {
        const selectLink = event.target.closest('a[data-entity-select]');
        if (!selectLink) return;

        event.preventDefault();
        event.stopPropagation();

        const fieldName = selectLink.dataset.entitySelect;
        const entityId = selectLink.dataset.entityId;
        const entityTitle = selectLink.dataset.entityTitle;
        const entityType = selectLink.dataset.entityType;

        // Find the search input, hidden field, results div, and selected display
        const searchInput = document.getElementById(fieldName + '_search');
        const hiddenField = document.getElementById(fieldName);
        const resultsDiv = document.getElementById(fieldName + '_results');
        const selectedDiv = document.getElementById(fieldName + '_selected');

        if (hiddenField) {
            // Set the hidden field value to the entity ID
            hiddenField.value = entityId;
        }

        if (searchInput) {
            // Show the entity title in the search field
            searchInput.value = entityTitle;
        }

        if (selectedDiv) {
            // Show selected entity info below the field
            selectedDiv.innerHTML = `Selected: ${entityTitle}`;
            selectedDiv.classList.remove('hidden');
        }

        if (resultsDiv) {
            // Hide the results dropdown and clear its contents
            resultsDiv.style.display = 'none';
            setTimeout(() => {
                resultsDiv.innerHTML = '';
            }, 100);
        } else {
            // Fallback: find and hide the div containing the results
            const parent = searchInput?.parentElement;
            if (parent) {
                const divs = parent.querySelectorAll('div');
                divs.forEach(div => {
                    if (div.querySelector('[data-entity-select]')) {
                        div.style.display = 'none';
                        setTimeout(() => {
                            div.innerHTML = '';
                        }, 100);
                    }
                });
            }
        }

        // Handle Company-Opportunity linking logic for Task forms
        handleCompanyOpportunityLinking(fieldName, entityId, entityTitle, entityType);
    });

    // Clear selection when search input is cleared
    document.addEventListener('input', function(event) {
        if (event.target.matches('[id$="_search"]')) {
            const fieldName = event.target.id.replace('_search', '');
            const hiddenField = document.getElementById(fieldName);
            const selectedDiv = document.getElementById(fieldName + '_selected');
            const resultsDiv = document.getElementById(fieldName + '_results');

            // If input is cleared, clear the selection
            if (!event.target.value.trim()) {
                if (hiddenField) hiddenField.value = '';
                if (selectedDiv) selectedDiv.innerHTML = '';
                if (resultsDiv) {
                    resultsDiv.style.display = 'none';
                    resultsDiv.innerHTML = '';
                }
            }
        }
    });

    // Hide dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        // Close entity search dropdowns when clicking outside
        document.querySelectorAll('[id$="_results"]').forEach(resultsDiv => {
            if (resultsDiv.style.display !== 'none') {
                const fieldName = resultsDiv.id.replace('_results', '');
                const searchInput = document.getElementById(fieldName + '_search');

                if (searchInput && !searchInput.contains(event.target) && !resultsDiv.contains(event.target)) {
                    resultsDiv.style.display = 'none';
                }
            }
        });
    });

    // Hide dropdowns on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('[id$="_results"]').forEach(resultsDiv => {
                if (resultsDiv.style.display !== 'none') {
                    resultsDiv.style.display = 'none';
                    const fieldName = resultsDiv.id.replace('_results', '');
                    const searchInput = document.getElementById(fieldName + '_search');
                    if (searchInput) searchInput.blur();
                }
            });
        }
    });
});

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