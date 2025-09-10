// Global search functionality

class SearchManager {
    constructor() {
        this.searchInput = document.querySelector('#global-search');
        this.searchResults = null;
        this.currentQuery = '';
        this.debounceTimer = null;
        
        if (this.searchInput) {
            this.init();
        }
    }
    
    init() {
        this.createResultsContainer();
        this.bindEvents();
    }
    
    createResultsContainer() {
        this.searchResults = document.createElement('div');
        this.searchResults.id = 'search-results';
        this.searchResults.className = 'absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-b-md shadow-lg z-50 max-h-96 overflow-y-auto hidden';
        
        // Position relative to search input
        const searchContainer = this.searchInput.parentElement;
        searchContainer.style.position = 'relative';
        searchContainer.appendChild(this.searchResults);
    }
    
    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('focus', (e) => this.handleFocus(e));
        this.searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.searchResults.contains(e.target)) {
                this.hideResults();
            }
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideResults();
                this.searchInput.blur();
            }
        });
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        // Always search, even with empty query (will show all results)
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        // Always perform search on focus, even with empty query
        this.performSearch(query);
    }
    
    handleKeydown(e) {
        if (!this.searchResults.classList.contains('hidden')) {
            const items = this.searchResults.querySelectorAll('[role="option"]');
            const current = this.searchResults.querySelector('[aria-selected="true"]');
            
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.selectNext(items, current);
                    break;
                    
                case 'ArrowUp':
                    e.preventDefault();
                    this.selectPrevious(items, current);
                    break;
                    
                case 'Enter':
                    e.preventDefault();
                    if (current) {
                        // Trigger the same modal event as clicking
                        const entityType = current.dataset.entityType;
                        const entityId = current.dataset.entityId;
                        
                        if (entityType && entityId) {
                            window.dispatchEvent(new CustomEvent(`open-detail-${entityType}-modal`, {
                                detail: { id: parseInt(entityId) }
                            }));
                            
                            this.hideResults();
                            this.searchInput.blur();
                        }
                    }
                    break;
            }
        }
    }
    
    selectNext(items, current) {
        if (!current) {
            this.selectItem(items[0]);
        } else {
            const currentIndex = Array.from(items).indexOf(current);
            const nextIndex = (currentIndex + 1) % items.length;
            this.selectItem(items[nextIndex]);
        }
    }
    
    selectPrevious(items, current) {
        if (!current) {
            this.selectItem(items[items.length - 1]);
        } else {
            const currentIndex = Array.from(items).indexOf(current);
            const prevIndex = (currentIndex - 1 + items.length) % items.length;
            this.selectItem(items[prevIndex]);
        }
    }
    
    selectItem(item) {
        // Clear previous selection
        this.searchResults.querySelectorAll('[aria-selected="true"]').forEach(el => {
            el.setAttribute('aria-selected', 'false');
            el.classList.remove('bg-blue-50');
        });
        
        // Select new item
        if (item) {
            item.setAttribute('aria-selected', 'true');
            item.classList.add('bg-blue-50');
            item.scrollIntoView({ block: 'nearest' });
        }
    }
    
    async performSearch(query) {
        this.currentQuery = query;
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=10`);
            if (!response.ok) throw new Error('Search failed');
            
            const results = await response.json();
            this.displayResults(results);
            
        } catch (error) {
            console.error('Search error:', error);
            this.displayError();
        }
    }
    
    displayResults(results) {
        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    No results found for "${this.currentQuery}"
                </div>
            `;
        } else {
            this.searchResults.innerHTML = this.renderBadgeResults(results);
            this.bindResultEvents();
        }
        
        this.showResults();
    }
    
    renderBadgeResults(results) {
        let html = '';
        
        results.forEach(result => {
            html += this.renderBadgeSearchItem(result);
        });
        
        return html;
    }
    
    renderBadgeSearchItem(result) {
        const getEntityTypeIcon = (type) => {
            switch(type) {
                case 'company': return '🏢';
                case 'contact': return '👤';
                case 'opportunity': return '💼';
                case 'task': return '✅';
                default: return '📄';
            }
        };
        
        const getEntityTypeBadgeClass = (type) => {
            switch(type) {
                case 'company': return 'bg-blue-100 text-blue-800';
                case 'contact': return 'bg-green-100 text-green-800';
                case 'opportunity': return 'bg-purple-100 text-purple-800';
                case 'task': return 'bg-orange-100 text-orange-800';
                default: return 'bg-gray-100 text-gray-800';
            }
        };
        
        return `
            <div role="option"
                 aria-selected="false"
                 data-entity-type="${result.type}"
                 data-entity-id="${result.id}"
                 class="block px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 cursor-pointer">
                <div class="flex items-center space-x-3">
                    <span class="text-lg">${getEntityTypeIcon(result.type)}</span>
                    <div class="flex-1 min-w-0">
                        <div class="text-label-primary truncate">
                            ${this.highlightQuery(result.title)}
                        </div>
                        <div class="text-xs-gray-500 truncate">
                            ${result.subtitle || ''}
                        </div>
                    </div>
                </div>
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getEntityTypeBadgeClass(result.type)}">
                    ${result.type}
                </span>
            </div>
        `;
    }
    
    highlightQuery(text) {
        if (!this.currentQuery) return text;
        
        const regex = new RegExp(`(${this.escapeRegex(this.currentQuery)})`, 'gi');
        return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
    }
    
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    displayError() {
        this.searchResults.innerHTML = `
            <div class="p-4 text-center text-red-500">
                Search failed. Please try again.
            </div>
        `;
        this.showResults();
    }
    
    bindResultEvents() {
        // Bind click events to search results
        this.searchResults.querySelectorAll('[data-entity-type]').forEach(item => {
            item.addEventListener('click', () => {
                const entityType = item.dataset.entityType;
                const entityId = item.dataset.entityId;
                
                // Dispatch modal open event
                window.dispatchEvent(new CustomEvent(`open-detail-${entityType}-modal`, {
                    detail: { id: parseInt(entityId) }
                }));
                
                // Hide search results
                this.hideResults();
                this.searchInput.blur();
            });
        });
    }
    
    showResults() {
        this.searchResults.classList.remove('hidden');
    }
    
    hideResults() {
        this.searchResults.classList.add('hidden');
        // Clear selection
        this.searchResults.querySelectorAll('[aria-selected="true"]').forEach(el => {
            el.setAttribute('aria-selected', 'false');
            el.classList.remove('bg-blue-50');
        });
    }
}

// Autocomplete for specific entity selects
class AutocompleteManager {
    constructor(inputElement, entityType) {
        this.input = inputElement;
        this.entityType = entityType;
        this.resultsContainer = null;
        this.debounceTimer = null;
        
        this.init();
    }
    
    init() {
        this.createResultsContainer();
        this.bindEvents();
    }
    
    createResultsContainer() {
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = 'absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-b-md shadow-lg z-50 max-h-48 overflow-y-auto hidden';
        
        const container = this.input.parentElement;
        container.style.position = 'relative';
        container.appendChild(this.resultsContainer);
    }
    
    bindEvents() {
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('focus', (e) => this.handleFocus(e));
        
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.resultsContainer.contains(e.target)) {
                this.hideResults();
            }
        });
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        // Always search, even with empty query
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300);
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        // Always fetch suggestions on focus, even with empty query
        this.fetchSuggestions(query);
    }
    
    async fetchSuggestions(query) {
        try {
            const response = await fetch(
                `/api/autocomplete?q=${encodeURIComponent(query)}&type=${this.entityType}&limit=8`
            );
            
            if (!response.ok) throw new Error('Autocomplete failed');
            
            const suggestions = await response.json();
            this.displaySuggestions(suggestions);
            
        } catch (error) {
            console.error('Autocomplete error:', error);
        }
    }
    
    displaySuggestions(suggestions) {
        if (suggestions.length === 0) {
            this.hideResults();
            return;
        }
        
        let html = '';
        suggestions.forEach(suggestion => {
            html += `
                <div class="px-3 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                     data-id="${suggestion.id}"
                     data-name="${suggestion.name}">
                    <div class="text-label-primary">
                        ${suggestion.name}
                    </div>
                    ${suggestion.company ? `<div class="text-xs-gray-500">${suggestion.company}</div>` : ''}
                </div>
            `;
        });
        
        this.resultsContainer.innerHTML = html;
        
        // Bind click events
        this.resultsContainer.querySelectorAll('[data-id]').forEach(item => {
            item.addEventListener('click', () => {
                this.selectSuggestion(item.dataset.id, item.dataset.name);
            });
        });
        
        this.showResults();
    }
    
    selectSuggestion(id, name) {
        this.input.value = name;
        this.input.dataset.selectedId = id;
        
        // Trigger change event
        this.input.dispatchEvent(new Event('change'));
        
        this.hideResults();
    }
    
    showResults() {
        this.resultsContainer.classList.remove('hidden');
    }
    
    hideResults() {
        this.resultsContainer.classList.add('hidden');
    }
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize global search
    new SearchManager();
    
    // Initialize autocomplete for entity selects
    document.querySelectorAll('[data-autocomplete]').forEach(input => {
        const entityType = input.dataset.autocomplete;
        new AutocompleteManager(input, entityType);
    });
});

// Export for global access
window.SearchManager = SearchManager;
window.AutocompleteManager = AutocompleteManager;