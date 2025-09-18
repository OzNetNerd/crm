# Utils package
# Re-export commonly used functions from utils.py to avoid import conflicts

from datetime import date
from typing import Optional


def format_date_with_relative(
    target_date: date, from_date: Optional[date] = None, date_format: str = "%d/%m/%y"
) -> str:
    """Format date with relative time information."""
    if not target_date:
        return ""

    formatted_date = target_date.strftime(date_format)

    # Calculate days difference
    if from_date is None:
        from_date = date.today()
    days_diff = (target_date - from_date).days

    # Format relative time
    if days_diff == 0:
        relative = "(today)"
    elif days_diff == 1:
        relative = "(tomorrow)"
    elif days_diff == -1:
        relative = "(yesterday)"
    elif days_diff > 1:
        relative = f"({days_diff} days to go)"
    else:
        relative = f"({abs(days_diff)} days ago)"

    return f"{formatted_date} {relative}"


def get_next_step_icon(next_step_type: Optional[str]) -> str:
    """Get appropriate icon name for next step type."""
    if not next_step_type:
        return "calendar"

    icons = {
        "call": "phone",
        "email": "envelope",
        "meeting": "calendar",
        "follow_up": "chevron-right",
    }
    return icons.get(next_step_type, "chevron-right")
