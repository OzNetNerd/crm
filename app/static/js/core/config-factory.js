/**
 * Model Config Factory
 * Builds JavaScript configurations from server-side model metadata
 * This eliminates hardcoded values and makes JS truly driven by backend models
 */

class ModelConfigFactory {
    /**
     * Build opportunity stage groups from model metadata
     */
    static buildOpportunityStageGroups(stageConfig) {
        if (!stageConfig || !stageConfig.choices) {
            return [];
        }

        return Object.entries(stageConfig.choices).map(([key, config]) => ({
            key: key,
            title: config.label,
            containerClass: `card-${this.getColorFromCssClass(config.css_class)}`,
            headerClass: `text-status-${this.getColorFromCssClass(config.css_class)}`,
            headerBgClass: `border-b border-${this.getColorFromCssClass(config.css_class)}-200 px-6 py-4 bg-${this.getColorFromCssClass(config.css_class)}-50 hover:bg-${this.getColorFromCssClass(config.css_class)}-100`,
            badgeClass: `badge-${this.getColorFromCssClass(config.css_class)}`,
            icon: config.icon || '',
            order: config.order || 0
        })).sort((a, b) => a.order - b.order);
    }

    /**
     * Build task priority groups from model metadata
     */
    static buildTaskPriorityGroups(priorityConfig) {
        if (!priorityConfig || !priorityConfig.choices) {
            return [];
        }

        return Object.entries(priorityConfig.choices).map(([key, config]) => ({
            key: key,
            title: config.label,
            containerClass: `card-${this.getColorFromCssClass(config.css_class)}`,
            headerClass: `text-priority-${key}`,
            headerBgClass: `border-b border-${this.getColorFromCssClass(config.css_class)}-200 px-6 py-4 bg-${this.getColorFromCssClass(config.css_class)}-50 hover:bg-${this.getColorFromCssClass(config.css_class)}-100`,
            badgeClass: `badge-${this.getColorFromCssClass(config.css_class)}`,
            icon: config.icon || '',
            order: config.order || 0
        })).sort((a, b) => a.order - b.order);
    }

    /**
     * Build task status groups from model metadata
     */
    static buildTaskStatusGroups(statusConfig) {
        if (!statusConfig || !statusConfig.choices) {
            return [];
        }

        return Object.entries(statusConfig.choices).map(([key, config]) => ({
            key: key,
            title: config.label,
            containerClass: `card-${this.getColorFromCssClass(config.css_class)}`,
            headerClass: `text-status-${key}`,
            headerBgClass: `border-b border-${this.getColorFromCssClass(config.css_class)}-200 px-6 py-4 bg-${this.getColorFromCssClass(config.css_class)}-50 hover:bg-${this.getColorFromCssClass(config.css_class)}-100`,
            badgeClass: `badge-${this.getColorFromCssClass(config.css_class)}`,
            icon: config.icon || '',
            order: config.order || 0
        })).sort((a, b) => a.order - b.order);
    }

    /**
     * Get completion checker function for opportunities
     */
    static buildOpportunityCompletionChecker(stageConfig) {
        if (!stageConfig || !stageConfig.choices) {
            return () => false;
        }

        // Find stages that indicate completion (typically closed-won, closed-lost)
        const completedStages = Object.entries(stageConfig.choices)
            .filter(([key, config]) => key.includes('closed') || config.description?.includes('closed'))
            .map(([key]) => key);

        return (opportunity) => completedStages.includes(opportunity.stage);
    }

    /**
     * Get priority calculation function for opportunities based on value ranges
     */
    static buildOpportunityPriorityCalculator(valueConfig) {
        return (opportunity) => {
            if (!opportunity.value || !valueConfig?.priority_ranges) {
                return 'low';
            }

            // priority_ranges is array of [min_value, priority, label, css_class]
            for (const [minValue, priority, label, cssClass] of valueConfig.priority_ranges) {
                if (opportunity.value >= minValue) {
                    return priority;
                }
            }
            return 'low';
        };
    }

    /**
     * Build validation rules from model metadata
     */
    static buildFieldValidation(fieldConfig) {
        const validation = {};
        
        if (fieldConfig.choices) {
            validation.validChoices = Object.keys(fieldConfig.choices);
        }
        
        if (fieldConfig.min_value !== undefined) {
            validation.minValue = fieldConfig.min_value;
        }
        
        if (fieldConfig.max_value !== undefined) {
            validation.maxValue = fieldConfig.max_value;
        }
        
        return validation;
    }

    /**
     * Extract color name from CSS class (e.g. 'status-prospect' -> 'green')
     */
    static getColorFromCssClass(cssClass) {
        if (!cssClass) return 'gray';
        
        // Map common CSS classes to colors
        const colorMap = {
            'status-prospect': 'green',
            'status-qualified': 'blue', 
            'status-proposal': 'yellow',
            'status-negotiating': 'orange',
            'status-won': 'green',
            'status-lost': 'gray',
            'priority-urgent': 'red',
            'priority-normal': 'yellow', 
            'priority-low': 'green',
            'status-todo': 'blue',
            'status-progress': 'yellow',
            'status-complete': 'green'
        };

        return colorMap[cssClass] || 'gray';
    }

    /**
     * Build complete entity configuration from model metadata
     */
    static buildEntityConfig(entityName, modelConfig) {
        if (!modelConfig) {
            console.warn(`No model config found for ${entityName}`);
            return {};
        }

        const config = {
            entityName: entityName,
            modelConfig: modelConfig
        };

        // Add entity-specific builders
        if (entityName === 'opportunity' && modelConfig.stage) {
            config.stageGroups = this.buildOpportunityStageGroups(modelConfig.stage);
            config.isCompleted = this.buildOpportunityCompletionChecker(modelConfig.stage);
            if (modelConfig.value) {
                config.priorityLogic = this.buildOpportunityPriorityCalculator(modelConfig.value);
            }
        }

        if (modelConfig.priority) {
            config.priorityGroups = this.buildTaskPriorityGroups(modelConfig.priority);
        }

        if (modelConfig.status) {
            config.statusGroups = this.buildTaskStatusGroups(modelConfig.status);
        }

        return config;
    }
}