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
        contacts: 'stakeholdersData', 
        opportunities: 'opportunitiesData',
        tasks: 'tasksData',
        teamMembers: 'teamData',
        modelConfigs: 'modelConfigs',
        opportunityConfig: 'opportunityConfig',
        taskConfig: 'taskConfig'
    };
    
    Object.keys(datasets).forEach(key => {
        const dataAttr = dataContainer.dataset[key];
        if (dataAttr && dataAttr.trim() !== '') {
            try {
                const parsed = JSON.parse(dataAttr);
                window[datasets[key]] = parsed || [];
                console.log(`Successfully parsed ${key}:`, Array.isArray(window[datasets[key]]) ? window[datasets[key]].length : 'object', 'items');
            } catch (e) {
                console.error(`Failed to parse ${key} data:`, e, 'Raw data:', dataAttr.substring(0, 100) + '...');
                window[datasets[key]] = [];
            }
        } else {
            // Initialize empty arrays/objects to prevent undefined errors only if the data doesn't exist as window variables
            if (!window[datasets[key]]) {
                // Use appropriate default based on expected type
                const defaultValue = key.includes('Config') ? {} : [];
                window[datasets[key]] = defaultValue;
                // Only log when debugging is needed
                if (dataAttr) {
                    console.log(`Empty data attribute for ${key}, initialized as:`, typeof defaultValue);
                }
            }
        }
    });
    
    // Trigger Alpine.js re-initialization after data is loaded
    // This fixes the timing issue where Alpine.js initializes before data is available
    document.dispatchEvent(new CustomEvent('dataReady'));
    
    // Initialize specific functionality based on page
    const pageType = dataContainer.dataset.pageType;
    
    switch (pageType) {
        case 'tasks-index':
            if (typeof initTasksData === 'function') {
                initTasksData(
                    window.companiesData || [],
                    window.stakeholdersData || [],
                    window.opportunitiesData || [],
                    window.tasksData || []
                );
            }
            break;
    }
});