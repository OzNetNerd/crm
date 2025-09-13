"""
Company Modal Form

Explicit form class for Company modals with controlled field ordering.
Replaces DynamicFormBuilder with simple, maintainable WTForms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from app.utils.core.model_introspection import ModelIntrospector
from app.models.company import Company


class CompanyModalForm(FlaskForm):
    """
    Company modal form with explicit field ordering:
    1. Company Name (required)
    2. Industry (dropdown)
    3. Comments (textarea)
    """

    # Field 1: Company Name (required, at top)
    name = StringField(
        'Company Name',
        validators=[DataRequired(), Length(max=255)],
        render_kw={'placeholder': 'Enter company name...'}
    )

    # Field 2: Industry (dropdown, middle)
    industry = SelectField(
        'Industry',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    # Field 3: Comments (textarea, at bottom)
    comments = TextAreaField(
        'Comments',
        validators=[Optional()],
        render_kw={'rows': 3, 'placeholder': 'Additional notes...'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get industry choices from model metadata
        industry_choices = ModelIntrospector.get_field_choices(Company, 'industry')

        # Add empty choice at the beginning
        choices = [('', 'Select industry')]
        choices.extend(industry_choices)

        self.industry.choices = choices