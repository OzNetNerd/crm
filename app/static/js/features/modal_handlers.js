// Global modal event handlers for read-only entity views from global search

class ModalHandlers {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindGlobalModalEvents();
    }
    
    bindGlobalModalEvents() {
        // Handle all entity modal open events from global search
        const entityTypes = ['company', 'contact', 'stakeholder', 'opportunity', 'task'];
        
        entityTypes.forEach(entityType => {
            window.addEventListener(`open-detail-${entityType}-modal`, (event) => {
                this.handleEntityModalOpen(entityType, event.detail);
            });
        });
    }
    
    async handleEntityModalOpen(entityType, detail) {
        const { id, readOnly = false } = detail;
        
        if (!id) {
            console.error(`No ID provided for ${entityType} modal`);
            return;
        }
        
        try {
            // Determine endpoint based on read-only flag
            const endpoint = readOnly 
                ? `/modals/${entityType}/${id}/view`
                : `/modals/${entityType}/${id}/edit`;
            
            // Make HTMX request to load the modal
            const response = await fetch(endpoint);
            
            if (!response.ok) {
                throw new Error(`Failed to load ${entityType} modal: ${response.statusText}`);
            }
            
            const modalHtml = await response.text();
            
            // Insert modal into the page
            this.showModal(modalHtml);
            
        } catch (error) {
            console.error(`Error opening ${entityType} modal:`, error);
            this.showErrorModal(`Failed to load ${entityType} details`);
        }
    }
    
    showModal(modalHtml) {
        // Remove any existing modals
        this.closeExistingModals();
        
        // Create modal container and insert HTML
        const modalContainer = document.createElement('div');
        modalContainer.id = 'modal-content-area';
        modalContainer.innerHTML = modalHtml;
        
        // Append to body
        document.body.appendChild(modalContainer);
        
        // Focus trap for accessibility
        this.focusModal(modalContainer);
    }
    
    closeExistingModals() {
        // Remove existing modals
        const existingModals = document.querySelectorAll('#modal-content-area, .modal-overlay');
        existingModals.forEach(modal => modal.remove());
    }
    
    focusModal(modalContainer) {
        // Focus the modal for accessibility
        const focusableElement = modalContainer.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusableElement) {
            focusableElement.focus();
        }
    }
    
    showErrorModal(message) {
        const errorHtml = `
            <div class="modal-overlay fixed inset-0 z-50 flex items-center justify-center" 
                 tabindex="-1">
                <div class="modal-backdrop fixed inset-0 bg-black bg-opacity-50" 
                     onclick="this.parentElement.remove()"></div>
                <div class="modal-content relative bg-white rounded-lg shadow-xl max-w-sm w-full mx-4">
                    <div class="p-6">
                        <div class="flex items-center mb-4">
                            <div class="text-red-500 text-2xl mr-3">⚠️</div>
                            <h3 class="text-lg font-semibold text-gray-900">Error</h3>
                        </div>
                        <p class="text-gray-600 mb-4">${message}</p>
                        <button onclick="this.closest('.modal-overlay').remove()" 
                                class="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                            OK
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        this.showModal(errorHtml);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ModalHandlers();
});

// Export for global access
window.ModalHandlers = ModalHandlers;