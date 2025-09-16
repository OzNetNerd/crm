/**
 * Alpine.js Dropdown Plugin
 * Unified dropdown component for single-select, multi-select, and form dropdowns
 * Replaces duplicate css_dropdown and form_select_dropdown macros
 */

// Ensure Alpine is loaded before registering components
function registerDropdown() {
    Alpine.data('dropdown', (config = {}) => ({
        // Core state
        open: false,
        selected: config.multi ? (config.selected || []) : (config.selected || ''),
        search: '',

        // Configuration
        name: config.name || 'dropdown',
        options: config.options || [],
        multi: config.multi || false,
        searchable: config.searchable || false,
        placeholder: config.placeholder || 'Select option',
        htmx: config.htmx || {},

        // Computed
        get filteredOptions() {
            if (!this.searchable || !this.search) {
                return this.options;
            }
            const searchLower = this.search.toLowerCase();
            return this.options.filter(opt => {
                const label = this.getOptionLabel(opt);
                return label.toLowerCase().includes(searchLower);
            });
        },

        get displayText() {
            if (this.multi) {
                if (this.selected.length === 0) {
                    return this.placeholder;
                }
                if (this.selected.length === 1) {
                    const option = this.findOption(this.selected[0]);
                    return option ? this.getOptionLabel(option) : this.placeholder;
                }
                return `${this.selected.length} selected`;
            } else {
                if (!this.selected) {
                    return this.placeholder;
                }
                const option = this.findOption(this.selected);
                return option ? this.getOptionLabel(option) : this.placeholder;
            }
        },

        get isSelected() {
            return (value) => {
                if (this.multi) {
                    return this.selected.includes(value);
                }
                return this.selected === value;
            };
        },

        // Methods
        init() {
            // Watch for changes and dispatch events
            this.$watch('selected', (value) => {
                this.$dispatch('dropdown:change', {
                    name: this.name,
                    value: value,
                    multi: this.multi
                });

                // Trigger HTMX if configured
                if (this.htmx.trigger) {
                    this.triggerHtmx();
                }
            });

            // Close on click outside
            this.$refs.container.addEventListener('click', (e) => {
                e.stopPropagation();
            });

            // Keyboard navigation
            this.$refs.container.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.close();
                }
            });
        },

        toggle() {
            this.open = !this.open;
            if (this.open && this.searchable) {
                this.$nextTick(() => {
                    this.$refs.searchInput?.focus();
                });
            }
        },

        close() {
            this.open = false;
            this.search = '';
        },

        select(value) {
            if (this.multi) {
                const index = this.selected.indexOf(value);
                if (index > -1) {
                    this.selected = this.selected.filter(v => v !== value);
                } else {
                    this.selected = [...this.selected, value];
                }
            } else {
                this.selected = value;
                this.close();
            }
        },

        selectAll() {
            if (this.multi) {
                if (this.selected.length === this.options.length) {
                    this.selected = [];
                } else {
                    this.selected = this.options.map(opt => this.getOptionValue(opt));
                }
            }
        },

        clearSelection() {
            this.selected = this.multi ? [] : '';
        },

        // Helper methods
        findOption(value) {
            return this.options.find(opt => this.getOptionValue(opt) === value);
        },

        getOptionValue(option) {
            return typeof option === 'object' ? option.value : option;
        },

        getOptionLabel(option) {
            if (typeof option === 'object') {
                return option.label || option.value;
            }
            return option.toString();
        },

        triggerHtmx() {
            // Find the form containing this dropdown and trigger HTMX
            const input = this.$refs.hiddenInput;
            if (input) {
                // Update the input value first
                input.value = this.selected;

                // Find the parent form
                const form = input.closest('form');
                if (form) {
                    // Trigger HTMX on the form using htmx API
                    if (window.htmx) {
                        htmx.trigger(form, 'change');
                    }
                } else {
                    // Fallback: dispatch event on input
                    const event = new Event('change', { bubbles: true });
                    input.dispatchEvent(event);
                }
            }
        },

        // Click outside handler
        clickOutside(event) {
            if (!this.$refs.container.contains(event.target)) {
                this.close();
            }
        }
    }));

    // Removed global click handler - handled by Alpine.js @click.away
}

// Register when Alpine is ready - ensure it works
document.addEventListener('DOMContentLoaded', () => {
    if (typeof Alpine !== 'undefined') {
        registerDropdown();
    } else {
        document.addEventListener('alpine:init', registerDropdown);
    }
});