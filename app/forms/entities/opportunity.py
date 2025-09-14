"""
Opportunity Forms

Simple opportunity form using WTForms with model introspection.
"""

from wtforms import StringField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from ..base.base_forms import BaseForm


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

    company = StringField('Company', validators=[DataRequired()])

    def get_fields(self):
        """Return field names to display in modal"""
        return ['name', 'company', 'value', 'stage']