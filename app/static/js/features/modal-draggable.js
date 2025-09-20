/**
 * Modal Draggable Module
 * Makes modals draggable using Interact.js
 * DRY implementation that works with all modal types
 */

(function() {
    'use strict';

    const ModalDraggable = {
        initialized: false,
        activeModals: new Map(),

        init() {
            if (this.initialized || typeof interact === 'undefined') return;

            this.setupDraggableModals();
            this.observeModalChanges();
            this.initialized = true;
        },

        setupDraggableModals() {
            interact('.modal-content')
                .draggable({
                    allowFrom: '.modal-header',
                    inertia: true,
                    modifiers: [
                        interact.modifiers.restrictRect({
                            restriction: 'parent',
                            endOnly: true
                        })
                    ],
                    autoScroll: false,
                    listeners: {
                        start: this.onDragStart.bind(this),
                        move: this.onDragMove.bind(this),
                        end: this.onDragEnd.bind(this)
                    }
                })
                .styleCursor(false);
        },

        onDragStart(event) {
            const modal = event.target;
            const modalId = this.getModalId(modal);

            modal.classList.add('is-dragging');
            modal.style.cursor = 'grabbing';

            if (!this.activeModals.has(modalId)) {
                this.activeModals.set(modalId, { x: 0, y: 0 });
            }
        },

        onDragMove(event) {
            const modal = event.target;
            const modalId = this.getModalId(modal);
            const position = this.activeModals.get(modalId);

            if (position) {
                position.x += event.dx;
                position.y += event.dy;

                this.updateModalPosition(modal, position);
            }
        },

        onDragEnd(event) {
            const modal = event.target;
            modal.classList.remove('is-dragging');
            modal.style.cursor = '';
        },

        updateModalPosition(modal, position) {
            modal.style.transform = `translate(${position.x}px, ${position.y}px)`;
        },

        resetModalPosition(modal) {
            const modalId = this.getModalId(modal);

            modal.style.transform = '';
            modal.style.cursor = '';
            modal.classList.remove('is-dragging');

            if (this.activeModals.has(modalId)) {
                this.activeModals.delete(modalId);
            }
        },

        getModalId(modalElement) {
            const parentModal = modalElement.closest('.modal');
            return parentModal ? parentModal.id || 'default-modal' : 'default-modal';
        },

        observeModalChanges() {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.removedNodes.forEach((node) => {
                        if (node.nodeType === 1 && node.classList?.contains('modal')) {
                            const modalContent = node.querySelector('.modal-content');
                            if (modalContent) {
                                this.resetModalPosition(modalContent);
                            }
                        }
                    });

                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1 && node.classList?.contains('modal')) {
                            const modalContent = node.querySelector('.modal-content');
                            if (modalContent) {
                                this.resetModalPosition(modalContent);
                            }
                        }
                    });
                });
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        },

        addModalStyles() {
            if (document.getElementById('modal-draggable-styles')) return;

            const styles = document.createElement('style');
            styles.id = 'modal-draggable-styles';
            styles.textContent = `
                .modal-header {
                    cursor: grab;
                    user-select: none;
                }

                .modal-header:active,
                .modal-content.is-dragging .modal-header {
                    cursor: grabbing;
                }

                .modal-content {
                    transition: none;
                }

                .modal-content.is-dragging {
                    opacity: 0.95;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
                }
            `;

            document.head.appendChild(styles);
        }
    };

    function initModalDraggable() {
        ModalDraggable.addModalStyles();
        ModalDraggable.init();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initModalDraggable);
    } else {
        initModalDraggable();
    }

    window.ModalDraggable = ModalDraggable;

    document.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.classList?.contains('modal') ||
            event.detail.target.querySelector?.('.modal')) {
            setTimeout(() => ModalDraggable.init(), 100);
        }
    });

    if (window.Alpine) {
        document.addEventListener('alpine:initialized', () => {
            ModalDraggable.init();
        });
    }
})();