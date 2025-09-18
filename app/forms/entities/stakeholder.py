"""
Stakeholder Forms

Simple stakeholder form using WTForms with model introspection.
"""

from wtforms import StringField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Optional, Length
from ..base.base_forms import BaseForm


class StakeholderForm(BaseForm):
    """Form for creating and editing stakeholders in modals"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    meddpicc_roles = HiddenField("MEDDPICC Roles")

    comments = TextAreaField(
        "Comments",
        validators=[Optional()],
        render_kw={"placeholder": "Additional notes about this stakeholder...", "rows": 3},
    )

    def get_display_fields(self):
        """Return field names to display in modal, in this exact order"""
        return ["name", "job_title", "company", "meddpicc_roles", "comments"]
