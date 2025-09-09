/**
 * Data Initializer - Clean pattern for passing server data to client JavaScript
 * This replaces inline script blocks with a systematic data attribute approach
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize global data from data attributes
    const dataContainer = document.getElementById('app-data');
    if (!dataContainer) return;
    
    // Parse and set global data if available
    const datasets = {
        companies: 'companiesData',
        contacts: 'contactsData', 
        opportunities: 'opportunitiesData',
        tasks: 'tasksData'
    };
    
    Object.keys(datasets).forEach(key => {
        const dataAttr = dataContainer.dataset[key];
        if (dataAttr) {
            try {
                window[datasets[key]] = JSON.parse(dataAttr);
                console.log(`Successfully parsed ${key}:`, window[datasets[key]].length, 'items');
            } catch (e) {
                console.error(`Failed to parse ${key} data:`, e);
                window[datasets[key]] = [];
            }
        } else {
            // Initialize empty arrays to prevent undefined errors only if the data doesn't exist as window variables
            if (!window[datasets[key]]) {
                console.log(`No data attribute found for ${key} and no window variable, initializing empty array`);
                window[datasets[key]] = [];
            }
        }
    });
    
    // Initialize specific functionality based on page
    const pageType = dataContainer.dataset.pageType;
    
    switch (pageType) {
        case 'multi-task':
            if (typeof initMultiTaskData === 'function') {
                initMultiTaskData(
                    window.companiesData || [],
                    window.contactsData || [],
                    window.opportunitiesData || []
                );
            }
            if (typeof initMultiTaskForm === 'function') {
                initMultiTaskForm();
            }
            break;
            
        case 'tasks-index':
            if (typeof initTasksData === 'function') {
                initTasksData(
                    window.companiesData || [],
                    window.contactsData || [],
                    window.opportunitiesData || [],
                    window.tasksData || []
                );
            }
            break;
    }
});