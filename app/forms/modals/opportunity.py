"""
Opportunity Modal Form

Explicit form class for Opportunity modals with controlled field ordering.
Focuses on essential fields for quick opportunity creation.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from app.utils.core.model_introspection import ModelIntrospector
from app.models.opportunity import Opportunity
from app.models.company import Company


class OpportunityModalForm(FlaskForm):
    """
    Opportunity modal form with explicit field ordering:
    1. Name (required)
    2. Company (required dropdown)
    3. Value (optional)
    4. Stage (optional dropdown)
    """

    # Field 1: Name (required, at top)
    name = StringField(
        'Opportunity Name',
        validators=[DataRequired(), Length(max=255)],
        render_kw={'placeholder': 'Enter opportunity name...'}
    )

    # Field 2: Company (required dropdown)
    company_id = SelectField(
        'Company',
        validators=[DataRequired()],
        choices=[]  # Will be populated in __init__
    )

    # Field 3: Value (optional)
    value = IntegerField(
        'Deal Value',
        validators=[Optional(), NumberRange(min=0)],
        render_kw={'placeholder': 'Enter deal value...', 'min': 0}
    )

    # Field 4: Stage (optional dropdown)
    stage = SelectField(
        'Pipeline Stage',
        validators=[Optional()],
        choices=[],  # Will be populated in __init__
        default='prospect'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set stage choices from model metadata
        stage_choices = ModelIntrospector.get_field_choices(Opportunity, 'stage')
        self.stage.choices = [('', 'Select stage')] + stage_choices

        # Set company choices
        companies = Company.query.order_by(Company.name).all()
        self.company_id.choices = [('', 'Select company')] + [
            (str(company.id), company.name) for company in companies
        ]