"""
User (Team Member) Modal Form

Explicit form class for User/Team Member modals with controlled field ordering.
Focuses on essential fields for quick team member creation.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Email
from app.models.user import User


class UserModalForm(FlaskForm):
    """
    User/Team Member modal form with explicit field ordering:
    1. Name (required)
    2. Email (required)
    3. Job Title (optional)
    4. Department (optional dropdown)
    """

    # Field 1: Name (required, at top)
    name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(max=255)],
        render_kw={"placeholder": "Enter team member name..."},
    )

    # Field 2: Email (required)
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=255)],
        render_kw={"placeholder": "Enter email address..."},
    )

    # Field 3: Job Title (optional)
    job_title = StringField(
        "Job Title",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Enter job title..."},
    )

    # Field 4: Department (optional dropdown)
    department = SelectField(
        "Department",
        validators=[Optional()],
        choices=[],  # Will be populated in __init__
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set department choices from model metadata
        department_choices = User.get_field_choices("department")
        self.department.choices = [("", "Select department")] + department_choices
