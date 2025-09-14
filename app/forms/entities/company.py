"""
Company Forms

Simple company form using WTForms with model introspection.
"""

from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, URL, Length
from ..base.base_forms import BaseForm
# ModelIntrospector removed - use model methods directly


class CompanyForm(BaseForm):
    """Unified form for creating and editing companies - supports both full and modal modes"""

    def __init__(self, *args, modal_mode=False, **kwargs):
        self.modal_mode = modal_mode
        super().__init__(*args, **kwargs)

        # Set industry choices from model metadata
        from app.models.company import Company
        industry_choices = Company.get_field_choices('industry')
        self.industry.choices = [('', 'Select industry')] + industry_choices

        if not modal_mode:
            # Only set size choices for full forms
            size_choices = Company.get_field_choices('size')
            self.size.choices = [('', 'Select size')] + size_choices

    name = StringField(
        'Company Name',
        validators=[DataRequired(), Length(max=255)]
    )

    industry = SelectField(
        'Industry',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    website = StringField(
        'Website',
        validators=[Optional(), URL()]
    )

    size = SelectField(
        'Company Size',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    phone = StringField(
        'Phone',
        validators=[Optional(), Length(max=50)]
    )

    address = TextAreaField(
        'Address',
        validators=[Optional()],
        render_kw={'rows': 2}
    )

    comments = TextAreaField(
        'Comments',
        validators=[Optional()],
        render_kw={'rows': 3}
    )

    def get_modal_fields(self):
        """Return field names to display in modal mode"""
        return ['name', 'industry', 'comments']

    def get_full_fields(self):
        """Return field names to display in full form mode"""
        return ['name', 'industry', 'website', 'size', 'phone', 'address']