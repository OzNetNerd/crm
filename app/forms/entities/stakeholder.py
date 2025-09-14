"""
Stakeholder Forms

Simple stakeholder form using WTForms with model introspection.
"""

from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Optional, Email, Length
from ..base.base_forms import BaseForm
from app.utils.core.model_introspection import ModelIntrospector


class StakeholderForm(BaseForm):
    """Unified form for creating and editing stakeholders - supports both full and modal modes"""

    def __init__(self, *args, modal_mode=False, **kwargs):
        self.modal_mode = modal_mode
        super().__init__(*args, **kwargs)
        # Set choices from model metadata
        from app.models.stakeholder import Stakeholder

        if not modal_mode:
            # Only set MEDDPICC choices for full forms
            meddpicc_choices = ModelIntrospector.get_field_choices(Stakeholder, 'meddpicc_role')
            self.meddpicc_role.choices = [('', 'Select MEDDPICC role')] + meddpicc_choices

        # Set company choices (needed for both modal and full forms)
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
        coerce=int
    )

    def get_modal_fields(self):
        """Return field names to display in modal mode"""
        return ['name', 'email', 'company_id']

    def get_full_fields(self):
        """Return field names to display in full form mode"""
        return ['name', 'job_title', 'email', 'phone', 'meddpicc_role', 'company_id']