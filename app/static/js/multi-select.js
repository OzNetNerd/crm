/**
 * Multi-Select Dropdown Component
 * Minimal JavaScript for dropdown toggle and text updates
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all multi-select dropdowns
    initMultiSelectDropdowns();
});

function initMultiSelectDropdowns() {
    const dropdowns = document.querySelectorAll('.multi-select-dropdown');

    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.multi-select-trigger');
        const options = dropdown.querySelector('.multi-select-options');
        const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
        const selectedText = trigger.querySelector('.selected-text');

        // Toggle dropdown on trigger click
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Close other dropdowns
            closeAllDropdowns(dropdown);

            // Toggle current dropdown
            const isHidden = options.classList.contains('hidden');
            options.classList.toggle('hidden', !isHidden);
            trigger.classList.toggle('active', isHidden);
        });

        // Update selected text when checkboxes change
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateSelectedText(dropdown);
            });
        });

        // Initialize selected text
        updateSelectedText(dropdown);
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.multi-select-dropdown')) {
            closeAllDropdowns();
        }
    });
}

function updateSelectedText(dropdown) {
    const trigger = dropdown.querySelector('.multi-select-trigger');
    const selectedText = trigger.querySelector('.selected-text');
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]:checked');
    const placeholder = selectedText.getAttribute('data-placeholder') || 'Select options...';

    if (checkboxes.length === 0) {
        selectedText.textContent = placeholder;
    } else if (checkboxes.length === 1) {
        selectedText.textContent = checkboxes[0].nextElementSibling.textContent;
    } else {
        selectedText.textContent = `${checkboxes.length} options selected`;
    }
}

function closeAllDropdowns(except = null) {
    const dropdowns = document.querySelectorAll('.multi-select-dropdown');

    dropdowns.forEach(dropdown => {
        if (dropdown !== except) {
            const options = dropdown.querySelector('.multi-select-options');
            const trigger = dropdown.querySelector('.multi-select-trigger');

            options.classList.add('hidden');
            trigger.classList.remove('active');
        }
    });
}