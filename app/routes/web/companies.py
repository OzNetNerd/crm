"""
Company web routes for the CRM application.
"""

from flask import Blueprint
from app.models import Company

# Create blueprint
companies_bp = Blueprint("companies", __name__)


@companies_bp.route("/")
def index():
    """Main companies index page."""
    return Company.render_index()


@companies_bp.route("/content")
def content():
    """HTMX endpoint for filtered company content."""
    return Company.render_content(
        filter_fields=['industry', 'size'],
        join_map={}  # No joins needed for company sorting
    )