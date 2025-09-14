"""
Team web routes for the CRM application.
"""

from flask import Blueprint
from app.models import User

# Create blueprint
teams_bp = Blueprint("teams", __name__)


@teams_bp.route("/")
def index():
    """Main teams index page."""
    return User.render_index()


@teams_bp.route("/content")
def content():
    """HTMX endpoint for filtered team content."""
    return User.render_content(
        filter_fields=['job_title', 'department'],
        join_map={}  # No joins needed for user/team sorting
    )