/**
 * Simple HTMX Search Handler
 * Replaces the complex 653-line search.js with minimal functionality
 * HTMX handles the search logic, this just manages UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('global-search');
    const searchResults = document.getElementById('search-results');

    if (!searchInput || !searchResults) return;

    // Show results when HTMX content loads
    document.addEventListener('htmx:afterSwap', function(event) {
        if (event.target === searchResults && searchInput.value.trim()) {
            searchResults.classList.remove('hidden');
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

    // Show results when focusing input (if there's content)
    searchInput.addEventListener('focus', function() {
        if (searchResults.children.length > 0 && this.value.trim()) {
            searchResults.classList.remove('hidden');
        }
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

// Export for module usage
export { };