/**
 * Centralized Color Scheme Manager
 * Provides consistent color assignment and management across all entity types
 */

class ColorSchemeManager {
    constructor() {
        // Define color schemes with consistent class naming
        this.colorSchemes = [
            {
                name: 'blue',
                containerClass: 'card-info',
                headerClass: 'text-status-info',
                headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100',
                badgeClass: 'badge-blue'
            },
            {
                name: 'green',
                containerClass: 'card-success',
                headerClass: 'text-status-success',
                headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100',
                badgeClass: 'badge-green'
            },
            {
                name: 'yellow',
                containerClass: 'card-warning',
                headerClass: 'text-status-warning',
                headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100',
                badgeClass: 'badge-yellow'
            },
            {
                name: 'orange',
                containerClass: 'card-orange',
                headerClass: 'text-status-warning',
                headerBgClass: 'border-b border-orange-200 px-6 py-4 bg-orange-50 hover:bg-orange-100',
                badgeClass: 'badge-orange'
            },
            {
                name: 'red',
                containerClass: 'card-danger',
                headerClass: 'text-status-overdue',
                headerBgClass: 'border-b border-red-200 px-6 py-4 bg-red-50 hover:bg-red-100',
                badgeClass: 'badge-red'
            },
            {
                name: 'purple',
                containerClass: 'card-purple',
                headerClass: 'text-purple-700',
                headerBgClass: 'border-b border-purple-200 px-6 py-4 bg-purple-50 hover:bg-purple-100',
                badgeClass: 'badge-purple'
            },
            {
                name: 'gray',
                containerClass: 'card-neutral',
                headerClass: 'text-status-neutral',
                headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100',
                badgeClass: 'badge-gray'
            }
        ];

        // Cache for consistent color assignment
        this.colorCache = new Map();
    }

    /**
     * Generate a simple hash from a string for consistent color assignment
     */
    hashString(str) {
        let hash = 0;
        if (str.length === 0) return hash;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash);
    }

    /**
     * Get a color scheme for a given key with consistent assignment
     * @param {string} key - Unique identifier for color assignment
     * @param {string} cachePrefix - Optional prefix for cache key to avoid collisions
     * @returns {Object} Color scheme object
     */
    getColorScheme(key, cachePrefix = '') {
        const cacheKey = `${cachePrefix}_${key}`;
        
        // Check cache first
        if (this.colorCache.has(cacheKey)) {
            return this.colorCache.get(cacheKey);
        }

        // Generate consistent color based on hash
        const hash = this.hashString(key);
        const colorIndex = hash % this.colorSchemes.length;
        const colorScheme = this.colorSchemes[colorIndex];

        // Cache the result
        this.colorCache.set(cacheKey, colorScheme);
        
        return colorScheme;
    }

    /**
     * Get rotating color scheme for dynamic groups (like companies)
     * Ensures good distribution across available colors
     */
    getRotatingColorScheme(items, cachePrefix = 'dynamic') {
        return items.map((item, index) => {
            const colorIndex = index % this.colorSchemes.length;
            const colorScheme = this.colorSchemes[colorIndex];
            
            // Cache for consistency
            const cacheKey = `${cachePrefix}_${item}`;
            this.colorCache.set(cacheKey, colorScheme);
            
            return {
                key: item,
                ...colorScheme
            };
        });
    }

    /**
     * Get predefined color schemes for specific entity types
     */
    getPredefinedSchemes() {
        return {
            // Task status colors
            taskStatus: {
                todo: this.colorSchemes[0], // blue
                'in-progress': this.colorSchemes[2], // yellow
                complete: this.colorSchemes[1] // green
            },
            
            // Task priority colors  
            taskPriority: {
                high: this.colorSchemes[4], // red
                medium: this.colorSchemes[2], // yellow
                low: this.colorSchemes[1] // green
            },
            
            // Opportunity stage colors
            opportunityStage: {
                prospect: this.colorSchemes[1], // green
                qualified: this.colorSchemes[0], // blue
                proposal: this.colorSchemes[2], // yellow
                negotiation: this.colorSchemes[3] // orange
            },
            
            // Contact info status colors
            contactInfo: {
                complete: this.colorSchemes[1], // green
                email_only: this.colorSchemes[0], // blue
                phone_only: this.colorSchemes[2], // yellow
                missing: this.colorSchemes[4] // red
            },
            
            // Industry colors (for contacts)
            industry: {
                technology: this.colorSchemes[0], // blue
                finance: this.colorSchemes[1], // green
                healthcare: this.colorSchemes[2], // yellow
                manufacturing: this.colorSchemes[3], // orange
                unknown: this.colorSchemes[6] // gray
            }
        };
    }

    /**
     * Clear color cache (useful for testing or reset)
     */
    clearCache() {
        this.colorCache.clear();
    }

    /**
     * Get available color scheme names
     */
    getAvailableColors() {
        return this.colorSchemes.map(scheme => scheme.name);
    }
}

// Create global instance
window.colorSchemeManager = new ColorSchemeManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ColorSchemeManager;
}