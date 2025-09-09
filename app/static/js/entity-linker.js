/**
 * Entity Linker - Search and link entities
 * Extracted from template macro for clean separation
 */

/**
 * Create entity linker functionality
 * @param {string} fieldName - Name for the hidden form field
 * @param {string} placeholder - Placeholder text for search input
 * @param {Array} selectedEntities - Pre-selected entities
 * @param {string} entityTypes - Comma-separated entity types to search
 */
function createEntityLinker(fieldName, placeholder = "Search entities...", selectedEntities = [], entityTypes = "company,contact,opportunity") {
    return {
        search: '',
        suggestions: [],
        selectedEntities: [...selectedEntities],
        isSearching: false,
        showDropdown: false,
        fieldName: fieldName,
        allowedTypes: entityTypes.split(','),
        
        async searchEntities(force = false) {
            // Always search if forced (on focus), otherwise need at least some text
            if (!force && this.search.length < 1) {
                this.suggestions = [];
                this.showDropdown = false;
                return;
            }
            
            this.isSearching = true;
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(this.search)}&limit=10`);
                const results = await response.json();
                
                // Filter by allowed entity types
                this.suggestions = results.filter(item => this.allowedTypes.includes(item.type));
                this.showDropdown = this.suggestions.length > 0;
            } catch (error) {
                console.error('Search error:', error);
                this.suggestions = [];
            } finally {
                this.isSearching = false;
            }
        },
        
        selectEntity(entity) {
            // Check if already selected
            const exists = this.selectedEntities.some(e => e.type === entity.type && e.id === entity.id);
            if (!exists) {
                this.selectedEntities.push({
                    type: entity.type,
                    id: entity.id,
                    name: entity.title || entity.name
                });
            }
            this.search = '';
            this.suggestions = [];
            this.showDropdown = false;
            this.updateHiddenField();
        },
        
        removeEntity(index) {
            this.selectedEntities.splice(index, 1);
            this.updateHiddenField();
        },
        
        updateHiddenField() {
            // Update hidden field with JSON representation
            const hiddenField = document.querySelector(`input[name="${this.fieldName}"]`);
            if (hiddenField) {
                hiddenField.value = JSON.stringify(this.selectedEntities);
            }
        },

        // Formatting helpers
        getEntityDisplayName(entity) {
            return entity.name || entity.title || 'Unknown';
        },

        getEntityTypeDisplay(type) {
            const typeMap = {
                company: 'Company',
                contact: 'Contact', 
                opportunity: 'Opportunity',
                task: 'Task'
            };
            return typeMap[type] || type;
        },

        // Event handlers
        onFocus() {
            if (this.search.length === 0) {
                this.searchEntities(true); // Force search on focus
            }
        },

        onBlur() {
            // Delay hiding dropdown to allow clicks
            setTimeout(() => {
                this.showDropdown = false;
            }, 200);
        },

        onInput() {
            this.searchEntities();
        }
    };
}

// Global factory function
window.createEntityLinker = createEntityLinker;