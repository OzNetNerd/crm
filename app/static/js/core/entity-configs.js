/**
 * Entity Configurations for the Generic Entity Manager System
 * Defines specific configurations for each entity type (Tasks, Opportunities, etc.)
 * Uses centralized icon utility for consistent icon management
 */

// Icons are handled server-side via Jinja2 templates for DRY architecture

/**
 * Opportunity Configuration
 * Used with createEntityManager() to handle opportunities
 */
function getOpportunityConfig(today) {
    return {
        // Data source
        entityName: 'opportunity',
        dataSource: 'opportunitiesData',
        contentContainerId: 'opportunities-content',
        
        // Default states
        defaultGroupBy: 'stage',
        defaultSortBy: 'close_date',
        defaultSortDirection: 'asc',
        defaultShowCompleted: false,
        defaultPrimaryFilter: [], // Priority filter (value-based)
        defaultSecondaryFilter: [], // Stage filter  
        defaultEntityFilter: [], // Company filter
        today: today,
        persistState: true,

        // Field mappings
        primaryFilterField: 'calculated_priority', // Will be calculated from value
        secondaryFilterField: 'stage',
        entityFilterField: 'company_name',
        
        // Completion logic
        isCompleted: (opportunity) => ['closed-won', 'closed-lost'].includes(opportunity.stage),

        // Priority calculation based on deal value
        priorityLogic: (opportunity) => {
            if (!opportunity.value) return 'low';
            if (opportunity.value >= 50000) return 'high';
            if (opportunity.value >= 10000) return 'medium';
            return 'low';
        },

        // Grouping options
        groupOptions: {
            'stage': {
                field: 'stage',
                groups: [
                    { 
                        key: 'prospect', 
                        title: 'Prospect', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: ''
                    },
                    { 
                        key: 'qualified', 
                        title: 'Qualified', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: ''
                    },
                    { 
                        key: 'proposal', 
                        title: 'Proposal', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: ''
                    },
                    { 
                        key: 'negotiation', 
                        title: 'Negotiation', 
                        containerClass: 'card-orange', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-orange-200 px-6 py-4 bg-orange-50 hover:bg-orange-100', 
                        badgeClass: 'badge-orange',
                        icon: ''                    }
                ]
            },
            'close_date': {
                field: 'expected_close_date',
                groups: [
                    { 
                        key: 'overdue', 
                        title: 'Overdue', 
                        containerClass: 'card-danger', 
                        headerClass: 'text-status-overdue', 
                        headerBgClass: 'border-b border-red-200 px-6 py-4 bg-red-50 hover:bg-red-100', 
                        badgeClass: 'badge-red',
                        icon: ''                    },
                    { 
                        key: 'this_week', 
                        title: 'This Week', 
                        containerClass: 'card-orange', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-orange-200 px-6 py-4 bg-orange-50 hover:bg-orange-100', 
                        badgeClass: 'badge-orange',
                        icon: ''                    },
                    { 
                        key: 'this_month', 
                        title: 'This Month', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: ''                    },
                    { 
                        key: 'later', 
                        title: 'Later', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: ''                    },
                    { 
                        key: 'no_date', 
                        title: 'No Close Date', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: ''                    }
                ],
                filterFn: (opportunity, groupKey) => {
                    const today = new Date();
                    const closeDate = opportunity.expected_close_date ? new Date(opportunity.expected_close_date) : null;
                    
                    if (groupKey === 'no_date') return !closeDate;
                    if (!closeDate) return false;
                    
                    const daysDiff = Math.ceil((closeDate - today) / (1000 * 60 * 60 * 24));
                    
                    switch(groupKey) {
                        case 'overdue': return daysDiff < 0;
                        case 'this_week': return daysDiff >= 0 && daysDiff <= 7;
                        case 'this_month': return daysDiff > 7 && daysDiff <= 30;
                        case 'later': return daysDiff > 30;
                        default: return false;
                    }
                }
            },
            'value': {
                field: 'value',
                groups: [
                    { 
                        key: 'high', 
                        title: 'High Value ($50K+)', 
                        containerClass: 'card-danger', 
                        headerClass: 'text-status-overdue', 
                        headerBgClass: 'border-b border-red-200 px-6 py-4 bg-red-50 hover:bg-red-100', 
                        badgeClass: 'badge-red',
                        icon: ''                    },
                    { 
                        key: 'medium', 
                        title: 'Medium Value ($10K-$50K)', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: ''                    },
                    { 
                        key: 'low', 
                        title: 'Low Value (<$10K)', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: ''                    }
                ],
                filterFn: (opportunity, groupKey) => {
                    const value = opportunity.value || 0;
                    switch(groupKey) {
                        case 'high': return value >= 50000;
                        case 'medium': return value >= 10000 && value < 50000;
                        case 'low': return value < 10000;
                        default: return false;
                    }
                }
            },
            'company': {
                field: 'company_name',
                groups: [] // Will be populated dynamically from data
            }
        },

        // Sorting options
        sortOptions: {
            'close_date': {
                label: 'Close Date',
                compareFn: (a, b) => {
                    if (!a.expected_close_date && !b.expected_close_date) return 0;
                    if (!a.expected_close_date) return 1;
                    if (!b.expected_close_date) return -1;
                    return new Date(a.expected_close_date) - new Date(b.expected_close_date);
                }
            },
            'value': {
                label: 'Deal Value',
                compareFn: (a, b) => (a.value || 0) - (b.value || 0)
            },
            'created_at': {
                label: 'Created Date',
                compareFn: (a, b) => new Date(a.created_at) - new Date(b.created_at)
            },
            'name': {
                label: 'Name',
                compareFn: (a, b) => (a.name || '').localeCompare(b.name || '')
            },
            'stage': {
                label: 'Stage',
                compareFn: (a, b) => {
                    const stageOrder = { 'prospect': 1, 'qualified': 2, 'proposal': 3, 'negotiation': 4 };
                    return (stageOrder[a.stage] || 5) - (stageOrder[b.stage] || 5);
                }
            }
        },

        // Filter options
        primaryFilterOptions: [
            { value: 'high', label: 'High ($50K+)' },
            { value: 'medium', label: 'Medium ($10K-$50K)' },
            { value: 'low', label: 'Low (<$10K)' }
        ],
        primaryFilterLabel: 'All Priorities',

        secondaryFilterOptions: [
            { value: 'prospect', label: 'Prospect' },
            { value: 'qualified', label: 'Qualified' },
            { value: 'proposal', label: 'Proposal' },
            { value: 'negotiation', label: 'Negotiation' }
        ],
        secondaryFilterLabel: 'All Stages',

        entityFilterOptions: [
            // Will be populated dynamically from company data
        ],
        entityFilterLabel: 'All Companies',

        // Default expanded sections
        defaultExpandedSections: {
            'prospect': true,
            'qualified': true,
            'proposal': true,
            'negotiation': true,
            'overdue': true,
            'this_week': true,
            'this_month': true,
            'later': true,
            'no_date': true,
            'high': true,
            'medium': true,
            'low': true
        },

        // Action mappings
        actions: {
            'Delete opportunity': 'deleteOpportunity',
            'View opportunity': 'openOpportunityModal',
            'Edit opportunity': 'editOpportunity'
        },

        // Bulk actions
        bulkActions: {
            'updateStage': (selectedIds) => window.bulkUpdateOpportunityStage(selectedIds),
            'delete': (selectedIds) => window.bulkDeleteOpportunities(selectedIds)
        }
    };
}

/**
 * Task Configuration
 * Used with createEntityManager() to handle tasks
 */
function getTaskConfig(today) {
    return {
        // Data source
        entityName: 'task',
        dataSource: 'tasksData',
        contentContainerId: 'tasks-content',
        
        // Default states
        defaultGroupBy: 'status',
        defaultSortBy: 'due_date',
        defaultSortDirection: 'asc',
        defaultShowCompleted: false,
        defaultPrimaryFilter: [], // Priority filter
        defaultSecondaryFilter: [], // Status filter  
        defaultEntityFilter: [], // Entity filter
        today: today,
        persistState: true,

        // Field mappings
        primaryFilterField: 'priority',
        secondaryFilterField: 'status',
        entityFilterField: 'entity_type',
        
        // Completion logic
        isCompleted: (task) => task.status === 'complete',

        // Grouping options
        groupOptions: {
            'status': {
                field: 'status',
                groups: [
                    { 
                        key: 'todo', 
                        title: 'To Do', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: ''                    },
                    { 
                        key: 'in-progress', 
                        title: 'In Progress', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: ''                    },
                    { 
                        key: 'complete', 
                        title: 'Completed', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: ''                    }
                ]
            },
            'priority': {
                field: 'priority',
                groups: [
                    { 
                        key: 'high', 
                        title: 'High Priority', 
                        containerClass: 'card-danger', 
                        headerClass: 'text-status-overdue', 
                        headerBgClass: 'border-b border-red-200 px-6 py-4 bg-red-50 hover:bg-red-100', 
                        badgeClass: 'badge-red',
                        icon: ''                    },
                    { 
                        key: 'medium', 
                        title: 'Medium Priority', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: ''                    },
                    { 
                        key: 'low', 
                        title: 'Low Priority', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: ''                    }
                ]
            },
            'due_date': {
                field: 'due_date',
                groups: [
                    { 
                        key: 'overdue', 
                        title: 'Overdue', 
                        containerClass: 'card-danger', 
                        headerClass: 'text-status-overdue', 
                        headerBgClass: 'border-b border-red-200 px-6 py-4 bg-red-50 hover:bg-red-100', 
                        badgeClass: 'badge-red',
                        icon: ''                    },
                    { 
                        key: 'today', 
                        title: 'Due Today', 
                        containerClass: 'card-orange', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-orange-200 px-6 py-4 bg-orange-50 hover:bg-orange-100', 
                        badgeClass: 'badge-orange',
                        icon: ''                    },
                    { 
                        key: 'this_week', 
                        title: 'This Week', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: ''                    },
                    { 
                        key: 'later', 
                        title: 'Later', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: ''                    },
                    { 
                        key: 'no_date', 
                        title: 'No Due Date', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: ''                    }
                ],
                filterFn: (task, groupKey) => {
                    if (task.task_type === 'child') return false;
                    if (!task.due_date && groupKey === 'no_date') return true;
                    if (!task.due_date) return false;
                    
                    const today = new Date();
                    const dueDate = new Date(task.due_date);
                    const daysDiff = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
                    
                    switch(groupKey) {
                        case 'overdue': return daysDiff < 0;
                        case 'today': return daysDiff === 0;
                        case 'this_week': return daysDiff > 0 && daysDiff <= 7;
                        case 'later': return daysDiff > 7;
                        case 'no_date': return false; // Already handled above
                        default: return false;
                    }
                }
            },
            'entity': {
                field: 'entity_type',
                groups: [
                    { 
                        key: 'company', 
                        title: 'Company Tasks', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: ''                    },
                    { 
                        key: 'contact', 
                        title: 'Stakeholder Tasks', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: ''                    },
                    { 
                        key: 'opportunity', 
                        title: 'Opportunity Tasks', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: ''                    },
                    { 
                        key: 'unrelated', 
                        title: 'General Tasks', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: ''                    }
                ],
                filterFn: (task, groupKey) => {
                    if (task.task_type === 'child') return false;
                    if (groupKey === 'unrelated') {
                        return !task.entity_type || task.entity_type === null;
                    }
                    return task.entity_type === groupKey;
                }
            }
        },

        // Sorting options
        sortOptions: {
            'due_date': {
                label: 'Due Date',
                compareFn: (a, b) => {
                    if (!a.due_date && !b.due_date) return 0;
                    if (!a.due_date) return 1;
                    if (!b.due_date) return -1;
                    return new Date(a.due_date) - new Date(b.due_date);
                }
            },
            'priority': {
                label: 'Priority',
                compareFn: (a, b) => {
                    const priorityOrder = {'high': 3, 'medium': 2, 'low': 1};
                    return (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
                }
            },
            'created_at': {
                label: 'Created Date',
                compareFn: (a, b) => new Date(b.created_at) - new Date(a.created_at)
            },
            'title': {
                label: 'Title',
                compareFn: (a, b) => (a.title || '').localeCompare(b.title || '')
            },
            'status': {
                label: 'Status',
                compareFn: (a, b) => (a.status || '').localeCompare(b.status || '')
            }
        },

        // Filter options
        primaryFilterOptions: [
            { value: 'high', label: 'High' },
            { value: 'medium', label: 'Medium' },
            { value: 'low', label: 'Low' }
        ],
        primaryFilterLabel: 'All Priorities',

        secondaryFilterOptions: [
            { value: 'todo', label: 'To Do' },
            { value: 'in-progress', label: 'In Progress' },
            { value: 'complete', label: 'Complete' }
        ],
        secondaryFilterLabel: 'All Statuses',

        entityFilterOptions: [
            { value: 'company', label: 'Company' },
            { value: 'contact', label: 'Stakeholder' },
            { value: 'opportunity', label: 'Opportunity' },
            { value: 'unrelated', label: 'General' }
        ],
        entityFilterLabel: 'All Entities',

        // Default expanded sections
        defaultExpandedSections: {
            'todo': true,
            'in-progress': true,
            'complete': true,
            'high': true,
            'medium': true,
            'low': true,
            'overdue': true,
            'today': true,
            'this_week': true,
            'later': true,
            'no_date': true,
            'company': true,
            'contact': true,
            'opportunity': true,
            'unrelated': true
        },



        // Bulk action mappings
        bulkActions: {
            'update': (selectedIds) => window.bulkUpdateTaskStatus(selectedIds),
            'delete': (selectedIds) => window.bulkDeleteTasks(selectedIds)
        }
    };
}

/**
 * Stakeholder Configuration
 * Used with createEntityManager() to handle contacts
 */
function getStakeholderConfig(today) {
    return {
        // Data source
        entityName: 'stakeholder',
        dataSource: 'stakeholdersData',
        contentContainerId: 'stakeholders-content',
        
        // Default states
        defaultGroupBy: 'company',
        defaultSortBy: 'name',
        defaultSortDirection: 'asc',
        defaultShowCompleted: false,
        defaultPrimaryFilter: [], // Stakeholder info filter
        defaultSecondaryFilter: [], // Industry filter
        defaultEntityFilter: [], // Role filter
        today: today,
        persistState: true,

        // Field mappings
        primaryFilterField: 'contact_info_status', // Will be calculated
        secondaryFilterField: 'company.industry',
        entityFilterField: 'job_title',
        
        // Completion logic (not applicable for contacts)
        isCompleted: (contact) => false,

        // Override primary filter value getter to calculate contact info status
        getPrimaryFilterValue: function(contact) {
            const hasEmail = !!contact.email;
            const hasPhone = !!contact.phone;
            if (hasEmail && hasPhone) return 'complete';
            if (hasEmail) return 'email_only';
            if (hasPhone) return 'phone_only';
            return 'missing';
        },

        // Override secondary filter value getter for industry
        getSecondaryFilterValue: function(contact) {
            return (contact.company?.industry || 'unknown').toLowerCase();
        },

        // Override entity filter value getter for roles
        getEntityFilterValue: function(contact) {
            return contact.job_title || 'no_job_title';
        },

        // Grouping options
        groupOptions: {
            'company': {
                field: 'company_name',
                groups: [], // Will be populated dynamically from data
                isDynamic: true,
                generateGroups: function(entities) {
                    // Get unique companies from contacts data
                    const companies = new Set();
                    entities.forEach(contact => {
                        if (contact.company_name) {
                            companies.add(contact.company_name);
                        }
                    });
                    
                    const sortedCompanies = Array.from(companies).sort();
                    
                    // Use the color scheme manager for consistent, varied colors
                    return sortedCompanies.map((companyName, index) => {
                        if (!window.colorSchemeManager) {
                            throw new Error('colorSchemeManager is not available. Ensure it is loaded before using entity configs.');
                        }
                        const colorScheme = window.colorSchemeManager.getColorScheme(companyName, 'company');
                            
                        return {
                            key: companyName,
                            title: companyName,
                            containerClass: colorScheme.containerClass,
                            headerClass: colorScheme.headerClass,
                            headerBgClass: colorScheme.headerBgClass,
                            badgeClass: colorScheme.badgeClass,
                            icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>'
                        };
                    });
                },
                filterFn: (contact, groupKey) => {
                    return contact.company_name === groupKey;
                }
            },
            'industry': {
                field: 'company.industry',
                groups: [
                    { 
                        key: 'technology', 
                        title: 'Technology', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>'
                    },
                    { 
                        key: 'finance', 
                        title: 'Finance', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    },
                    { 
                        key: 'healthcare', 
                        title: 'Healthcare', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>'
                    },
                    { 
                        key: 'manufacturing', 
                        title: 'Manufacturing', 
                        containerClass: 'card-orange', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-orange-200 px-6 py-4 bg-orange-50 hover:bg-orange-100', 
                        badgeClass: 'badge-orange',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>'
                    },
                    { 
                        key: 'unknown', 
                        title: 'Unknown Industry', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    }
                ],
                filterFn: (contact, groupKey) => {
                    const industry = contact.company?.industry || 'unknown';
                    return industry === groupKey;
                }
            },
            'job_title': {
                field: 'job_title',
                groups: [
                    { 
                        key: 'ceo', 
                        title: 'CEO', 
                        containerClass: 'card-danger', 
                        headerClass: 'text-status-overdue', 
                        headerBgClass: 'border-b border-red-200 px-6 py-4 bg-red-50 hover:bg-red-100', 
                        badgeClass: 'badge-red',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path></svg>'
                    },
                    { 
                        key: 'manager', 
                        title: 'Manager', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>'
                    },
                    { 
                        key: 'director', 
                        title: 'Director', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>'
                    },
                    { 
                        key: 'developer', 
                        title: 'Developer', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>'
                    },
                    { 
                        key: 'no_job_title', 
                        title: 'No Job Title Specified', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    }
                ],
                filterFn: (contact, groupKey) => {
                    if (groupKey === 'no_job_title') return !contact.job_title;
                    return contact.job_title === groupKey;
                }
            },
            'contact_info': {
                field: 'contact_info_status',
                groups: [
                    { 
                        key: 'complete', 
                        title: 'Complete Info (Email + Phone)', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd"></path></svg>'
                    },
                    { 
                        key: 'email_only', 
                        title: 'Email Only', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>'
                    },
                    { 
                        key: 'phone_only', 
                        title: 'Phone Only', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>'
                    },
                    { 
                        key: 'missing', 
                        title: 'Missing Stakeholder Info', 
                        containerClass: 'card-danger', 
                        headerClass: 'text-status-overdue', 
                        headerBgClass: 'border-b border-red-200 px-6 py-4 bg-red-50 hover:bg-red-100', 
                        badgeClass: 'badge-red',
                        icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clip-rule="evenodd"></path></svg>'
                    }
                ],
                filterFn: (contact, groupKey) => {
                    const hasEmail = !!contact.email;
                    const hasPhone = !!contact.phone;
                    
                    switch(groupKey) {
                        case 'complete': return hasEmail && hasPhone;
                        case 'email_only': return hasEmail && !hasPhone;
                        case 'phone_only': return !hasEmail && hasPhone;
                        case 'missing': return !hasEmail && !hasPhone;
                        default: return false;
                    }
                }
            }
        },

        // Sorting options
        sortOptions: {
            'name': {
                label: 'Name',
                compareFn: (a, b) => (a.name || '').localeCompare(b.name || '')
            },
            'company': {
                label: 'Company',
                compareFn: (a, b) => {
                    const companyA = a.company?.name || '';
                    const companyB = b.company?.name || '';
                    return companyA.localeCompare(companyB);
                }
            },
            'email': {
                label: 'Email',
                compareFn: (a, b) => (a.email || '').localeCompare(b.email || '')
            },
            'phone': {
                label: 'Phone',
                compareFn: (a, b) => (a.phone || '').localeCompare(b.phone || '')
            },
            'job_title': {
                label: 'Job Title',
                compareFn: (a, b) => (a.job_title || '').localeCompare(b.job_title || '')
            }
        },

        // Filter options
        primaryFilterOptions: [
            { value: 'complete', label: 'Complete Info' },
            { value: 'email_only', label: 'Email Only' },
            { value: 'phone_only', label: 'Phone Only' },
            { value: 'missing', label: 'Missing Info' }
        ],
        primaryFilterLabel: 'All Stakeholder Info',

        secondaryFilterOptions: [
            { value: 'technology', label: 'Technology' },
            { value: 'finance', label: 'Finance' },
            { value: 'healthcare', label: 'Healthcare' },
            { value: 'manufacturing', label: 'Manufacturing' }
        ],
        secondaryFilterLabel: 'All Industries',

        entityFilterOptions: [
            { value: 'ceo', label: 'CEO' },
            { value: 'manager', label: 'Manager' },
            { value: 'director', label: 'Director' },
            { value: 'developer', label: 'Developer' }
        ],
        entityFilterLabel: 'All Job Titles',

        // Default expanded sections
        defaultExpandedSections: {
            // Company grouping
            'complete': true,
            'email_only': true,
            'phone_only': true,
            'missing': true,
            // Industry grouping  
            'technology': true,
            'finance': true,
            'healthcare': true,
            'manufacturing': true,
            'unknown': true,
            // Job Title grouping
            'ceo': true,
            'manager': true,
            'director': true,
            'developer': true,
            'no_job_title': true
        },

        // Action mappings
        actions: {
            'View contact': 'openStakeholderModal',
            'Edit contact': 'editStakeholder',
            'Delete contact': 'deleteStakeholder',
            'Create task': 'createTaskForStakeholder',
            'Create opportunity': 'createOpportunityForStakeholder'
        },

        // Bulk actions
        bulkActions: {
            'delete': (selectedIds) => window.bulkDeleteStakeholders(selectedIds),
            'createTasks': (selectedIds) => window.bulkCreateTasksForStakeholders(selectedIds)
        }
    };
}

/**
 * Company Configuration
 * Used with createEntityManager() to handle companies
 */
function getCompanyConfig(today) {
    return {
        // Data source
        entityName: 'company',
        dataSource: 'companiesData',
        contentContainerId: 'companies-content',
        
        // Default states
        defaultGroupBy: 'industry',
        defaultSortBy: 'name',
        defaultSortDirection: 'asc',
        defaultShowCompleted: false,
        defaultPrimaryFilter: [], // Company info filter
        defaultSecondaryFilter: [], // Industry filter
        defaultEntityFilter: [], // Size filter
        today: today,
        persistState: true,

        // Field mappings
        primaryFilterField: 'company_info_status', // Will be calculated
        secondaryFilterField: 'industry',
        entityFilterField: 'size_category', // Will be calculated
        
        // Completion logic (not applicable for companies)
        isCompleted: (company) => false,

        // Override primary filter value getter to calculate company info status
        getPrimaryFilterValue: function(company) {
            const hasIndustry = !!company.industry;
            const hasWebsite = !!company.website;
            const hasStakeholders = company.contacts && company.contacts.length > 0;
            
            if (hasIndustry && hasWebsite && hasStakeholders) return 'has_industry';
            if (hasWebsite) return 'has_website';
            if (hasStakeholders) return 'has_contacts';
            return 'missing_info';
        },

        // Override secondary filter value getter for industry
        getSecondaryFilterValue: function(company) {
            return (company.industry || 'unknown').toLowerCase();
        },

        // Override entity filter value getter for company size
        getEntityFilterValue: function(company) {
            const contactCount = company.contacts ? company.contacts.length : 0;
            if (contactCount === 0) return 'unknown';
            if (contactCount <= 10) return 'small';
            if (contactCount <= 50) return 'medium';
            return 'large';
        },

        // Grouping options
        groupOptions: {
            'industry': {
                field: 'industry',
                groups: [
                    { 
                        key: 'technology', 
                        title: 'Technology', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>'
                    },
                    { 
                        key: 'finance', 
                        title: 'Finance', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    },
                    { 
                        key: 'healthcare', 
                        title: 'Healthcare', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>'
                    },
                    { 
                        key: 'manufacturing', 
                        title: 'Manufacturing', 
                        containerClass: 'card-orange', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-orange-200 px-6 py-4 bg-orange-50 hover:bg-orange-100', 
                        badgeClass: 'badge-orange',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>'
                    },
                    { 
                        key: 'retail', 
                        title: 'Retail', 
                        containerClass: 'card-purple', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-purple-200 px-6 py-4 bg-purple-50 hover:bg-purple-100', 
                        badgeClass: 'badge-purple',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path></svg>'
                    },
                    { 
                        key: 'consulting', 
                        title: 'Consulting', 
                        containerClass: 'card-indigo', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-indigo-200 px-6 py-4 bg-indigo-50 hover:bg-indigo-100', 
                        badgeClass: 'badge-indigo',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>'
                    },
                    { 
                        key: 'unknown', 
                        title: 'Unknown Industry', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    }
                ],
                filterFn: (company, groupKey) => {
                    const industry = (company.industry || 'unknown').toLowerCase();
                    return industry === groupKey;
                }
            },
            'size': {
                field: 'size_category',
                groups: [
                    { 
                        key: 'large', 
                        title: 'Large Companies (50+ contacts)', 
                        containerClass: 'card-danger', 
                        headerClass: 'text-status-overdue', 
                        headerBgClass: 'border-b border-red-200 px-6 py-4 bg-red-50 hover:bg-red-100', 
                        badgeClass: 'badge-red',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>'
                    },
                    { 
                        key: 'medium', 
                        title: 'Medium Companies (11-50 contacts)', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>'
                    },
                    { 
                        key: 'small', 
                        title: 'Small Companies (1-10 contacts)', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>'
                    },
                    { 
                        key: 'unknown', 
                        title: 'No Stakeholders', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    }
                ],
                filterFn: (company, groupKey) => {
                    const contactCount = company.contacts ? company.contacts.length : 0;
                    switch(groupKey) {
                        case 'large': return contactCount > 50;
                        case 'medium': return contactCount >= 11 && contactCount <= 50;
                        case 'small': return contactCount >= 1 && contactCount <= 10;
                        case 'unknown': return contactCount === 0;
                        default: return false;
                    }
                }
            },
            'contacts': {
                field: 'contacts_count',
                groups: [
                    { 
                        key: 'many', 
                        title: 'Many Stakeholders (20+)', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>'
                    },
                    { 
                        key: 'few', 
                        title: 'Few Stakeholders (1-19)', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>'
                    },
                    { 
                        key: 'none', 
                        title: 'No Stakeholders', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path></svg>'
                    }
                ],
                filterFn: (company, groupKey) => {
                    const contactCount = company.contacts ? company.contacts.length : 0;
                    switch(groupKey) {
                        case 'many': return contactCount >= 20;
                        case 'few': return contactCount >= 1 && contactCount < 20;
                        case 'none': return contactCount === 0;
                        default: return false;
                    }
                }
            },
            'opportunities': {
                field: 'opportunities_count',
                groups: [
                    { 
                        key: 'active', 
                        title: 'Active Opportunities', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>'
                    },
                    { 
                        key: 'none', 
                        title: 'No Opportunities', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path></svg>'
                    }
                ],
                filterFn: (company, groupKey) => {
                    const oppCount = company.opportunities ? company.opportunities.length : 0;
                    switch(groupKey) {
                        case 'active': return oppCount > 0;
                        case 'none': return oppCount === 0;
                        default: return false;
                    }
                }
            }
        },

        // Sorting options
        sortOptions: {
            'name': {
                label: 'Name',
                compareFn: (a, b) => (a.name || '').localeCompare(b.name || '')
            },
            'industry': {
                label: 'Industry',
                compareFn: (a, b) => (a.industry || '').localeCompare(b.industry || '')
            },
            'contacts_count': {
                label: 'Stakeholder Count',
                compareFn: (a, b) => {
                    const contactsA = a.contacts ? a.contacts.length : 0;
                    const contactsB = b.contacts ? b.contacts.length : 0;
                    return contactsB - contactsA;
                }
            },
            'opportunities_count': {
                label: 'Opportunity Count',
                compareFn: (a, b) => {
                    const oppA = a.opportunities ? a.opportunities.length : 0;
                    const oppB = b.opportunities ? b.opportunities.length : 0;
                    return oppB - oppA;
                }
            },
            'created_at': {
                label: 'Date Added',
                compareFn: (a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0)
            }
        },

        // Filter options
        primaryFilterOptions: [
            { value: 'has_industry', label: 'Has Industry' },
            { value: 'has_website', label: 'Has Website' },
            { value: 'has_contacts', label: 'Has Stakeholders' },
            { value: 'missing_info', label: 'Missing Info' }
        ],
        primaryFilterLabel: 'All Company Info',

        secondaryFilterOptions: [
            { value: 'technology', label: 'Technology' },
            { value: 'finance', label: 'Finance' },
            { value: 'healthcare', label: 'Healthcare' },
            { value: 'manufacturing', label: 'Manufacturing' },
            { value: 'retail', label: 'Retail' },
            { value: 'consulting', label: 'Consulting' }
        ],
        secondaryFilterLabel: 'All Industries',

        entityFilterOptions: [
            { value: 'small', label: 'Small (1-50)' },
            { value: 'medium', label: 'Medium (51-500)' },
            { value: 'large', label: 'Large (500+)' },
            { value: 'unknown', label: 'Unknown Size' }
        ],
        entityFilterLabel: 'All Sizes',

        // Default expanded sections
        defaultExpandedSections: {
            // Industry grouping
            'technology': true,
            'finance': true,
            'healthcare': true,
            'manufacturing': true,
            'retail': true,
            'consulting': true,
            'unknown': true,
            // Size grouping
            'large': true,
            'medium': true,
            'small': true,
            // Stakeholder count grouping
            'many': true,
            'few': true,
            'none': true,
            // Opportunity grouping
            'active': true
        },


        // Action mappings
        actions: {
            'View company': 'openCompanyModal',
            'Edit company': 'editCompany',
            'Delete company': 'deleteCompany',
            'Create task': 'createTaskForCompany',
            'Create contact': 'createStakeholderForCompany',
            'Create opportunity': 'createOpportunityForCompany'
        },

        // Bulk actions
        bulkActions: {
            'delete': (selectedIds) => window.bulkDeleteCompanies(selectedIds),
            'createTasks': (selectedIds) => window.bulkCreateTasksForCompanies(selectedIds)
        }
    };
}

/**
 * Team Configuration
 * Used with createEntityManager() to handle account team members
 */
function getTeamConfig(today) {
    return {
        // Data source
        entityName: 'team',
        dataSource: 'teamData',
        contentContainerId: 'teams-content',
        
        // Default states
        defaultGroupBy: 'job_title',
        defaultSortBy: 'name',
        defaultSortDirection: 'asc',
        defaultShowCompleted: false,
        defaultPrimaryFilter: [], // Assignment status filter
        defaultSecondaryFilter: [], // Job title filter  
        defaultEntityFilter: [], // Assignment count filter
        today: today,
        persistState: true,

        // Field mappings
        primaryFilterField: 'assignment_status', // Will be calculated from assignments
        secondaryFilterField: 'job_title',
        entityFilterField: 'assignment_count',
        
        // Completion logic (for "show unassigned only" functionality)
        // Note: In this context, "completed" means "unassigned" (no assignments)
        isCompleted: (member) => {
            const totalAssignments = (member.company_assignments?.length || 0) + (member.opportunity_assignments?.length || 0);
            return totalAssignments === 0; // "completed" = unassigned (no assignments)
        },

        // Priority calculation based on assignment count
        priorityLogic: (member) => {
            const totalAssignments = (member.company_assignments?.length || 0) + (member.opportunity_assignments?.length || 0);
            if (totalAssignments === 0) return 'unassigned';
            if (totalAssignments >= 5) return 'assigned';
            return 'assigned';
        },

        // Grouping configurations
        groupOptions: {
            'job_title': {
                field: 'job_title',
                groups: [
                    { key: 'Account Manager', title: 'Account Manager', color: 'blue', expanded: true, 
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>' },
                    { key: 'Sales Representative', title: 'Sales Representative', color: 'green', expanded: true,
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>' },
                    { key: 'Solutions Engineer', title: 'Solutions Engineer', color: 'purple', expanded: true,
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>' },
                    { key: 'Technical Architect', title: 'Technical Architect', color: 'orange', expanded: true,
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>' },
                    { key: 'Customer Success Manager', title: 'Customer Success Manager', color: 'teal', expanded: true,
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>' },
                    { key: 'Sales Engineer', title: 'Sales Engineer', color: 'indigo', expanded: true,
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>' },
                    { key: 'Account Executive', title: 'Account Executive', color: 'pink', expanded: true,
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>' },
                    { key: 'Implementation Specialist', title: 'Implementation Specialist', color: 'yellow', expanded: true,
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100-4m0 4v2m0-6V4"></path></svg>' },
                    { key: 'Support Manager', title: 'Support Manager', color: 'red', expanded: true,
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>' },
                    { key: 'Business Development Rep', title: 'Business Development Rep', color: 'gray', expanded: true,
                      icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>' }
                ]
            },
            'name': {
                field: 'name',
                groups: [], // Will be populated dynamically
                isDynamic: true,
                generateGroups: function(entities) {
                    const letters = [...new Set(entities.map(member => 
                        (member.name?.charAt(0)?.toUpperCase() || 'Unknown')
                    ))].sort();
                    return letters.map(letter => ({ 
                        key: letter, 
                        title: `${letter}*`, 
                        color: 'blue',
                        expanded: true 
                    }));
                },
                filterFn: (entity, groupKey) => {
                    const firstLetter = entity.name?.charAt(0)?.toUpperCase() || 'Unknown';
                    return firstLetter === groupKey;
                }
            },
            'assignment_count': {
                field: 'assignment_count',
                groups: [
                    { key: 'unassigned', title: 'Unassigned', color: 'red', expanded: true },
                    { key: 'light_workload', title: 'Light Workload (1)', color: 'yellow', expanded: true },
                    { key: 'medium_workload', title: 'Medium Workload (2-4)', color: 'blue', expanded: true },
                    { key: 'high_workload', title: 'High Workload (5+)', color: 'green', expanded: true }
                ],
                filterFn: (entity, groupKey) => {
                    const total = (entity.company_assignments?.length || 0) + (entity.opportunity_assignments?.length || 0);
                    switch(groupKey) {
                        case 'unassigned': return total === 0;
                        case 'light_workload': return total === 1;
                        case 'medium_workload': return total >= 2 && total <= 4;
                        case 'high_workload': return total >= 5;
                        default: return false;
                    }
                }
            }
        },

        // Sorting configurations
        sortOptions: {
            'name': {
                label: 'Name',
                sortFn: (a, b) => (a.name || '').localeCompare(b.name || '')
            },
            'job_title': {
                label: 'Job Title', 
                sortFn: (a, b) => (a.job_title || '').localeCompare(b.job_title || '')
            },
            'email': {
                label: 'Email',
                sortFn: (a, b) => (a.email || '').localeCompare(b.email || '')
            },
            'assignment_count': {
                label: 'Assignment Count',
                sortFn: (a, b) => {
                    const aCount = (a.company_assignments?.length || 0) + (a.opportunity_assignments?.length || 0);
                    const bCount = (b.company_assignments?.length || 0) + (b.opportunity_assignments?.length || 0);
                    return bCount - aCount; // Descending by default
                }
            }
        },

        // Filter configurations
        primaryFilterOptions: [
            { value: 'all', label: 'All Members' },
            { value: 'assigned', label: 'Assigned Members' },
            { value: 'unassigned', label: 'Unassigned Members' }
        ],
        primaryFilterLabel: 'All Members',

        secondaryFilterOptions: [
            { value: 'Account Manager', label: 'Account Manager' },
            { value: 'Sales Representative', label: 'Sales Representative' },
            { value: 'Technical Consultant', label: 'Technical Consultant' },
            { value: 'Customer Success Manager', label: 'Customer Success Manager' },
            { value: 'Business Development Manager', label: 'Business Development Manager' }
        ],
        secondaryFilterLabel: 'All Roles',

        entityFilterOptions: [
            { value: 'high_workload', label: 'High Workload (5+)' },
            { value: 'medium_workload', label: 'Medium Workload (2-4)' },
            { value: 'light_workload', label: 'Light Workload (1)' },
            { value: 'unassigned', label: 'Unassigned' }
        ],
        entityFilterLabel: 'All Workloads',

        // Default expanded sections
        defaultExpandedSections: {
            // Job title grouping
            'Account Manager': true,
            'Sales Representative': true,
            'Technical Consultant': true,
            'Customer Success Manager': true,
            'Business Development Manager': true,
            'Unknown Role': true,
            // Assignment count grouping
            'High Workload (5+)': true,
            'Medium Workload (2-4)': true,
            'Light Workload (1)': true,
            'Unassigned': true,
            // Name grouping (first letters)
            'A': true, 'B': true, 'C': true, 'D': true, 'E': true
        },

        // Action mappings
        actions: {
            'View member': 'openTeamMemberModal',
            'Edit member': 'editTeamMember',
            'Remove member': 'removeTeamMember',
            'Assign to company': 'assignToCompany',
            'Assign to opportunity': 'assignToOpportunity',
            'Create task': 'createTaskForTeamMember'
        },

        // Bulk actions
        bulkActions: {
            'remove': (selectedIds) => window.bulkDelete(selectedIds),
            'assignToCompany': (selectedIds) => window.bulkAssignToCompany(selectedIds)
        }
    };
}

// Export configurations
window.getOpportunityConfig = getOpportunityConfig;
window.getTaskConfig = getTaskConfig;
window.getStakeholderConfig = getStakeholderConfig;
window.getCompanyConfig = getCompanyConfig;
window.getTeamConfig = getTeamConfig;