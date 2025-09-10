/**
 * Icon Utility - Centralized icon management system
 * Fetches icon HTML from Jinja2 macros and provides caching
 */

class IconUtility {
    constructor() {
        this.cache = new Map();
        this.iconMapping = {
            // Entity type icons
            'company': 'building_office_alt_icon',
            'contact': 'user_icon', 
            'opportunity': 'currency_dollar_icon',
            'task': 'check_icon',
            
            // Priority icons
            'high': 'fire_icon_solid',
            'medium': 'exclamation_triangle_icon',
            'low': 'question_mark_circle_icon',
            
            // Status icons
            'to_do': 'clipboard_list_icon',
            'in_progress': 'bolt_icon',
            'completed': 'check_circle_icon_solid',
            
            // Due date icons
            'overdue': 'exclamation_circle_icon_solid',
            'due_today': 'calendar_days_icon',
            'this_week': 'calendar_icon',
            'later': 'chart_bar_icon',
            'no_due_date': 'question_mark_circle_icon',
            
            // Stage icons (opportunities)
            'prospect': 'building_office_alt_icon',
            'qualified': 'chart_bar_icon',
            'proposal': 'currency_dollar_icon',
            'negotiation': 'clock_icon',
            'closed_won': 'check_circle_icon',
            'closed_lost': 'exclamation_circle_icon_solid',
            
            // Time-based icons
            'calendar': 'calendar_icon',
            'calendar_days': 'calendar_days_icon',
            'clock': 'clock_icon',
            
            // General purpose
            'chevron': 'chevron_right_icon',
            'plus': 'plus_icon',
            'edit': 'pencil_icon',
            'email': 'envelope_icon',
            'phone': 'phone_icon',
            'delete': 'trash_icon',
            'document': 'document_icon',
            
            // Alternative versions
            'fire_alt': 'fire_alt_icon',
            'exclamation_triangle_alt': 'exclamation_triangle_alt_icon',
            'check_circle': 'check_circle_icon',
            'information_circle': 'information_circle_icon',
            'currency_dollar_circle': 'currency_dollar_circle_icon'
        };
    }

    /**
     * Get icon HTML by name
     * @param {string} iconName - Name from iconMapping
     * @param {string} className - CSS classes (default: w-5 h-5)
     * @returns {Promise<string>} HTML string of the icon
     */
    async getIcon(iconName, className = 'w-5 h-5') {
        const macroName = this.iconMapping[iconName];
        if (!macroName) {
            throw new Error(`Icon '${iconName}' not found in mapping. Available icons: ${Object.keys(this.iconMapping).join(', ')}`);
        }

        const cacheKey = `${macroName}_${className}`;
        
        // Return cached version if available
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        try {
            // Fetch icon HTML from server endpoint
            const response = await fetch('/api/icon', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    macro_name: macroName,
                    class: className
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch icon: ${response.status}`);
            }

            const iconHtml = await response.text();
            
            // Cache the result
            this.cache.set(cacheKey, iconHtml);
            
            return iconHtml;
        } catch (error) {
            console.error(`Error fetching icon '${iconName}':`, error);
            throw new Error(`Failed to fetch icon '${iconName}': ${error.message}`);
        }
    }

    /**
     * Get icon synchronously (requires pre-loading)
     * @param {string} iconName - Name from iconMapping
     * @param {string} className - CSS classes
     * @returns {string} HTML string or fallback
     */
    getIconSync(iconName, className = 'w-5 h-5') {
        const macroName = this.iconMapping[iconName];
        if (!macroName) {
            throw new Error(`Icon '${iconName}' not found in mapping. Available icons: ${Object.keys(this.iconMapping).join(', ')}`);
        }

        const cacheKey = `${macroName}_${className}`;
        const cachedIcon = this.cache.get(cacheKey);
        if (!cachedIcon) {
            throw new Error(`Icon '${iconName}' not loaded. Use preloadIcons() or getIcon() first.`);
        }
        return cachedIcon;
    }

    /**
     * Pre-load commonly used icons
     * @param {Array<string>} iconNames - Array of icon names to pre-load
     * @param {string} className - CSS classes
     */
    async preloadIcons(iconNames, className = 'w-5 h-5') {
        const promises = iconNames.map(name => this.getIcon(name, className));
        await Promise.all(promises);
    }


    /**
     * Clear icon cache
     */
    clearCache() {
        this.cache.clear();
    }

    /**
     * Get all available icon names
     * @returns {Array<string>} Array of available icon names
     */
    getAvailableIcons() {
        return Object.keys(this.iconMapping);
    }
}

// Create global instance
window.iconUtility = new IconUtility();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IconUtility;
}