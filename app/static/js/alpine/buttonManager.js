/**
 * Alpine.js Button Manager
 *
 * Replaces button_generator.py server-side button generation with client-side Alpine.js
 * Provides dynamic button rendering and click handling.
 */
window.buttonManager = (config = {}) => {
    const { entityTypes = [], buttonType = 'create' } = config;

    return {
        // Button configurations (replaces EntityButtonGenerator)
        buttonConfigs: {
            company: {
                label: 'New Company',
                icon: 'icon-company',
                color: 'bg-blue-600 hover:bg-blue-700',
                description: 'Create a new company'
            },
            contact: {
                label: 'New Contact',
                icon: 'icon-contact',
                color: 'bg-green-600 hover:bg-green-700',
                description: 'Create a new contact'
            },
            opportunity: {
                label: 'New Opportunity',
                icon: 'icon-opportunity',
                color: 'bg-purple-600 hover:bg-purple-700',
                description: 'Create a new opportunity'
            },
            task: {
                label: 'New Task',
                icon: 'icon-task',
                color: 'bg-orange-600 hover:bg-orange-700',
                description: 'Create a new task'
            },
            stakeholder: {
                label: 'New Stakeholder',
                icon: 'icon-stakeholder',
                color: 'bg-indigo-600 hover:bg-indigo-700',
                description: 'Create a new stakeholder'
            }
        },

        // Generate buttons for given entity types
        get buttons() {
            return entityTypes.map(entityType => ({
                ...this.buttonConfigs[entityType.toLowerCase()],
                entityType: entityType.toLowerCase(),
                id: `new-${entityType.toLowerCase()}-btn`
            })).filter(button => button.label); // Filter out unknown entity types
        },

        // Dashboard buttons (most common entities)
        get dashboardButtons() {
            const dashboardEntities = ['company', 'contact', 'opportunity', 'task'];
            return dashboardEntities.map(entityType => ({
                ...this.buttonConfigs[entityType],
                entityType: entityType,
                id: `new-${entityType}-btn`
            }));
        },

        // Handle button click - open modal
        handleButtonClick(entityType, actionType = 'create') {
            // Dispatch custom event to open modal
            window.dispatchEvent(new CustomEvent('open-modal', {
                detail: {
                    type: actionType,
                    modelName: entityType,
                    id: null
                }
            }));
        },

        // Handle entity edit - open edit modal
        editEntity(entityType, entityId) {
            window.dispatchEvent(new CustomEvent('open-modal', {
                detail: {
                    type: 'edit',
                    modelName: entityType,
                    id: entityId
                }
            }));
        },

        // Handle entity view - open view modal
        viewEntity(entityType, entityId) {
            window.dispatchEvent(new CustomEvent('open-modal', {
                detail: {
                    type: 'view',
                    modelName: entityType,
                    id: entityId
                }
            }));
        },

        // Generate action buttons for entity cards/rows
        getEntityActions(entityType, entityId) {
            return [
                {
                    label: 'Edit',
                    icon: 'edit',
                    action: () => this.editEntity(entityType, entityId),
                    class: 'text-blue-600 hover:text-blue-800'
                },
                {
                    label: 'View',
                    icon: 'eye',
                    action: () => this.viewEntity(entityType, entityId),
                    class: 'text-gray-600 hover:text-gray-800'
                }
            ];
        },

        // Bulk action buttons
        getBulkActions(entityType) {
            return [
                {
                    label: 'Delete Selected',
                    icon: 'trash',
                    action: 'bulk-delete',
                    class: 'text-red-600 hover:text-red-800',
                    requiresSelection: true
                },
                {
                    label: 'Export Selected',
                    icon: 'download',
                    action: 'bulk-export',
                    class: 'text-green-600 hover:text-green-800',
                    requiresSelection: true
                }
            ];
        },

        // Get button style classes
        getButtonClasses(button) {
            const baseClasses = 'inline-flex items-center px-4 py-2 text-sm font-medium text-white border border-transparent rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 shadow-sm';
            return `${baseClasses} ${button.color || 'bg-blue-600 hover:bg-blue-700'}`;
        },

        // Get icon classes
        getIconClasses(iconName) {
            return `w-4 h-4 mr-2 ${iconName}`;
        }
    };
};

// Initialize global button manager
document.addEventListener('DOMContentLoaded', function() {
    // Expose global button manager
    window.globalButtonManager = window.buttonManager();
});