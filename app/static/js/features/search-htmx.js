/**
 * Simple HTMX Search Handler
 * Replaces the complex 653-line search.js with minimal functionality
 * HTMX handles the search logic, this just manages UI interactions
 */

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
    // Handle clicks on entity select results
    document.addEventListener('click', function(event) {
        const selectLink = event.target.closest('a[data-entity-select]');
        if (!selectLink) return;

        event.preventDefault();

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
            // Hide the results dropdown
            resultsDiv.classList.add('hidden');
        }
    });

    // Clear selection when search input is cleared
    document.addEventListener('input', function(event) {
        if (event.target.matches('[id$="_search"]')) {
            const fieldName = event.target.id.replace('_search', '');
            const hiddenField = document.getElementById(fieldName);
            const selectedDiv = document.getElementById(fieldName + '_selected');

            // If input is cleared, clear the selection
            if (!event.target.value.trim()) {
                if (hiddenField) hiddenField.value = '';
                if (selectedDiv) selectedDiv.innerHTML = '';
            }
        }
    });
});