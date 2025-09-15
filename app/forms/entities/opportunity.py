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

        # Process fields that use model classes as labels
        if hasattr(self.company.label, 'text') and hasattr(self.company.label.text, '__tablename__'):
            model_class = self.company.label.text
            self.company.label.text = model_class.get_display_name()
            if not self.company.render_kw:
                self.company.render_kw = {}
            self.company.render_kw['placeholder'] = f"Search {model_class.get_display_name_plural().lower()}..."

        # Set priority choices from model metadata
        priority_choices = self.model.get_field_choices('priority')
        self.priority.choices = [('', 'Select priority')] + priority_choices

        # Set stage choices from model metadata
        stage_choices = self.model.get_field_choices('stage')
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

    # Field from Company model - uses search instead of dropdown
    company = StringField(Company, validators=[DataRequired()])

    def get_display_fields(self):
        """Return field names to display in modal, in this exact order"""
        return ['company', 'name', 'value', 'stage']
