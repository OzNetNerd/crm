/**
 * Alpine.js Template Helpers
 *
 * Replaces template_globals.py server-side template functions with client-side Alpine.js helpers.
 * Provides dynamic field options, sorting, grouping, and other template utilities.
 */
window.templateHelpers = () => {
    return {
        // Cached data to avoid repeated API calls
        fieldOptionsCache: {},
        modelConfigCache: {},

        // Get field options for dropdowns (replaces get_field_options)
        async getFieldOptions(modelName, fieldName) {
            const cacheKey = `${modelName}.${fieldName}`;

            if (this.fieldOptionsCache[cacheKey]) {
                return this.fieldOptionsCache[cacheKey];
            }

            try {
                const response = await fetch(`/api/models/${modelName}/fields/${fieldName}/options`);
                if (response.ok) {
                    const options = await response.json();
                    this.fieldOptionsCache[cacheKey] = options;
                    return options;
                }
            } catch (error) {
                console.error(`Error loading field options for ${modelName}.${fieldName}:`, error);
            }

            return [];
        },

        // Get sortable fields for a model (replaces get_sortable_fields)
        getSortableFields(modelName) {
            const commonSortableFields = {
                company: [
                    { value: 'name', label: 'Company Name' },
                    { value: 'industry', label: 'Industry' },
                    { value: 'size', label: 'Company Size' },
                    { value: 'created_at', label: 'Created Date' }
                ],
                contact: [
                    { value: 'first_name', label: 'First Name' },
                    { value: 'last_name', label: 'Last Name' },
                    { value: 'email', label: 'Email' },
                    { value: 'title', label: 'Job Title' },
                    { value: 'company_name', label: 'Company' }
                ],
                opportunity: [
                    { value: 'name', label: 'Opportunity Name' },
                    { value: 'stage', label: 'Stage' },
                    { value: 'value', label: 'Value' },
                    { value: 'close_date', label: 'Close Date' },
                    { value: 'company_name', label: 'Company' }
                ],
                task: [
                    { value: 'title', label: 'Task Title' },
                    { value: 'priority', label: 'Priority' },
                    { value: 'status', label: 'Status' },
                    { value: 'due_date', label: 'Due Date' },
                    { value: 'assigned_to', label: 'Assigned To' }
                ],
                stakeholder: [
                    { value: 'name', label: 'Name' },
                    { value: 'role', label: 'Role' },
                    { value: 'influence', label: 'Influence' },
                    { value: 'sentiment', label: 'Sentiment' }
                ]
            };

            return commonSortableFields[modelName.toLowerCase()] || [];
        },

        // Get groupable fields for a model (replaces get_groupable_fields)
        getGroupableFields(modelName) {
            const commonGroupableFields = {
                company: [
                    { value: 'industry', label: 'Industry' },
                    { value: 'size', label: 'Company Size' }
                ],
                contact: [
                    { value: 'title', label: 'Job Title' },
                    { value: 'company_name', label: 'Company' }
                ],
                opportunity: [
                    { value: 'stage', label: 'Stage' },
                    { value: 'company_name', label: 'Company' }
                ],
                task: [
                    { value: 'priority', label: 'Priority' },
                    { value: 'status', label: 'Status' },
                    { value: 'assigned_to', label: 'Assigned To' }
                ],
                stakeholder: [
                    { value: 'role', label: 'Role' },
                    { value: 'influence', label: 'Influence' },
                    { value: 'sentiment', label: 'Sentiment' }
                ]
            };

            return commonGroupableFields[modelName.toLowerCase()] || [];
        },

        // Get filter fields for a model
        getFilterFields(modelName) {
            const filterFields = {
                company: [
                    { field: 'industry', type: 'select', label: 'Industry' },
                    { field: 'size', type: 'select', label: 'Company Size' },
                    { field: 'name', type: 'text', label: 'Company Name' }
                ],
                contact: [
                    { field: 'title', type: 'text', label: 'Job Title' },
                    { field: 'company_name', type: 'select', label: 'Company' },
                    { field: 'name', type: 'text', label: 'Name' }
                ],
                opportunity: [
                    { field: 'stage', type: 'select', label: 'Stage' },
                    { field: 'company_name', type: 'select', label: 'Company' },
                    { field: 'value_range', type: 'range', label: 'Value Range' }
                ],
                task: [
                    { field: 'priority', type: 'select', label: 'Priority' },
                    { field: 'status', type: 'select', label: 'Status' },
                    { field: 'assigned_to', type: 'select', label: 'Assigned To' },
                    { field: 'due_date_range', type: 'date_range', label: 'Due Date Range' }
                ]
            };

            return filterFields[modelName.toLowerCase()] || [];
        },

        // Format values for display
        formatValue(value, type = 'text') {
            if (value === null || value === undefined || value === '') {
                return '-';
            }

            switch (type) {
                case 'date':
                    return new Date(value).toLocaleDateString();
                case 'datetime':
                    return new Date(value).toLocaleString();
                case 'currency':
                    return new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD'
                    }).format(value);
                case 'number':
                    return new Intl.NumberFormat().format(value);
                case 'boolean':
                    return value ? 'Yes' : 'No';
                case 'email':
                    return `<a href="mailto:${value}" class="text-blue-600 hover:text-blue-800">${value}</a>`;
                case 'url':
                    return `<a href="${value}" target="_blank" class="text-blue-600 hover:text-blue-800">${value}</a>`;
                default:
                    return String(value);
            }
        },

        // Get model display name (singular/plural)
        getModelDisplayName(modelName, plural = false) {
            const modelNames = {
                company: { singular: 'Company', plural: 'Companies' },
                contact: { singular: 'Contact', plural: 'Contacts' },
                opportunity: { singular: 'Opportunity', plural: 'Opportunities' },
                task: { singular: 'Task', plural: 'Tasks' },
                stakeholder: { singular: 'Stakeholder', plural: 'Stakeholders' },
                user: { singular: 'User', plural: 'Users' }
            };

            const config = modelNames[modelName.toLowerCase()];
            if (!config) {
                const formatted = modelName.charAt(0).toUpperCase() + modelName.slice(1);
                return plural ? `${formatted}s` : formatted;
            }

            return plural ? config.plural : config.singular;
        },

        // Get entity icon class
        getEntityIcon(modelName) {
            const iconMap = {
                company: 'icon-company',
                contact: 'icon-contact',
                opportunity: 'icon-opportunity',
                task: 'icon-task',
                stakeholder: 'icon-stakeholder',
                user: 'icon-user'
            };

            return iconMap[modelName.toLowerCase()] || 'icon-default';
        },

        // Get status badge classes
        getStatusBadgeClass(status, type = 'default') {
            const statusClasses = {
                // Task statuses
                pending: 'bg-yellow-100 text-yellow-800',
                in_progress: 'bg-blue-100 text-blue-800',
                completed: 'bg-green-100 text-green-800',
                cancelled: 'bg-red-100 text-red-800',

                // Opportunity stages
                prospecting: 'bg-gray-100 text-gray-800',
                qualification: 'bg-blue-100 text-blue-800',
                proposal: 'bg-purple-100 text-purple-800',
                negotiation: 'bg-orange-100 text-orange-800',
                closed_won: 'bg-green-100 text-green-800',
                closed_lost: 'bg-red-100 text-red-800',

                // Priority levels
                low: 'bg-gray-100 text-gray-800',
                medium: 'bg-yellow-100 text-yellow-800',
                high: 'bg-orange-100 text-orange-800',
                urgent: 'bg-red-100 text-red-800'
            };

            return statusClasses[status] || 'bg-gray-100 text-gray-800';
        },

        // Generate empty state message
        getEmptyStateMessage(modelName, context = 'list') {
            const messages = {
                list: {
                    company: 'No companies found. Create your first company to get started.',
                    contact: 'No contacts found. Add contacts to manage your relationships.',
                    opportunity: 'No opportunities found. Create opportunities to track your sales pipeline.',
                    task: 'No tasks found. Add tasks to organize your work.',
                    stakeholder: 'No stakeholders found. Add stakeholders to track key relationships.'
                },
                search: {
                    company: 'No companies match your search criteria.',
                    contact: 'No contacts match your search criteria.',
                    opportunity: 'No opportunities match your search criteria.',
                    task: 'No tasks match your search criteria.',
                    stakeholder: 'No stakeholders match your search criteria.'
                }
            };

            const contextMessages = messages[context] || messages.list;
            return contextMessages[modelName.toLowerCase()] || 'No items found.';
        },

        // Initialize helpers (load any required data)
        async init() {
            // Pre-load commonly used field options
            const commonFields = [
                { model: 'company', field: 'industry' },
                { model: 'company', field: 'size' },
                { model: 'task', field: 'priority' },
                { model: 'task', field: 'status' },
                { model: 'opportunity', field: 'stage' }
            ];

            for (const { model, field } of commonFields) {
                await this.getFieldOptions(model, field);
            }
        }
    };
};

// Global helper instance
document.addEventListener('DOMContentLoaded', function() {
    window.globalTemplateHelpers = window.templateHelpers();
    window.globalTemplateHelpers.init();
});