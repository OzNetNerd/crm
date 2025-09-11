"""
Dynamic Form Builder System

This module provides utilities to dynamically build WTForms from model metadata,
eliminating the need for hardcoded form field choices and configurations.
"""

from typing import Dict, List, Any, Optional, Type
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    IntegerField,
    DecimalField,
    DateField,
    BooleanField,
    SelectMultipleField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    NumberRange,
    URL,
    Optional as OptionalValidator,
)
from app.utils.model_introspection import ModelIntrospector
from app.models import db


class DynamicFormBuilder:
    """
    Builds WTForms dynamically from model metadata, ensuring forms stay
    synchronized with model configurations without duplication.
    """
    
    @staticmethod
    def build_select_field(model_class, field_name: str, **kwargs) -> SelectField:
        """
        Build a SelectField from model metadata.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field
            **kwargs: Additional arguments for the SelectField
            
        Returns:
            Configured SelectField
        """
        choices = ModelIntrospector.get_field_choices(model_class, field_name)
        
        # Get field info for additional configuration
        field_info = getattr(model_class, field_name, None)
        if field_info and hasattr(field_info.property, 'columns'):
            info = field_info.property.columns[0].info
            
            # Set display label
            label = kwargs.get('label', info.get('display_label', field_name.replace('_', ' ').title()))
            
            # Set validators - merge with any provided in kwargs
            validators = kwargs.pop('validators', [])
            if not validators:
                if info.get('required', False):
                    validators.append(DataRequired())
                else:
                    validators.append(OptionalValidator())
                
            # Add empty choice if optional
            if not info.get('required', False) and choices:
                choices = [('', f"Select {label.lower()}")] + choices
            
            return SelectField(
                label=label,
                choices=choices,
                validators=validators,
                **kwargs
            )
        
        return SelectField(choices=choices, **kwargs)
    
    @staticmethod
    def build_string_field(model_class, field_name: str, **kwargs) -> StringField:
        """
        Build a StringField from model metadata.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field
            **kwargs: Additional arguments for the StringField
            
        Returns:
            Configured StringField
        """
        field_info = getattr(model_class, field_name, None)
        if field_info and hasattr(field_info.property, 'columns'):
            column = field_info.property.columns[0]
            info = column.info or {}  # Handle empty info or {}  # Handle empty info
            
            # Set display label
            label = kwargs.get('label', info.get('display_label', field_name.replace('_', ' ').title()))
            
            # Set validators
            validators = []
            if info.get('required', False) or not column.nullable:
                validators.append(DataRequired())
            else:
                validators.append(OptionalValidator())
                
            # Add length validator from column definition
            if hasattr(column.type, 'length') and column.type.length:
                validators.append(Length(max=column.type.length))
                
            # Add email validator for email fields
            if 'email' in field_name.lower() or (info.get('contact_field') and 'email' in field_name):
                validators.append(Email())
                
            # Add URL validator for URL fields
            if 'url' in field_name.lower() or 'website' in field_name.lower() or info.get('url_field'):
                validators.append(URL())
            
            # Set render_kw for additional attributes
            render_kw = kwargs.get('render_kw', {})
            if info.get('contact_field'):
                render_kw.setdefault('placeholder', f'Enter {label.lower()}...')
            
            # Handle textarea fields (Text column type should be textarea)
            if isinstance(column.type, db.Text):
                from wtforms import TextAreaField
                return TextAreaField(
                    label=label,
                    validators=validators,
                    render_kw=render_kw,
                    **{k: v for k, v in kwargs.items() if k not in ['label', 'render_kw']}
                )
            
            return StringField(
                label=label,
                validators=validators,
                render_kw=render_kw,
                **{k: v for k, v in kwargs.items() if k not in ['label', 'render_kw']}
            )
        
        return StringField(**kwargs)
    
    @staticmethod
    def build_integer_field(model_class, field_name: str, **kwargs) -> IntegerField:
        """
        Build an IntegerField from model metadata.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field
            **kwargs: Additional arguments for the IntegerField
            
        Returns:
            Configured IntegerField
        """
        field_info = getattr(model_class, field_name, None)
        if field_info and hasattr(field_info.property, 'columns'):
            column = field_info.property.columns[0]
            info = column.info or {}  # Handle empty info
            
            # Set display label
            label = kwargs.get('label', info.get('display_label', field_name.replace('_', ' ').title()))
            
            # Set validators
            validators = []
            if info.get('required', False) or not column.nullable:
                validators.append(DataRequired())
            else:
                validators.append(OptionalValidator())
                
            # Add number range validator from metadata
            min_value = info.get('min_value')
            max_value = info.get('max_value')
            if min_value is not None or max_value is not None:
                validators.append(NumberRange(min=min_value, max=max_value))
            
            # Set render_kw for additional attributes
            render_kw = kwargs.get('render_kw', {})
            if min_value is not None:
                render_kw['min'] = min_value
            if max_value is not None:
                render_kw['max'] = max_value
            if info.get('unit'):
                render_kw.setdefault('placeholder', f"Enter {label.lower()} in {info['unit']}")
            
            return IntegerField(
                label=label,
                validators=validators,
                render_kw=render_kw,
                **{k: v for k, v in kwargs.items() if k not in ['label', 'render_kw']}
            )
        
        return IntegerField(**kwargs)
    
    @staticmethod
    def build_date_field(model_class, field_name: str, **kwargs) -> DateField:
        """
        Build a DateField from model metadata.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field
            **kwargs: Additional arguments for the DateField
            
        Returns:
            Configured DateField
        """
        field_info = getattr(model_class, field_name, None)
        if field_info and hasattr(field_info.property, 'columns'):
            column = field_info.property.columns[0]
            info = column.info or {}  # Handle empty info
            
            # Set display label
            label = kwargs.get('label', info.get('display_label', field_name.replace('_', ' ').title()))
            
            # Set validators
            validators = []
            if info.get('required', False) or not column.nullable:
                validators.append(DataRequired())
            else:
                validators.append(OptionalValidator())
            
            return DateField(
                label=label,
                validators=validators,
                **kwargs
            )
        
        return DateField(**kwargs)
    
    @classmethod
    def build_dynamic_form(cls, model_class, base_form_class: Type[FlaskForm] = None) -> Type[FlaskForm]:
        """
        Build a complete dynamic form class from model metadata.
        
        Args:
            model_class: SQLAlchemy model class
            base_form_class: Base form class to inherit from (defaults to FlaskForm)
            
        Returns:
            Dynamically created form class
        """
        if base_form_class is None:
            base_form_class = FlaskForm
        
        # Create dynamic form class
        form_name = f"Dynamic{model_class.__name__}Form"
        form_attrs = {}
        
        # Process each column in the model
        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)
            if hasattr(attr, 'property') and hasattr(attr.property, 'columns'):
                column = attr.property.columns[0]
                info = column.info
                
                # Skip fields that are marked as non-form fields
                if info and info.get('form_exclude', False):
                    continue
                
                # Skip system fields
                if attr_name in ['id', 'created_at', 'updated_at']:
                    continue
                
                # Determine field type and create appropriate field
                if info.get('choices'):
                    form_attrs[attr_name] = cls.build_select_field(model_class, attr_name)
                elif isinstance(column.type, db.Integer):
                    form_attrs[attr_name] = cls.build_integer_field(model_class, attr_name)
                elif isinstance(column.type, db.Date):
                    form_attrs[attr_name] = cls.build_date_field(model_class, attr_name)
                else:
                    # Default to StringField
                    form_attrs[attr_name] = cls.build_string_field(model_class, attr_name)
        
        # Create and return the dynamic form class
        return type(form_name, (base_form_class,), form_attrs)
    
    @staticmethod
    def get_form_choices_api_data(model_class) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get form choices data formatted for API consumption.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            Dict mapping field names to choice data
        """
        choices_data = {}
        
        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)
            if hasattr(attr, 'property') and hasattr(attr.property, 'columns'):
                column = attr.property.columns[0]
                info = column.info
                
                choices_config = info.get('choices', {})
                if choices_config:
                    # Convert choices to API format
                    choices_data[attr_name] = [
                        {
                            'value': value,
                            'label': config['label'],
                            'css_class': config.get('css_class', ''),
                            'icon': config.get('icon', ''),
                            'description': config.get('description', ''),
                            'order': config.get('order', 999)
                        }
                        for value, config in choices_config.items()
                    ]
                    
                    # Sort by order
                    choices_data[attr_name].sort(key=lambda x: x['order'])
        
        return choices_data


# Convenience function for backward compatibility
def create_form_for_model(model_class, base_form_class: Type[FlaskForm] = None) -> Type[FlaskForm]:
    """
    Create a dynamic form class for a model.
    
    Args:
        model_class: SQLAlchemy model class
        base_form_class: Base form class to inherit from
        
    Returns:
        Dynamically created form class
    """
    return DynamicFormBuilder.build_dynamic_form(model_class, base_form_class)