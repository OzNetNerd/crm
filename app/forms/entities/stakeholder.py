"""
Stakeholder Forms

Simple stakeholder form using WTForms with model introspection.
"""

from wtforms import StringField, TextAreaField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, Length
from ..base.base_forms import BaseForm


class StakeholderForm(BaseForm):
    """Form for creating and editing stakeholders in modals"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate MEDDPICC role choices
        from app.models.enums import MeddpiccRole

        self.meddpicc_roles_select.choices = [
            (role.value, role.value.replace("_", " ").title())
            for role in MeddpiccRole
        ]

    name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(max=255)],
        render_kw={"placeholder": "Enter stakeholder name..."},
    )

    job_title = StringField(
        "Job Title",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Enter job title..."},
    )

    company = StringField("Company", validators=[DataRequired()])

    meddpicc_roles = HiddenField("MEDDPICC Roles")  # Keep for backward compatibility

    meddpicc_roles_select = SelectMultipleField(
        "MEDDPICC Roles",
        choices=[],  # Will be populated in __init__
        validators=[Optional()],
        render_kw={"class": "form-select", "size": "8"}
    )

    relationship_owners = HiddenField("Relationship Owners")

    comments = TextAreaField(
        "Comments",
        validators=[Optional()],
        render_kw={
            "placeholder": "Additional notes about this stakeholder...",
            "rows": 3,
        },
    )

    def get_display_fields(self):
        """Return field names to display in modal, in this exact order"""
        return ["name", "company", "job_title", "meddpicc_roles_select", "relationship_owners", "comments"]

    def get_field_layout(self):
        """
        Define field layout for consistent rendering in view and edit modes.
        Company and Job Title side by side for better space utilization.
        """
        return [
            {'type': 'single', 'field': 'name'},
            {'type': 'inline-2col', 'fields': ['company', 'job_title']},
            {'type': 'single', 'field': 'meddpicc_roles_select'},
            {'type': 'single', 'field': 'relationship_owners'},
            {'type': 'single', 'field': 'comments'}
        ]
