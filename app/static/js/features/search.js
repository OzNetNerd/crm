// Global search functionality

class SearchManager {
    constructor() {
        this.searchInput = document.querySelector('#global-search');
        this.searchResults = null;
        this.currentQuery = '';
        this.debounceTimer = null;
        this.selectedEntityTypes = ['all']; // Default to all entity types
        this.entityTypes = {}; // Will be populated from backend
        
        if (this.searchInput) {
            this.init();
        }
    }
    
    init() {
        this.createResultsContainer();
        this.bindEvents();
        this.bindAdvancedSearchEvents();
        this.loadEntityTypes();
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
        
        // Escape key to close (only for global search results)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.searchResults.classList.contains('hidden')) {
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
                        // Trigger view modal event for global search (read-only)
                        const entityType = current.dataset.entityType;
                        const entityId = current.dataset.entityId;
                        
                        if (entityType && entityId) {
                            window.dispatchEvent(new CustomEvent(`open-detail-${entityType}-modal`, {
                                detail: { id: parseInt(entityId), readOnly: true }
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
            // Build type parameter based on selected entity types
            const typeParam = this.selectedEntityTypes.includes('all') ? 'all' : this.selectedEntityTypes.join(',');
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&type=${typeParam}&limit=10`);
            if (!response.ok) throw new Error('Search failed');
            
            const results = await response.json();
            this.displayResults(results);
            
        } catch (error) {
            console.error('Search error:', error);
            this.displayError();
        }
    }
    
    async loadEntityTypes() {
        const response = await fetch('/api/search/entity-types');
        if (!response.ok) {
            throw new Error(`Failed to load entity types: ${response.status} ${response.statusText}`);
        }
        
        this.entityTypes = await response.json();
        this.populateEntityTypeFilters();
    }
    
    populateEntityTypeFilters() {
        const container = document.getElementById('entity-type-filters');
        if (!container) return;
        
        container.innerHTML = '';
        
        Object.entries(this.entityTypes).forEach(([type, config]) => {
            const label = document.createElement('label');
            label.className = 'flex items-center whitespace-nowrap';
            label.innerHTML = `
                <input type="checkbox" 
                       id="search-${type}" 
                       checked 
                       class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                <span class="text-sm text-gray-700">${config.icon} ${config.name}</span>
            `;
            container.appendChild(label);
        });
    }

    bindAdvancedSearchEvents() {
        // Advanced search button click
        const advancedBtn = document.getElementById('advanced-search-btn');
        if (advancedBtn) {
            advancedBtn.addEventListener('click', () => this.openAdvancedSearch());
        }
        
        // Wire advanced search input to use same logic as global search
        const advancedQuery = document.getElementById('advanced-search-query');
        if (advancedQuery) {
            // Copy current search when modal opens
            document.addEventListener('click', (e) => {
                if (e.target.id === 'advanced-search-btn') {
                    advancedQuery.value = this.searchInput.value;
                }
            });
            
            // Make advanced search work like global search with entity filtering
            advancedQuery.addEventListener('input', (e) => {
                const query = e.target.value.trim();
                this.updateEntityTypesFromModal();
                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    this.performSearch(query);
                }, 300);
            });
            
            // Update entity types when checkboxes change
            document.addEventListener('change', (e) => {
                if (e.target.id && e.target.id.startsWith('search-')) {
                    this.updateEntityTypesFromModal();
                    this.performSearch(advancedQuery.value.trim());
                }
            });
        }
    }
    
    updateEntityTypesFromModal() {
        const selectedTypes = [];
        Object.keys(this.entityTypes).forEach(type => {
            const checkbox = document.getElementById(`search-${type}`);
            if (checkbox && checkbox.checked) {
                selectedTypes.push(type);
            }
        });
        this.selectedEntityTypes = selectedTypes.length === 0 ? ['all'] : selectedTypes;
    }
    
    openAdvancedSearch() {
        if (typeof openModalById === 'function') {
            openModalById('advanced-search-modal');
        }
        
        setTimeout(() => {
            const queryInput = document.getElementById('advanced-search-query');
            if (queryInput) {
                queryInput.focus();
            }
        }, 100);
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
                case 'company': return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>`;
                case 'contact': return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>`;
                case 'opportunity': return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>`;
                case 'task': return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
                </svg>`;
                default: return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>`;
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
                    <div class="flex-shrink-0">${getEntityTypeIcon(result.type)}</div>
                    <div class="flex-1 min-w-0">
                        <div class="text-label-primary truncate">
                            ${this.highlightQuery(result.title)}
                        </div>
                        <div class="text-xs text-gray-500 truncate">
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
                
                // Dispatch view modal event for global search (read-only)
                window.dispatchEvent(new CustomEvent(`open-detail-${entityType}-modal`, {
                    detail: { id: parseInt(entityId), readOnly: true }
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

// Filterable search manager for entity-specific search inputs
class FilterableSearchManager extends SearchManager {
    constructor(inputElement, entityFilter = 'all') {
        super();
        this.input = inputElement;
        this.entityFilter = entityFilter;
        this.resultsContainer = null;
        this.debounceTimer = null;
        this.currentQuery = '';
        
        // Override parent properties for this specific input
        this.searchInput = inputElement;
        this.searchResults = null;
        
        this.init();
    }
    
    init() {
        this.createResultsContainer();
        this.bindEvents();
    }
    
    createResultsContainer() {
        this.searchResults = document.createElement('div');
        this.searchResults.className = 'absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-b-md shadow-lg z-50 max-h-48 overflow-y-auto hidden';
        
        const container = this.input.parentElement;
        container.style.position = 'relative';
        container.appendChild(this.searchResults);
        this.resultsContainer = this.searchResults;
    }
    
    bindEvents() {
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('focus', (e) => this.handleFocus(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.searchResults.contains(e.target)) {
                this.hideResults();
            }
        });
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        this.performSearch(query);
    }
    
    async performSearch(query) {
        this.currentQuery = query;
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&type=${this.entityFilter}&limit=8`);
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
            this.hideResults();
            return;
        }
        
        let html = '';
        results.forEach(result => {
            html += `
                <div class="px-3 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                     data-id="${result.id}"
                     data-name="${result.title}"
                     data-entity-type="${result.type}">
                    <div class="text-label-primary">
                        ${this.highlightQuery(result.title)}
                    </div>
                    ${result.subtitle ? `<div class="text-xs text-gray-500">${result.subtitle}</div>` : ''}
                </div>
            `;
        });
        
        this.searchResults.innerHTML = html;
        this.bindResultEvents();
        this.showResults();
    }
    
    bindResultEvents() {
        this.searchResults.querySelectorAll('[data-id]').forEach(item => {
            item.addEventListener('click', () => {
                this.selectResult(item.dataset.id, item.dataset.name);
            });
        });
    }
    
    selectResult(id, name) {
        this.input.value = name;
        this.input.dataset.selectedId = id;
        
        // Trigger change event
        this.input.dispatchEvent(new Event('change'));
        
        this.hideResults();
    }
    
    showResults() {
        this.searchResults.classList.remove('hidden');
    }
    
    hideResults() {
        this.searchResults.classList.add('hidden');
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
                    ${suggestion.company ? `<div class="text-xs text-gray-500">${suggestion.company}</div>` : ''}
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
    
    // Initialize filterable search inputs
    document.querySelectorAll('[data-searchable]').forEach(input => {
        const entityFilter = input.dataset.searchable;
        new FilterableSearchManager(input, entityFilter);
    });
});

// Export for global access
window.SearchManager = SearchManager;
window.FilterableSearchManager = FilterableSearchManager;
window.AutocompleteManager = AutocompleteManager;