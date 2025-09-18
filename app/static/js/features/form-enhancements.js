/**
 * Form Enhancement Features
 * - Date field increment buttons
 * - Days countdown calculation
 */

/**
 * Add specified number of days to a date field
 * @param {string} fieldId - The ID of the date input field
 * @param {number} days - Number of days to add
 */
function addDaysToDate(fieldId, days) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    let currentDate;
    if (field.value) {
        currentDate = new Date(field.value);
    } else {
        currentDate = new Date();
    }

    // Add the specified number of days
    currentDate.setDate(currentDate.getDate() + days);

    // Format as YYYY-MM-DD for the date input
    const year = currentDate.getFullYear();
    const month = String(currentDate.getMonth() + 1).padStart(2, '0');
    const day = String(currentDate.getDate()).padStart(2, '0');

    field.value = `${year}-${month}-${day}`;

    // Trigger input event to update any listeners
    field.dispatchEvent(new Event('input', { bubbles: true }));

    // Update countdown
    updateDateCountdown(fieldId);
}

/**
 * Calculate and display days remaining until the date
 * @param {string} fieldId - The ID of the date input field
 */
function updateDateCountdown(fieldId) {
    const field = document.getElementById(fieldId);
    const countdownDiv = document.getElementById(fieldId + '_countdown');

    if (!field || !countdownDiv) return;

    const dateValue = field.value;
    if (!dateValue) {
        countdownDiv.style.display = 'none';
        countdownDiv.classList.add('hidden');
        return;
    }

    const selectedDate = new Date(dateValue);
    const today = new Date();

    // Reset time to start of day for accurate day calculation
    today.setHours(0, 0, 0, 0);
    selectedDate.setHours(0, 0, 0, 0);

    const timeDiff = selectedDate.getTime() - today.getTime();
    const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));

    const countdownText = countdownDiv.querySelector('.countdown-text');
    if (!countdownText) return;

    let message = '';
    let className = '';

    if (daysDiff === 0) {
        message = 'Today';
        className = 'countdown-today';
    } else if (daysDiff === 1) {
        message = 'Tomorrow';
        className = 'countdown-soon';
    } else if (daysDiff === -1) {
        message = 'Yesterday';
        className = 'countdown-overdue';
    } else if (daysDiff > 1) {
        message = `${daysDiff} days to go`;
        className = daysDiff <= 7 ? 'countdown-soon' : 'countdown-future';
    } else {
        message = `${Math.abs(daysDiff)} days ago`;
        className = 'countdown-overdue';
    }

    countdownText.textContent = message;
    countdownDiv.className = `form-date-countdown ${className}`;
    countdownDiv.style.display = 'inline-block';
    countdownDiv.classList.remove('hidden');
}

/**
 * Initialize date field enhancements when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Find all date fields with enhancements
    const dateFields = document.querySelectorAll('input[type="date"].form-date-compact');

    dateFields.forEach(field => {
        // Add input event listener to update countdown
        field.addEventListener('input', function() {
            updateDateCountdown(field.id);
        });

        // Initialize countdown if field has a value
        if (field.value) {
            updateDateCountdown(field.id);
        }
    });
});

/**
 * Re-initialize date enhancements after HTMX content updates
 */
document.addEventListener('htmx:afterSwap', function(event) {
    // Only process if new content contains date fields
    const newDateFields = event.detail.target.querySelectorAll('input[type="date"].form-date-compact');

    newDateFields.forEach(field => {
        field.addEventListener('input', function() {
            updateDateCountdown(field.id);
        });

        if (field.value) {
            updateDateCountdown(field.id);
        }
    });
});