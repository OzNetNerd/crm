from datetime import date
from typing import Optional


def calculate_relative_days(target_date: date, from_date: Optional[date] = None) -> int:
    """
    Calculate the number of days between dates.

    Args:
        target_date: The target date to compare to
        from_date: The reference date (defaults to today)

    Returns:
        int: Positive for future dates, negative for past dates, 0 for today
    """
    if not target_date:
        return 0

    if from_date is None:
        from_date = date.today()

    return (target_date - from_date).days


def format_relative_time(days_diff: int) -> str:
    """
    Format relative time display based on days difference.

    Args:
        days_diff: Number of days (positive=future, negative=past, 0=today)

    Returns:
        str: Formatted relative time string
    """
    if days_diff < 0:
        days_ago = abs(days_diff)
        return f"({days_ago} day{'s' if days_ago != 1 else ''} ago)"
    elif days_diff == 0:
        return "(Today)"
    else:
        return f"({days_diff} day{'s' if days_diff != 1 else ''} to go)"


def format_date_with_relative(
    target_date: Optional[date],
    from_date: Optional[date] = None,
    date_format: str = "%d/%m/%y",
) -> str:
    """
    Format date with relative time information.

    Args:
        target_date: The date to format
        from_date: The reference date (defaults to today)
        date_format: Date format string

    Returns:
        str: Formatted date with relative time, e.g. "15/09/25 (3 days to go)"
    """
    if not target_date:
        return ""

    formatted_date = target_date.strftime(date_format)
    days_diff = calculate_relative_days(target_date, from_date)
    relative_time = format_relative_time(days_diff)

    return f"{formatted_date} {relative_time}"


def get_next_step_icon(next_step_type: Optional[str]) -> str:
    """
    Get appropriate icon name for next step type.

    Args:
        next_step_type: The type of next step

    Returns:
        str: Icon name for use with the icon macro
    """
    icon_map = {
        "call": "phone",
        "email": "envelope",
        "meeting": "calendar",
        "demo": "calendar",
    }
    return icon_map.get(next_step_type, "calendar")
