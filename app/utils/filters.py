"""
Jinja2 template filters for the CRM application.
Provides DRY utility functions for template rendering.
"""


def badge_class(value):
    """
    Convert a value to a badge-compatible CSS class.

    Rules:
    - Lowercase the value
    - Replace underscores with spaces
    - Replace hyphens with spaces

    Args:
        value (str): The input value to convert

    Returns:
        str: The badge-compatible class name

    Examples:
        'In_Progress' -> 'in progress'
        'High-Priority' -> 'high priority'
        'COMPLETED' -> 'completed'
    """
    if not value:
        return ''

    return str(value).lower().replace('_', ' ').replace('-', ' ')