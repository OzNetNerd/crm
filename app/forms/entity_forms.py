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


# Lazy form creation with caching
_form_cache = {}

def get_company_form():
    """Get dynamically generated CompanyForm (lazy with caching)"""
    if 'CompanyForm' not in _form_cache:
        from app.models.company import Company
        _form_cache['CompanyForm'] = DynamicFormBuilder.build_dynamic_form(Company, BaseForm)
    return _form_cache['CompanyForm']

def get_stakeholder_form():
    """Get dynamically generated StakeholderForm (lazy with caching)"""
    if 'StakeholderForm' not in _form_cache:
        from app.models.stakeholder import Stakeholder
        _form_cache['StakeholderForm'] = DynamicFormBuilder.build_dynamic_form(Stakeholder, BaseForm)
    return _form_cache['StakeholderForm']

def get_opportunity_form():
    """Get dynamically generated OpportunityForm (lazy with caching)"""
    if 'OpportunityForm' not in _form_cache:
        from app.models.opportunity import Opportunity
        _form_cache['OpportunityForm'] = DynamicFormBuilder.build_dynamic_form(Opportunity, BaseForm)
    return _form_cache['OpportunityForm']

# Backward compatibility - these will be created lazily when accessed
def __getattr__(name):
    if name == 'CompanyForm':
        return get_company_form()
    elif name == 'StakeholderForm':
        return get_stakeholder_form()
    elif name == 'OpportunityForm':
        return get_opportunity_form()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


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