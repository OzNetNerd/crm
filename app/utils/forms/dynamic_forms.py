"""
Universal Dynamic Form Generator

Creates WTForms dynamically from model column metadata.
Single source of truth - no more duplicate form definitions.
"""

from typing import Type, Dict, Any, List
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, IntegerField, SelectField,
    DateField, BooleanField, FloatField
)
from wtforms.validators import (
    DataRequired, Optional as OptionalValidator, Email, URL,
    Length, NumberRange
)
from sqlalchemy import Column
from app.forms.base.base_forms import BaseForm


def _get_field_type(column: Column):
    """Get WTForms field type from column"""
    info = column.info or {}

    # Choices = SelectField
    if info.get('choices'):
        return SelectField

    # Text with rows = TextAreaField
    if info.get('rows', 1) > 1:
        return TextAreaField

    # Column type mapping
    column_type = str(column.type).lower()
    if 'integer' in column_type:
        return IntegerField
    if 'float' in column_type or 'numeric' in column_type:
        return FloatField
    if 'boolean' in column_type:
        return BooleanField
    if 'date' in column_type:
        return DateField

    return StringField


def _get_validators(column: Column) -> List:
    """Get validators from column"""
    info = column.info or {}
    validators = []

    # Required or optional
    if not column.nullable and info.get('required', True):
        validators.append(DataRequired())
    else:
        validators.append(OptionalValidator())

    # Length from column type
    if hasattr(column.type, 'length') and column.type.length:
        validators.append(Length(max=column.type.length))

    # Special validators
    if info.get('email_field'):
        validators.append(Email())
    if info.get('url_field'):
        validators.append(URL())

    return validators


def _get_render_kw(column: Column) -> Dict[str, Any]:
    """Get render_kw from column info"""
    info = column.info or {}
    render_kw = {}

    # Placeholder
    if info.get('placeholder'):
        render_kw['placeholder'] = info['placeholder']
    elif not info.get('choices'):
        label = info.get('display_label', column.name.replace('_', ' ').title())
        render_kw['placeholder'] = f"Enter {label.lower()}..."

    # Rows for textarea
    if info.get('rows'):
        render_kw['rows'] = info['rows']

    # Input types
    if info.get('email_field'):
        render_kw['type'] = 'email'
    elif info.get('url_field'):
        render_kw['type'] = 'url'
    elif info.get('contact_field'):
        render_kw['type'] = 'tel'
    elif 'date' in str(column.type).lower():
        render_kw['type'] = 'date'

    return render_kw


def create_dynamic_form(model_class: Type, mode: str = 'full') -> Type[FlaskForm]:
    """Create WTForms class from model column metadata"""
    fields = {}

    for column in model_class.__table__.columns:
        info = column.info or {}

        # Skip system fields and non-form fields
        if column.name in ['id', 'created_at', 'updated_at']:
            continue
        if not info.get('form_include', True):
            continue
        if mode == 'modal' and not info.get('modal_include', True):
            continue

        # Create field
        field_class = _get_field_type(column)
        validators = _get_validators(column)
        label = info.get('display_label', column.name.replace('_', ' ').title())
        render_kw = _get_render_kw(column)

        # Handle choices
        field_kwargs = {'label': label, 'validators': validators}
        if render_kw:
            field_kwargs['render_kw'] = render_kw

        if field_class == SelectField and info.get('choices'):
            choices = model_class.get_field_choices(column.name)
            field_kwargs['choices'] = [('', f"Select {label}")] + choices

        fields[column.name] = field_class(**field_kwargs)

    return type(f"{model_class.__name__}Form", (BaseForm,), fields)


def get_form_config_json(model_class: Type, mode: str = 'create') -> Dict[str, Any]:
    """Generate JSON form config from model metadata"""
    fields = []

    for column in model_class.__table__.columns:
        info = column.info or {}

        # Skip system and non-form fields
        if column.name in ['id', 'created_at', 'updated_at']:
            continue
        if not info.get('form_include', True):
            continue

        # Build field config
        label = info.get('display_label', column.name.replace('_', ' ').title())
        field_config = {
            'name': column.name,
            'label': label,
            'type': _get_api_field_type(column),
            'required': not column.nullable and info.get('required', True)
        }

        # Add attributes
        if info.get('placeholder'):
            field_config['placeholder'] = info['placeholder']
        elif not info.get('choices'):
            field_config['placeholder'] = f"Enter {label.lower()}"

        if info.get('rows'):
            field_config['rows'] = info['rows']

        # Add choices
        if info.get('choices'):
            choices = model_class.get_field_choices(column.name)
            field_config['options'] = [{'value': '', 'label': f"Select {label}"}]
            field_config['options'].extend([
                {'value': value, 'label': label} for value, label in choices
            ])

        fields.append(field_config)

    return {
        'title': f"{mode.title()} {model_class.__name__}",
        'fields': fields
    }


def _get_api_field_type(column: Column) -> str:
    """Get API field type string from column"""
    info = column.info or {}

    if info.get('choices'):
        return 'select'
    if info.get('rows', 1) > 1:
        return 'textarea'
    if info.get('email_field'):
        return 'email'
    if info.get('url_field'):
        return 'url'
    if info.get('contact_field'):
        return 'tel'

    column_type = str(column.type).lower()
    if 'date' in column_type:
        return 'date'
    if 'integer' in column_type or 'float' in column_type:
        return 'number'

    return 'text'