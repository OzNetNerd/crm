"""Number and currency formatting utilities for the CRM application."""


def format_number(value):
    """Format number with thousand separators.

    Args:
        value: Numeric value to format

    Returns:
        Formatted string with commas (e.g., 75000 → 75,000)
    """
    if value is None or value == "":
        return "0"
    try:
        # Handle string inputs that might be numeric
        if isinstance(value, str):
            value = float(value) if '.' in value else int(value)
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return "0"


def format_currency(value):
    """Format value as currency with dollar sign and thousand separators.

    Args:
        value: Numeric value to format

    Returns:
        Formatted currency string (e.g., 75000 → $75,000)
    """
    if value is None or value == "" or value == 0:
        return "$0"
    try:
        # Handle string inputs that might be numeric
        if isinstance(value, str):
            value = float(value) if '.' in value else int(value)
        return f"${int(value):,}"
    except (ValueError, TypeError):
        return "$0"


def format_currency_short(value):
    """Format currency values with abbreviated units for large numbers.

    Args:
        value: The numeric value to format.

    Returns:
        Formatted currency string (e.g., "$1.5M", "$250K", "$100")
    """
    if value is None or value == "" or value == 0:
        return "$0"

    try:
        # Handle string inputs that might be numeric
        if isinstance(value, str):
            value = float(value) if '.' in value else int(value)

        value = float(value)
        if value >= 1000000:
            # Format millions with 1 decimal if needed, but remove .0
            formatted = f"{value/1000000:.1f}M"
            if formatted.endswith('.0M'):
                formatted = formatted[:-3] + 'M'
            return f"${formatted}"
        elif value >= 1000:
            return f"${value/1000:.0f}K"
        return f"${int(value):,}"
    except (ValueError, TypeError):
        return "$0"


def format_percentage(value):
    """Format percentage values.

    Args:
        value: The numeric value to format as percentage.

    Returns:
        Formatted percentage string (e.g., "75%")
    """
    if value is None:
        return "0%"
    try:
        return f"{float(value):.0f}%"
    except (ValueError, TypeError):
        return f"{value}%"