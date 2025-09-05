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
        
        if (query.length < 2) {
            this.hideResults();
            return;
        }
        
        // Debounce search requests
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }
    
    handleFocus(e) {
        if (this.currentQuery && this.searchResults.children.length > 0) {
            this.showResults();
        }
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
                        current.click();
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
            const groupedResults = this.groupResultsByType(results);
            this.searchResults.innerHTML = this.renderGroupedResults(groupedResults);
        }
        
        this.showResults();
    }
    
    groupResultsByType(results) {
        const groups = {};
        
        results.forEach(result => {
            if (!groups[result.type]) {
                groups[result.type] = [];
            }
            groups[result.type].push(result);
        });
        
        return groups;
    }
    
    renderGroupedResults(groups) {
        const typeLabels = {
            company: 'Companies',
            contact: 'Contacts', 
            opportunity: 'Opportunities',
            task: 'Tasks'
        };
        
        let html = '';
        
        Object.keys(groups).forEach(type => {
            html += `
                <div class="border-b border-gray-100 last:border-b-0">
                    <div class="px-4 py-2 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wide">
                        ${typeLabels[type] || type}
                    </div>
            `;
            
            groups[type].forEach(result => {
                html += this.renderSearchItem(result);
            });
            
            html += '</div>';
        });
        
        return html;
    }
    
    renderSearchItem(result) {
        const iconMap = {
            company: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21h18M5 21V7l8-4v18M9 9h1m0 0h1m-1 0v1m0-1V8m3 1h1m0 0h1m-1 0v1m0-1V8"/></svg>',
            contact: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>',
            opportunity: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/></svg>',
            task: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>'
        };
        
        return `
            <a href="${result.url}" 
               role="option"
               aria-selected="false"
               class="block px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0">
                <div class="flex items-center space-x-3">
                    <span class="text-lg">${iconMap[result.type] || '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>'}</span>
                    <div class="flex-1 min-w-0">
                        <div class="text-sm font-medium text-gray-900 truncate">
                            ${this.highlightQuery(result.title)}
                        </div>
                        <div class="text-xs text-gray-500 truncate">
                            ${result.subtitle || ''}
                        </div>
                    </div>
                </div>
            </a>
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
        
        if (query.length < 2) {
            this.hideResults();
            return;
        }
        
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300);
    }
    
    handleFocus(e) {
        if (e.target.value.length >= 2) {
            this.fetchSuggestions(e.target.value.trim());
        }
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
                    <div class="text-sm font-medium text-gray-900">
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
});

// Export for global access
window.SearchManager = SearchManager;
window.AutocompleteManager = AutocompleteManager;