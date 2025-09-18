"""Template utilities - simple functions for Jinja2."""


def badge_class(value):
    """Convert value to badge-compatible CSS class."""
    return str(value).lower().replace("_", " ").replace("-", " ") if value else ""


def get_dashboard_action_buttons():
    """Get list of dashboard action buttons."""
    return ["companies", "tasks", "opportunities", "stakeholders", "teams"]
