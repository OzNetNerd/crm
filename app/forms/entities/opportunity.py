"""
Opportunity Forms

Simple opportunity form using WTForms with model introspection.
"""

from wtforms import StringField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from ..base.base_forms import BaseForm
from app.models.opportunity import Opportunity
from app.models.company import Company


class OpportunityForm(BaseForm):
    """Form for creating and editing opportunities in modals"""

    model = Opportunity  # Primary model for metadata/validation

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set priority choices from model metadata
        priority_choices = self.model.get_field_choices("priority")
        self.priority.choices = [("", "Select priority")] + priority_choices

    name = StringField(
        "Opportunity Name",
        validators=[DataRequired(), Length(max=255)],
        render_kw={"placeholder": "Enter opportunity name..."},
    )

    value = IntegerField(
        "Deal Value",
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Enter deal value...", "min": 0},
    )

    probability = IntegerField(
        "Win Probability (%)",
        validators=[Optional(), NumberRange(min=0, max=100)],
        render_kw={"placeholder": "0-100", "min": 0, "max": 100},
        default=0,
    )

    priority = SelectField(
        "Priority", validators=[Optional()], choices=[]  # Will be populated in __init__
    )

    expected_close_date = DateField(
        "Expected Close Date",
        validators=[Optional()],
        render_kw={"placeholder": "Select date..."},
    )

    stage = StringField(
        "Pipeline Stage",
        validators=[DataRequired()],
        render_kw={
            "data-search-type": "choice:stage",
            "placeholder": "Search pipeline stages...",
            "autocomplete": "off",
        },
        default="prospect",
    )

    # Field from Company model - uses search instead of dropdown
    company = StringField(
        "Company",
        validators=[DataRequired()],
        render_kw={
            "data-search-type": "company",
            "placeholder": "Search companies...",
            "autocomplete": "off",
        },
    )

    def get_display_fields(self):
        """Return field names to display in modal, in this exact order"""
        return ["company", "name", "stage", "value"]
