from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    DecimalField,
    DateField,
    IntegerField,
)
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange, URL
from wtforms.widgets import TextArea
# Models will be imported lazily to avoid circular imports
from app.utils.forms.form_builder import DynamicFormBuilder
from app.utils.core.model_introspection import ModelIntrospector
from .base_forms import BaseForm, FieldFactory, FormConstants


# Dynamic form generation from model metadata
def _get_company_form():
    """Get dynamically generated CompanyForm"""
    from app.models.company import Company
    return DynamicFormBuilder.build_dynamic_form(Company, BaseForm)

def _get_company_form_instance():
    """Get instance of dynamically generated CompanyForm"""
    CompanyForm = _get_company_form()
    return CompanyForm()

# Export the form class dynamically
CompanyForm = _get_company_form()


# Dynamic StakeholderForm generation
def _get_stakeholder_form():
    """Get dynamically generated StakeholderForm"""
    from app.models.stakeholder import Stakeholder
    return DynamicFormBuilder.build_dynamic_form(Stakeholder, BaseForm)

StakeholderForm = _get_stakeholder_form()


# Dynamic OpportunityForm generation
def _get_opportunity_form():
    """Get dynamically generated OpportunityForm"""
    from app.models.opportunity import Opportunity
    return DynamicFormBuilder.build_dynamic_form(Opportunity, BaseForm)

OpportunityForm = _get_opportunity_form()


# NoteForm with custom logic preserved
class NoteForm(BaseForm):
    content = TextAreaField(
        "Note Content",
        validators=[DataRequired(), Length(min=1, max=FormConstants.NOTE_MAX_LENGTH)],
        render_kw={
            "placeholder": "Enter your note...",
            "rows": 4
        }
    )

    is_internal = SelectField(
        "Note Type",
        choices=[
            ("1", "Internal Note"),
            ("0", "Client-Facing Note")
        ],
        default="1",
        coerce=lambda x: x == "1"
    )