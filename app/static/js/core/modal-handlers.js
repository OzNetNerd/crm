/**
 * Modal event handlers using event delegation
 * Replaces all inline JavaScript handlers with proper event listeners
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle modal close buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-modal-close]')) {
            const modal = e.target.closest('.modal-overlay');
            if (modal) {
                modal.remove();
            }
        }
    });

    // Handle backdrop clicks
    document.addEventListener('click', function(e) {
        if (e.target.matches('.modal-backdrop[data-close-on-click]')) {
            const modal = e.target.closest('.modal-overlay');
            if (modal) {
                modal.remove();
            }
        }
    });

    // Handle escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal-overlay[data-close-on-escape]');
            if (modal) {
                modal.remove();
            }
        }
    });

    // Handle auto-close success messages
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    // Check for auto-close success messages
                    const successMsg = node.querySelector?.('[data-auto-close]');
                    if (successMsg) {
                        const delay = parseInt(successMsg.dataset.autoClose) || 1500;
                        const entityId = successMsg.dataset.entityId;

                        setTimeout(() => {
                            const modal = successMsg.closest('.modal-overlay');
                            if (modal) {
                                modal.remove();
                            }

                            // Trigger refresh if needed
                            if (window.htmxModalSuccess && entityId) {
                                window.htmxModalSuccess(entityId);
                            } else {
                                window.location.reload();
                            }
                        }, delay);
                    }

                    // Check for trigger close
                    const triggerClose = node.querySelector?.('[data-trigger-modal-close]');
                    if (triggerClose) {
                        const modal = document.querySelector('.modal-overlay');
                        if (modal) {
                            modal.remove();
                        }
                        if (window.htmxModalClosed) {
                            window.htmxModalClosed();
                        }
                    }
                }
            });
        });
    });

    // Start observing the document for added nodes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});