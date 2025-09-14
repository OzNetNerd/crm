"""
Opportunity Forms

Simple opportunity form using WTForms with model introspection.
"""

from wtforms import StringField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from ..base.base_forms import BaseForm
from app.utils.core.model_introspection import ModelIntrospector
from app.utils.forms.helpers import safe_int_coerce


class OpportunityForm(BaseForm):
    """Unified form for creating and editing opportunities - supports both full and modal modes"""

    def __init__(self, *args, modal_mode=False, **kwargs):
        self.modal_mode = modal_mode
        super().__init__(*args, **kwargs)
        # Set choices from model metadata
        from app.models.opportunity import Opportunity

        if not modal_mode:
            # Only set priority choices for full forms
            priority_choices = ModelIntrospector.get_field_choices(Opportunity, 'priority')
            self.priority.choices = [('', 'Select priority')] + priority_choices

        # Set stage choices (needed for both modal and full forms)
        stage_choices = ModelIntrospector.get_field_choices(Opportunity, 'stage')
        self.stage.choices = [('', 'Select stage')] + stage_choices

        # Set company choices (needed for both modal and full forms)
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

    def get_modal_fields(self):
        """Return field names to display in modal mode"""
        return ['name', 'company_id', 'value', 'stage']

    def get_full_fields(self):
        """Return field names to display in full form mode"""
        return ['name', 'value', 'probability', 'priority', 'expected_close_date', 'stage', 'company_id']