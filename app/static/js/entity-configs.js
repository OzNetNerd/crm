/**
 * Entity Configurations for the Generic Entity Manager System
 * Defines specific configurations for each entity type (Tasks, Opportunities, etc.)
 */

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
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>'
                    },
                    { 
                        key: 'qualified', 
                        title: 'Qualified', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>'
                    },
                    { 
                        key: 'proposal', 
                        title: 'Proposal', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path></svg>'
                    },
                    { 
                        key: 'negotiation', 
                        title: 'Negotiation', 
                        containerClass: 'card-orange', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-orange-200 px-6 py-4 bg-orange-50 hover:bg-orange-100', 
                        badgeClass: 'badge-orange',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    }
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
                        icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clip-rule="evenodd"></path></svg>'
                    },
                    { 
                        key: 'this_week', 
                        title: 'This Week', 
                        containerClass: 'card-orange', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-orange-200 px-6 py-4 bg-orange-50 hover:bg-orange-100', 
                        badgeClass: 'badge-orange',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5a2.25 2.25 0 002.25-2.25m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5a2.25 2.25 0 012.25 2.25v7.5M8.25 21h7.5"></path></svg>'
                    },
                    { 
                        key: 'this_month', 
                        title: 'This Month', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>'
                    },
                    { 
                        key: 'later', 
                        title: 'Later', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>'
                    },
                    { 
                        key: 'no_date', 
                        title: 'No Close Date', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    }
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
                        icon: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M12.963 2.286a.75.75 0 00-1.071-.136 9.742 9.742 0 00-3.539 6.177A7.547 7.547 0 016.648 6.61a.75.75 0 00-1.152-.082A9 9 0 1015.68 4.534a7.46 7.46 0 01-2.717-2.248zM15.75 14.25a3.75 3.75 0 11-7.313-1.172c.628.465 1.35.81 2.133 1a5.99 5.99 0 011.925-3.545 3.75 3.75 0 013.255 3.717z" clip-rule="evenodd"></path></svg>'
                    },
                    { 
                        key: 'medium', 
                        title: 'Medium Value ($10K-$50K)', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path></svg>'
                    },
                    { 
                        key: 'low', 
                        title: 'Low Value (<$10K)', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>'
                    }
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
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>'
                    },
                    { 
                        key: 'in-progress', 
                        title: 'In Progress', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>'
                    },
                    { 
                        key: 'complete', 
                        title: 'Completed', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    }
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
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z"></path></svg>'
                    },
                    { 
                        key: 'medium', 
                        title: 'Medium Priority', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>'
                    },
                    { 
                        key: 'low', 
                        title: 'Low Priority', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>'
                    }
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
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    },
                    { 
                        key: 'today', 
                        title: 'Due Today', 
                        containerClass: 'card-orange', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-orange-200 px-6 py-4 bg-orange-50 hover:bg-orange-100', 
                        badgeClass: 'badge-orange',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>'
                    },
                    { 
                        key: 'this_week', 
                        title: 'This Week', 
                        containerClass: 'card-info', 
                        headerClass: 'text-status-info', 
                        headerBgClass: 'border-b border-blue-200 px-6 py-4 bg-blue-50 hover:bg-blue-100', 
                        badgeClass: 'badge-blue',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>'
                    },
                    { 
                        key: 'later', 
                        title: 'Later', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>'
                    },
                    { 
                        key: 'no_date', 
                        title: 'No Due Date', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    }
                ]
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
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>'
                    },
                    { 
                        key: 'contact', 
                        title: 'Contact Tasks', 
                        containerClass: 'card-success', 
                        headerClass: 'text-status-success', 
                        headerBgClass: 'border-b border-green-200 px-6 py-4 bg-green-50 hover:bg-green-100', 
                        badgeClass: 'badge-green',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>'
                    },
                    { 
                        key: 'opportunity', 
                        title: 'Opportunity Tasks', 
                        containerClass: 'card-warning', 
                        headerClass: 'text-status-warning', 
                        headerBgClass: 'border-b border-yellow-200 px-6 py-4 bg-yellow-50 hover:bg-yellow-100', 
                        badgeClass: 'badge-yellow',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    },
                    { 
                        key: 'unrelated', 
                        title: 'General Tasks', 
                        containerClass: 'card-neutral', 
                        headerClass: 'text-status-neutral', 
                        headerBgClass: 'border-b border-gray-200 px-6 py-4 bg-gray-50 hover:bg-gray-100', 
                        badgeClass: 'badge-gray',
                        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>'
                    }
                ]
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
            { value: 'contact', label: 'Contact' },
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

        // Entity card renderer
        renderEntityCard: (task, groupContext) => {
            const cachedElement = document.getElementById(`task-card-${task.id}`);
            return cachedElement ? cachedElement.innerHTML : '';
        },

        // Due date category logic
        getDueDateCategory: (task, today) => {
            if (!task.due_date) return 'no_date';
            
            const dueDate = new Date(task.due_date);
            const daysDiff = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
            
            if (daysDiff < 0) return 'overdue';
            if (daysDiff === 0) return 'today';
            if (daysDiff <= 7) return 'this_week';
            return 'later';
        },

        // Custom grouping logic for due dates and entities
        customGroupLogic: {
            'due_date': (tasks, config) => {
                return config.groupOptions.due_date.groups.map(group => ({
                    ...group,
                    entities: tasks.filter(task => {
                        if (task.task_type === 'child') return false;
                        return config.getDueDateCategory(task, config.today) === group.key;
                    })
                }));
            },
            'entity': (tasks, config) => {
                return config.groupOptions.entity.groups.map(group => ({
                    ...group,
                    entities: tasks.filter(task => {
                        if (task.task_type === 'child') return false;
                        if (group.key === 'unrelated') {
                            return !task.entity_type || task.entity_type === null;
                        }
                        return task.entity_type === group.key;
                    })
                }));
            }
        },

        // Bulk action mappings
        bulkActions: {
            'update': (selectedIds) => window.bulkUpdateTaskStatus(selectedIds),
            'delete': (selectedIds) => window.bulkDeleteTasks(selectedIds)
        }
    };
}

// Export configurations
window.getOpportunityConfig = getOpportunityConfig;
window.getTaskConfig = getTaskConfig;