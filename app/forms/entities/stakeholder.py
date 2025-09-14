"""
Stakeholder Forms

Simple stakeholder form using WTForms with model introspection.
"""

from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Optional, Email, Length
from ..base.base_forms import BaseForm
# ModelIntrospector removed - use model methods directly
from app.utils.forms.helpers import safe_int_coerce


class StakeholderForm(BaseForm):
    """Form for creating and editing stakeholders in modals"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set choices from model metadata
        from app.models.stakeholder import Stakeholder

        # Set MEDDPICC choices
        meddpicc_choices = Stakeholder.get_field_choices('meddpicc_role')
        self.meddpicc_role.choices = [('', 'Select MEDDPICC role')] + meddpicc_choices

        # Set company choices
        from app.models.company import Company
        companies = Company.query.order_by(Company.name).all()
        self.company_id.choices = [('', 'Select company')] + [
            (str(company.id), company.name) for company in companies
        ]

    name = StringField(
        'Full Name',
        validators=[DataRequired(), Length(max=255)],
        render_kw={'placeholder': 'Enter stakeholder name...'}
    )

    job_title = StringField(
        'Job Title',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Enter job title...'}
    )

    email = StringField(
        'Email Address',
        validators=[Optional(), Email(), Length(max=255)],
        render_kw={'placeholder': 'Enter email address...'}
    )

    phone = StringField(
        'Phone Number',
        validators=[Optional(), Length(max=50)],
        render_kw={'placeholder': 'Enter phone number...'}
    )

    meddpicc_role = SelectField(
        'MEDDPICC Role',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    company_id = SelectField(
        'Company',
        validators=[DataRequired()],
        choices=[],  # Will be populated in __init__
        coerce=safe_int_coerce
    )

    def get_fields(self):
        """Return field names to display in modal"""
        return ['name', 'email', 'company_id']