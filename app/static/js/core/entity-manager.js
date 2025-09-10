/**
 * Generic Entity Manager System
 * Provides filtering, sorting, grouping, and bulk operations for any entity type
 * Used by Tasks, Opportunities, Stakeholders, Companies, etc.
 */

/**
 * Creates a generic entity manager Alpine.js component
 * @param {Object} config - Entity-specific configuration
 * @returns {Object} Alpine.js component
 */
function createEntityManager(config) {
    return {
        // Core data
        allEntities: window[config.dataSource] || [],
        filteredEntities: [],
        
        // Filter states (initialized from backend or defaults)
        groupBy: config.defaultGroupBy || Object.keys(config.groupOptions)[0],
        sortBy: config.defaultSortBy || Object.keys(config.sortOptions)[0],
        sortDirection: config.defaultSortDirection || 'asc',
        
        // Filter arrays (empty = show all)
        primaryFilter: config.defaultPrimaryFilter || [],
        secondaryFilter: config.defaultSecondaryFilter || [],
        entityFilter: config.defaultEntityFilter || [],
        
        // UI states
        showCompleted: config.defaultShowCompleted || false,
        selectedItems: [],
        
        // Date reference
        today: new Date(config.today),
        
        // Expanded sections state
        expandedSections: { ...config.defaultExpandedSections },
        
        // Store config for access to groupOptions and other settings
        config: config,

        init() {
            // Ensure we have data before proceeding
            if (!this.allEntities || !Array.isArray(this.allEntities)) {
                console.warn(`Entity Manager: No data found for ${config.dataSource}. Using empty array.`);
                this.allEntities = [];
            }
            this.updateFilters();
            this.setupEventDelegation();
            // Ensure all sections are expanded by default
            this.expandedSections = { ...config.defaultExpandedSections };
            
            // Listen for data ready event to reload data
            document.addEventListener('dataReady', () => {
                this.reloadData();
            });
        },

        // Reload data when it becomes available
        reloadData() {
            const newData = window[config.dataSource];
            if (newData && Array.isArray(newData) && newData.length > 0) {
                console.log(`Entity Manager: Reloading ${newData.length} items from ${config.dataSource}`);
                this.allEntities = [...newData]; // Use spread to trigger reactivity
                this.updateFilters();
                // Force re-render by toggling a filter state
                const currentFilter = this.primaryFilter;
                this.primaryFilter = [...currentFilter];
                console.log('Alpine.js reactivity triggered via data spread and filter update');
            }
        },

        // Setup event delegation for dynamically rendered entity cards
        setupEventDelegation() {
            const contentContainer = document.getElementById(config.contentContainerId);
            if (!contentContainer) return;

            // Event delegation for all entity card buttons
            contentContainer.addEventListener('click', (e) => {
                const button = e.target.closest('button[title]');
                if (!button) return;

                const entityCard = button.closest(`[data-${config.entityName}-id]`);
                if (!entityCard) return;

                const entityId = parseInt(entityCard.getAttribute(`data-${config.entityName}-id`));
                if (!entityId) return;

                e.stopPropagation();

                // Route to appropriate action based on button title
                const title = button.getAttribute('title');
                this.handleEntityAction(title, entityId);
            });
        },

        // Handle entity-specific actions
        handleEntityAction(action, entityId) {
            const actionMap = config.actions || {};
            const handler = actionMap[action];
            
            if (handler && window[handler]) {
                window[handler](entityId);
            } else {
                console.warn(`No handler found for action: ${action}`);
            }
        },

        // Check if entity should be shown based on current filters
        shouldShowEntity(entity) {
            // Primary filter (e.g., priority, stage)
            const primaryMatch = this.primaryFilter.length === 0 || 
                                  this.primaryFilter.includes(this.getPrimaryFilterValue(entity));
            
            // Secondary filter (e.g., status, company)  
            const secondaryMatch = this.secondaryFilter.length === 0 || 
                                   this.secondaryFilter.includes(this.getSecondaryFilterValue(entity));
            
            // Entity filter (e.g., related entity type)
            const entityMatch = this.entityFilter.length === 0 || 
                                this.entityFilter.includes(this.getEntityFilterValue(entity));
            
            // Completed/closed status filter
            const completedMatch = !this.isCompleted(entity) || this.showCompleted;
            
            return primaryMatch && secondaryMatch && entityMatch && completedMatch;
        },

        // Get primary filter value using config
        getPrimaryFilterValue(entity) {
            if (config.getPrimaryFilterValue) {
                return config.getPrimaryFilterValue(entity);
            }
            if (config.priorityLogic) {
                return config.priorityLogic(entity);
            }
            return entity[config.primaryFilterField] || 'none';
        },

        // Get secondary filter value using config
        getSecondaryFilterValue(entity) {
            if (config.getSecondaryFilterValue) {
                return config.getSecondaryFilterValue(entity);
            }
            return entity[config.secondaryFilterField] || 'none';
        },

        // Get entity filter value using config
        getEntityFilterValue(entity) {
            if (config.getEntityFilterValue) {
                return config.getEntityFilterValue(entity);
            }
            const value = entity[config.entityFilterField];
            return value || 'unrelated';
        },

        // Check if entity is completed/closed
        isCompleted(entity) {
            return config.isCompleted ? config.isCompleted(entity) : false;
        },

        // Update filters and refresh display
        updateFilters() {
            // Apply all filters and sorting
            let entities = [...this.allEntities];
            
            // Filter entities
            entities = entities.filter(entity => this.shouldShowEntity(entity));
            
            // Sort entities
            entities = this.sortEntities(entities);
            
            this.filteredEntities = entities;
            this.updateUrlState();
        },

        // Sort entities based on current sort settings
        sortEntities(entities) {
            return entities.sort((a, b) => {
                let comparison = 0;
                const sortConfig = config.sortOptions[this.sortBy];
                
                if (sortConfig && sortConfig.compareFn) {
                    comparison = sortConfig.compareFn(a, b);
                } else {
                    // Default string/date comparison
                    const valueA = a[this.sortBy] || '';
                    const valueB = b[this.sortBy] || '';
                    
                    if (valueA < valueB) comparison = -1;
                    else if (valueA > valueB) comparison = 1;
                    else comparison = 0;
                }
                
                return this.sortDirection === 'desc' ? -comparison : comparison;
            });
        },

        // Update URL state for persistence
        updateUrlState() {
            if (!config.persistState) return;
            
            const params = new URLSearchParams(window.location.search);
            params.set('group_by', this.groupBy);
            params.set('sort_by', this.sortBy);
            params.set('sort_direction', this.sortDirection);
            params.set('show_completed', this.showCompleted.toString());
            params.set('primary_filter', this.primaryFilter.join(','));
            params.set('secondary_filter', this.secondaryFilter.join(','));
            params.set('entity_filter', this.entityFilter.join(','));
            
            const newUrl = window.location.pathname + '?' + params.toString();
            window.history.pushState({}, '', newUrl);
        },

        // Main grouping function - returns grouped and filtered entities
        getGroupedEntities() {
            // 1. Filter entities first
            let filteredEntities = this.allEntities.filter(entity => this.shouldShowEntity(entity));
            
            // 2. Sort entities
            let sortedEntities = this.sortEntities(filteredEntities);
            
            // 3. Group by current groupBy setting
            return this.groupEntitiesByType(sortedEntities, this.groupBy);
        },

        // Group entities by the specified type
        groupEntitiesByType(entities, groupType) {
            const groupConfig = config.groupOptions[groupType];
            if (!groupConfig) return [];

            // Handle dynamic groups that need to be generated from data
            let groups = groupConfig.groups;
            if (groupConfig.isDynamic && groupConfig.generateGroups) {
                groups = groupConfig.generateGroups(entities);
            }

            return groups.map(group => ({
                ...group,
                entities: entities.filter(entity => {
                    if (groupConfig.filterFn) {
                        return groupConfig.filterFn(entity, group.key);
                    }
                    return entity[groupConfig.field] === group.key;
                })
            }));
        },

        // Toggle section expansion
        toggleSection(sectionKey) {
            this.expandedSections[sectionKey] = !this.expandedSections[sectionKey];
        },

        // Filter helper functions for multiselects
        togglePrimaryFilter(value) {
            if (this.primaryFilter.includes(value)) {
                this.primaryFilter = this.primaryFilter.filter(v => v !== value);
            } else {
                this.primaryFilter.push(value);
            }
            this.updateFilters();
        },

        toggleSecondaryFilter(value) {
            if (this.secondaryFilter.includes(value)) {
                this.secondaryFilter = this.secondaryFilter.filter(v => v !== value);
            } else {
                this.secondaryFilter.push(value);
            }
            this.updateFilters();
        },

        toggleEntityFilter(value) {
            if (this.entityFilter.includes(value)) {
                this.entityFilter = this.entityFilter.filter(v => v !== value);
            } else {
                this.entityFilter.push(value);
            }
            this.updateFilters();
        },

        // Display text helpers for multiselects
        getPrimaryFilterDisplayText() {
            if (this.primaryFilter.length === 0) return config.primaryFilterLabel || 'All';
            if (this.primaryFilter.length === 1) {
                const option = config.primaryFilterOptions.find(opt => opt.value === this.primaryFilter[0]);
                return option ? option.label : this.primaryFilter[0];
            }
            return `${this.primaryFilter.length} Selected`;
        },

        getSecondaryFilterDisplayText() {
            if (this.secondaryFilter.length === 0) return config.secondaryFilterLabel || 'All';
            if (this.secondaryFilter.length === 1) {
                const option = config.secondaryFilterOptions.find(opt => opt.value === this.secondaryFilter[0]);
                return option ? option.label : this.secondaryFilter[0];
            }
            return `${this.secondaryFilter.length} Selected`;
        },

        getEntityFilterDisplayText() {
            if (this.entityFilter.length === 0) return config.entityFilterLabel || 'All';
            if (this.entityFilter.length === 1) {
                const option = config.entityFilterOptions.find(opt => opt.value === this.entityFilter[0]);
                return option ? option.label : this.entityFilter[0];
            }
            return `${this.entityFilter.length} Selected`;
        },

        // Get pre-rendered entity card HTML
        renderEntityCard(entity, groupContext) {
            const cachedElement = document.getElementById(`${config.entityName}-card-${entity.id}`);
            return cachedElement ? cachedElement.innerHTML : '';
        },

        // Helper to get icon HTML (can be overridden by config)
        getIconHTML(iconType) {
            if (config.icons && config.icons[iconType]) {
                return config.icons[iconType];
            }
            // Use centralized icon utility
            return '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>';
        },

        // Bulk operations
        selectAll() {
            this.selectedItems = this.filteredEntities.map(entity => entity.id);
        },

        clearSelection() {
            this.selectedItems = [];
        },

        bulkAction(actionName) {
            if (config.bulkActions && config.bulkActions[actionName]) {
                config.bulkActions[actionName](this.selectedItems);
            }
        }
    };
}

// Export for global use
window.createEntityManager = createEntityManager;