"""
Company Forms

Simple company form using WTForms with model introspection.
"""

from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, URL, Length
from ..base.base_forms import BaseForm
from app.utils.core.model_introspection import ModelIntrospector


class CompanyForm(BaseForm):
    """Unified form for creating and editing companies - supports both full and modal modes"""

    def __init__(self, *args, modal_mode=False, **kwargs):
        self.modal_mode = modal_mode
        super().__init__(*args, **kwargs)

        # Set industry choices from model metadata
        from app.models.company import Company
        industry_choices = ModelIntrospector.get_field_choices(Company, 'industry')
        self.industry.choices = [('', 'Select industry')] + industry_choices

        if not modal_mode:
            # Only set size choices for full forms
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

    comments = TextAreaField(
        'Comments',
        validators=[Optional()],
        render_kw={'rows': 3, 'placeholder': 'Additional notes...'}
    )

    def get_modal_fields(self):
        """Return field names to display in modal mode"""
        return ['name', 'industry', 'comments']

    def get_full_fields(self):
        """Return field names to display in full form mode"""
        return ['name', 'industry', 'website', 'size', 'phone', 'address']