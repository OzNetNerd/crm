"""
Stakeholder Modal Form

Explicit form class for Stakeholder modals with controlled field ordering.
Focuses on essential fields for quick stakeholder creation.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Email
from app.utils.core.model_introspection import ModelIntrospector
from app.models.stakeholder import Stakeholder
from app.models.company import Company


class StakeholderModalForm(FlaskForm):
    """
    Stakeholder modal form with explicit field ordering:
    1. Name (required)
    2. Email (optional)
    3. Company (required dropdown)
    """

    # Field 1: Name (required, at top)
    name = StringField(
        'Full Name',
        validators=[DataRequired(), Length(max=255)],
        render_kw={'placeholder': 'Enter stakeholder name...'}
    )

    # Field 2: Email (optional, middle)
    email = StringField(
        'Email Address',
        validators=[Optional(), Email(), Length(max=255)],
        render_kw={'placeholder': 'Enter email address...'}
    )

    # Field 3: Company (required dropdown, at bottom)
    company_id = SelectField(
        'Company',
        validators=[DataRequired()],
        choices=[]  # Will be populated in __init__
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set company choices
        companies = Company.query.order_by(Company.name).all()
        self.company_id.choices = [('', 'Select company')] + [
            (str(company.id), company.name) for company in companies
        ]