"""
Opportunity Forms

Simple opportunity form using WTForms with model introspection.
"""

from wtforms import StringField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from ..base.base_forms import BaseForm
# ModelIntrospector removed - use model methods directly
from app.utils.forms.helpers import safe_int_coerce


class OpportunityForm(BaseForm):
    """Form for creating and editing opportunities in modals"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set choices from model metadata
        from app.models.opportunity import Opportunity

        # Set priority choices
        priority_choices = Opportunity.get_field_choices('priority')
        self.priority.choices = [('', 'Select priority')] + priority_choices

        # Set stage choices
        stage_choices = Opportunity.get_field_choices('stage')
        self.stage.choices = [('', 'Select stage')] + stage_choices

        # Set company choices
        from app.models.company import Company
        companies = Company.query.order_by(Company.name).all()
        self.company_id.choices = [('', 'Select company')] + [
            (str(company.id), company.name) for company in companies
        ]

    name = StringField(
        'Opportunity Name',
        validators=[DataRequired(), Length(max=255)],
        render_kw={'placeholder': 'Enter opportunity name...'}
    )

    value = IntegerField(
        'Deal Value',
        validators=[Optional(), NumberRange(min=0)],
        render_kw={'placeholder': 'Enter deal value...', 'min': 0}
    )

    probability = IntegerField(
        'Win Probability (%)',
        validators=[Optional(), NumberRange(min=0, max=100)],
        render_kw={'placeholder': '0-100', 'min': 0, 'max': 100},
        default=0
    )

    priority = SelectField(
        'Priority',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    expected_close_date = DateField(
        'Expected Close Date',
        validators=[Optional()],
        render_kw={'placeholder': 'Select date...'}
    )

    stage = SelectField(
        'Pipeline Stage',
        validators=[Optional()],
        choices=[],  # Will be populated in __init__
        default='prospect'
    )

    company_id = SelectField(
        'Company',
        validators=[DataRequired()],
        choices=[],  # Will be populated in __init__
        coerce=safe_int_coerce
    )

    def get_fields(self):
        """Return field names to display in modal"""
        return ['name', 'company_id', 'value', 'stage']