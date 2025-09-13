"""
Essential Server-Side Formatters

Minimal replacement for formatters.py - keeps only essential server-side formatting
that must happen during template rendering. Client-side formatting moved to Alpine.js.
"""

from datetime import datetime, date
from typing import Optional, Union


class CoreFormatter:
    """Minimal server-side formatter for essential template rendering."""

    # Default format strings
    DATE_FORMAT = '%m/%d/%y'
    DATETIME_FORMAT = '%m/%d %H:%M'
    CURRENCY_SYMBOL = '$'

    @classmethod
    def format_date_for_input(cls, date_value: Optional[Union[date, datetime]]) -> str:
        """Format date for HTML input fields (YYYY-MM-DD format)."""
        if not date_value:
            return ''

        if isinstance(date_value, datetime):
            date_value = date_value.date()

        return date_value.strftime('%Y-%m-%d')

    @classmethod
    def safe_string(cls, value, default='') -> str:
        """Safely convert value to string with fallback."""
        if value is None:
            return default
        return str(value)

    @classmethod
    def truncate_text(cls, text: str, length: int = 50, suffix: str = '...') -> str:
        """Truncate text with ellipsis - needed for server-side email previews."""
        if not text or len(text) <= length:
            return text or ''
        return text[:length].rstrip() + suffix


# Template filter functions for Jinja2
def date_for_input(date_value):
    """Jinja2 filter: Format date for HTML input fields."""
    return CoreFormatter.format_date_for_input(date_value)


def safe_string(value, default=''):
    """Jinja2 filter: Safe string conversion."""
    return CoreFormatter.safe_string(value, default)


def truncate(text, length=50, suffix='...'):
    """Jinja2 filter: Truncate text with ellipsis."""
    return CoreFormatter.truncate_text(text, length, suffix)