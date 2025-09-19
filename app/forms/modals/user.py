"""
User (Team Member) Modal Form

Explicit form class for User/Team Member modals with controlled field ordering.
Focuses on essential fields for quick team member creation.
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Optional


class UserModalForm(FlaskForm):
    """
    User/Team Member modal form with simplified fields:
    1. Name (required)
    2. Job Title (optional)

    These fields are displayed side-by-side in the modal.

    Note: This simplified form is used specifically for modals to provide
    a streamlined user creation experience. Email and Department fields
    have been removed to focus on essential information only.
    """

    # Field 1: Name (required) - Essential identification
    name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(max=255)],
        render_kw={"placeholder": "Enter team member name..."},
    )

    # Field 2: Job Title (optional) - Role identification
    job_title = StringField(
        "Job Title",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Enter job title..."},
    )

    def get_display_fields(self):
        """Return field names to display in modal"""
        return ["name", "job_title"]

    def get_field_layout(self):
        """
        Define field layout for consistent rendering in view and edit modes.
        Name and Job Title side by side for compact user creation.
        """
        return [
            {'type': 'inline-2col', 'fields': ['name', 'job_title']}
        ]
