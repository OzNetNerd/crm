/**
 * Entity Linker - Alpine.js Component
 * 
 * Interactive entity search and selection component.
 * Separates concerns: search logic in Alpine.js, template in macro.
 * 
 * @param {Object} config - Configuration object
 * @param {string} config.fieldName - Name of the form field
 * @param {Array} config.selectedEntities - Pre-selected entities
 * @param {string} config.entityTypes - Comma-separated allowed entity types
 */
window.entityLinker = (config) => {
    const { fieldName, selectedEntities = [], entityTypes = 'company,contact,opportunity' } = config;
    
    return {
        // Search state
        search: '',
        suggestions: [],
        isSearching: false,
        showDropdown: false,
        
        // Selection state
        selectedEntities: [...selectedEntities],
        
        // Entity type configuration
        entityTypeConfig: {
            company: { icon: '🏢', badgeClass: 'bg-blue-100 text-blue-800' },
            contact: { icon: '👤', badgeClass: 'bg-green-100 text-green-800' },
            stakeholder: { icon: '👤', badgeClass: 'bg-green-100 text-green-800' },
            opportunity: { icon: '💼', badgeClass: 'bg-purple-100 text-purple-800' },
            task: { icon: '📋', badgeClass: 'bg-yellow-100 text-yellow-800' }
        },
        
        // Initialize component
        init() {
            this.updateHiddenField();
        },
        
        // Search functionality
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
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const results = await response.json();
                
                // Filter by allowed entity types
                const allowedTypes = entityTypes.split(',').map(t => t.trim());
                this.suggestions = results.filter(item => 
                    allowedTypes.includes(item.type) || 
                    allowedTypes.includes(item.entity_type)
                );
                
                this.showDropdown = this.suggestions.length > 0;
                
            } catch (error) {
                console.error('Entity search error:', error);
                this.suggestions = [];
                this.showDropdown = false;
            } finally {
                this.isSearching = false;
            }
        },
        
        // Selection management
        selectEntity(entity) {
            // Check if already selected
            const exists = this.selectedEntities.some(e => 
                e.type === entity.type && e.id === entity.id
            );
            
            if (!exists) {
                this.selectedEntities.push({
                    type: entity.type || entity.entity_type,
                    id: entity.id,
                    name: entity.title || entity.name
                });
            }
            
            // Clear search
            this.search = '';
            this.suggestions = [];
            this.showDropdown = false;
            
            // Update form field
            this.updateHiddenField();
        },
        
        removeEntity(index) {
            if (index >= 0 && index < this.selectedEntities.length) {
                this.selectedEntities.splice(index, 1);
                this.updateHiddenField();
            }
        },
        
        clearAllEntities() {
            this.selectedEntities = [];
            this.updateHiddenField();
        },
        
        // Form integration
        updateHiddenField() {
            const hiddenField = this.$el.querySelector(`input[name="${fieldName}"]`);
            if (hiddenField) {
                hiddenField.value = JSON.stringify(this.selectedEntities);
            }
        },
        
        // Utility functions
        getEntityTypeIcon(type) {
            return this.entityTypeConfig[type]?.icon || '📄';
        },
        
        getEntityTypeBadgeClass(type) {
            return this.entityTypeConfig[type]?.badgeClass || 'bg-gray-100 text-gray-800';
        },
        
        getEntityTypeLabel(type) {
            return type.charAt(0).toUpperCase() + type.slice(1);
        },
        
        // Keyboard navigation (future enhancement)
        onKeydown(event) {
            // Could add arrow key navigation of suggestions
            if (event.key === 'Escape') {
                this.showDropdown = false;
            }
        },
        
        // Close dropdown when clicking outside
        closeDropdown() {
            this.showDropdown = false;
        }
    };
};