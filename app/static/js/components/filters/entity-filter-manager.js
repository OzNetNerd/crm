/**
 * Entity Filter Manager - Extracted from template macros
 * Provides comprehensive filtering, sorting, and grouping for entity lists
 */

/**
 * Create entity filter manager for a specific entity type
 * @param {string} entityType - The entity type (companies, contacts, etc.)
 * @param {Array} groupOptions - Available grouping options
 * @param {Array} sortOptions - Available sorting options
 * @param {Object} filterOptions - Entity-specific filter options
 * @param {Object} initialValues - Initial filter state
 */
function createEntityFilterManager(entityType, groupOptions, sortOptions, filterOptions = {}, initialValues = {}) {
    return {
        // Core filter states
        allItems: window[`${entityType}Data`] || [],
        filteredItems: [],
        
        // Display states  
        viewMode: initialValues.view_mode || 'grid',
        groupBy: initialValues.group_by || (groupOptions[0] && groupOptions[0].value) || 'none',
        sortBy: initialValues.sort_by || (sortOptions[0] && sortOptions[0].value) || 'name',
        sortDirection: initialValues.sort_direction || 'asc',
        
        // Dynamic filter properties
        ...Object.keys(filterOptions).reduce((filters, key) => {
            filters[`${key}Filter`] = initialValues[`${key}_filter`] || [];
            return filters;
        }, {}),
        
        showCompleted: initialValues.show_completed || false,
        
        // Expanded sections state
        expandedSections: {},

        init() {
            // Initialize expanded sections
            groupOptions.forEach(option => {
                if (option.sections) {
                    option.sections.forEach(section => {
                        this.expandedSections[section] = true;
                    });
                }
            });
            this.updateFilters();
        },

        // Core filtering and sorting
        shouldShowItem(item) {
            // Apply all dynamic filters
            for (const [filterKey] of Object.entries(filterOptions)) {
                const filterArray = this[`${filterKey}Filter`] || [];
                if (filterArray.length > 0 && !filterArray.includes(item[filterKey])) {
                    return false;
                }
            }
            
            // Show completed items check
            if (item.status === 'complete' && !this.showCompleted) {
                return false;
            }
            
            return true;
        },

        updateFilters() {
            // Apply filters
            this.filteredItems = this.allItems.filter(item => this.shouldShowItem(item));
            
            // Apply sorting
            this.filteredItems.sort((a, b) => {
                let valueA = a[this.sortBy];
                let valueB = b[this.sortBy];
                
                // Handle different data types
                if (typeof valueA === 'string') {
                    valueA = valueA.toLowerCase();
                    valueB = (valueB || '').toLowerCase();
                }
                
                if (valueA < valueB) return this.sortDirection === 'asc' ? -1 : 1;
                if (valueA > valueB) return this.sortDirection === 'asc' ? 1 : -1;
                return 0;
            });
            
            // Trigger UI update
            this.updateUI();
        },

        updateUI() {
            // This method should be overridden or extended by specific implementations
            console.log(`Filtered ${this.filteredItems.length} items from ${this.allItems.length} total`);
        },

        // Group management
        getGroupedItems() {
            if (this.groupBy === 'none') {
                return { 'All Items': this.filteredItems };
            }
            
            return this.filteredItems.reduce((groups, item) => {
                const groupValue = item[this.groupBy] || 'Uncategorized';
                if (!groups[groupValue]) {
                    groups[groupValue] = [];
                }
                groups[groupValue].push(item);
                return groups;
            }, {});
        },

        // Filter toggle methods
        toggleFilter(filterName, value) {
            const filterArray = this[`${filterName}Filter`] || [];
            const index = filterArray.indexOf(value);
            
            if (index > -1) {
                filterArray.splice(index, 1);
            } else {
                filterArray.push(value);
            }
            
            this.updateFilters();
        },

        // Display text helpers
        getFilterDisplayText(filterName, placeholder = 'All') {
            const filterArray = this[`${filterName}Filter`] || [];
            if (filterArray.length === 0) return placeholder;
            if (filterArray.length === 1) return filterArray[0];
            return `${filterArray.length} selected`;
        }
    };
}

// Global factory function for backward compatibility
window.createEntityFilterManager = createEntityFilterManager;