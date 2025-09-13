"""
Company Forms

Simple company form using WTForms with model introspection.
"""

from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, URL, Length
from ..base.base_forms import BaseForm
from app.utils.core.model_introspection import ModelIntrospector


class CompanyForm(BaseForm):
    """Form for creating and editing companies"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set industry choices from model metadata
        from app.models.company import Company
        industry_choices = ModelIntrospector.get_field_choices(Company, 'industry')
        self.industry.choices = [('', 'Select industry')] + industry_choices

        size_choices = ModelIntrospector.get_field_choices(Company, 'size')
        self.size.choices = [('', 'Select size')] + size_choices

    name = StringField(
        'Company Name',
        validators=[DataRequired(), Length(max=255)],
        render_kw={'placeholder': 'Enter company name...'}
    )

    industry = SelectField(
        'Industry',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    website = StringField(
        'Website',
        validators=[Optional(), URL()],
        render_kw={'placeholder': 'https://...'}
    )

    size = SelectField(
        'Company Size',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    phone = StringField(
        'Phone',
        validators=[Optional(), Length(max=50)],
        render_kw={'placeholder': 'Enter phone number...'}
    )

    address = TextAreaField(
        'Address',
        validators=[Optional()],
        render_kw={'rows': 2, 'placeholder': 'Enter company address...'}
    )