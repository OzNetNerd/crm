"""
Company Forms

Simple company form using WTForms with model introspection.
"""

from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, URL, Length
from ..base.base_forms import BaseForm
# ModelIntrospector removed - use model methods directly


class CompanyForm(BaseForm):
    """Form for creating and editing companies in modals"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set choices from model metadata
        from app.models.company import Company
        industry_choices = Company.get_field_choices('industry')
        self.industry.choices = [('', 'Select industry')] + industry_choices

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

    def get_fields(self):
        """Return field names to display in modal"""
        return ['name', 'industry', 'comments']