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
                if (resultsDiv.children.length > 0 && this.value.trim()) {
                    resultsDiv.classList.remove('hidden');
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
            resultsDiv.classList.add('hidden');
            setTimeout(() => {
                resultsDiv.innerHTML = '';
            }, 100);
        }
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
                    resultsDiv.classList.add('hidden');
                    resultsDiv.innerHTML = '';
                }
            }
        }
    });

    // Hide dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        // Close entity search dropdowns when clicking outside
        document.querySelectorAll('[id$="_results"]:not(.hidden)').forEach(resultsDiv => {
            const fieldName = resultsDiv.id.replace('_results', '');
            const searchInput = document.getElementById(fieldName + '_search');

            if (searchInput && !searchInput.contains(event.target) && !resultsDiv.contains(event.target)) {
                resultsDiv.classList.add('hidden');
            }
        });
    });

    // Hide dropdowns on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('[id$="_results"]:not(.hidden)').forEach(resultsDiv => {
                resultsDiv.classList.add('hidden');
                const fieldName = resultsDiv.id.replace('_results', '');
                const searchInput = document.getElementById(fieldName + '_search');
                if (searchInput) searchInput.blur();
            });
        }
    });
});