"""
Form Helper Functions

Safe coercion and utility functions for WTForms.
"""


def safe_int_coerce(value):
    """
    Safe integer coercion for WTForms SelectField.

    Handles empty strings, None, and invalid values gracefully
    to prevent ValueError crashes in form rendering.

    Args:
        value: Value to coerce to integer

    Returns:
        int: Coerced integer value or None for invalid inputs

    Example:
        company_id = SelectField('Company', coerce=safe_int_coerce)
    """
    if value == '' or value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None