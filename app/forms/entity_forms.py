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

# Dynamic form configuration - maps form names to model imports
_DYNAMIC_FORMS = {
    'CompanyForm': 'app.models.company.Company',
    'StakeholderForm': 'app.models.stakeholder.Stakeholder', 
    'OpportunityForm': 'app.models.opportunity.Opportunity',
}

def _get_dynamic_form(form_name):
    """Generic lazy form creation with caching"""
    if form_name not in _form_cache:
        if form_name not in _DYNAMIC_FORMS:
            raise ValueError(f"Unknown dynamic form: {form_name}")
        
        # Dynamic import of model class
        module_path, class_name = _DYNAMIC_FORMS[form_name].rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        model_class = getattr(module, class_name)
        
        _form_cache[form_name] = DynamicFormBuilder.build_dynamic_form(model_class, BaseForm)
    return _form_cache[form_name]

def __getattr__(name):
    """Lazy form creation for backward compatibility"""
    if name in _DYNAMIC_FORMS:
        return _get_dynamic_form(name)
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