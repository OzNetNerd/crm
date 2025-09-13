"""
Unified Form Builder System

This module combines dynamic form building and configuration management,
eliminating duplication between backend forms and frontend template configs.
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
    Field,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    NumberRange,
    URL,
    Optional as OptionalValidator,
)
from app.utils.core.model_introspection import ModelIntrospector
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
            info = column.info or {}  # Handle empty info
            
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
    def _should_include_field_in_form(cls, model_class, attr_name: str, info: dict) -> bool:
        """
        Determine if a field should be included in the form.

        Uses form_include whitelist approach when available, falls back to form_exclude blacklist.

        Args:
            model_class: SQLAlchemy model class
            attr_name: Name of the field attribute
            info: Field info dictionary

        Returns:
            True if field should be included in form, False otherwise
        """
        # Check if model uses form_include whitelist approach
        has_form_include_fields = any(
            hasattr(getattr(model_class, name, None), 'property') and
            hasattr(getattr(model_class, name).property, 'columns') and
            getattr(model_class, name).property.columns[0].info and
            getattr(model_class, name).property.columns[0].info.get('form_include')
            for name in dir(model_class)
            if hasattr(getattr(model_class, name, None), 'property')
        )

        if has_form_include_fields:
            # Whitelist mode: only include fields explicitly marked with form_include=True
            return info and info.get('form_include', False)
        else:
            # Blacklist mode: include all fields except those marked with form_exclude=True
            return not (info and info.get('form_exclude', False))

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

                # Skip system fields
                if attr_name in ['id', 'created_at', 'updated_at']:
                    continue

                # Check if field should be included in form
                if not cls._should_include_field_in_form(model_class, attr_name, info):
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


class FormConfigManager:
    """
    DRY Form Configuration Manager

    Generates dynamic form configurations from WTForms definitions,
    eliminating duplication between backend and frontend.
    """

    # Field type mapping - single source of truth
    FIELD_TYPE_MAP = {
        StringField: "text",
        TextAreaField: "textarea",
        SelectField: "select",
        SelectMultipleField: "multiselect",
        IntegerField: "number",
        DecimalField: "number",
        DateField: "date",
        BooleanField: "checkbox",
    }

    # Validator type mapping - DRY validation rules
    VALIDATOR_TYPE_MAP = {
        DataRequired: "required",
        Length: "length",
        Email: "email",
        NumberRange: "number_range",
        URL: "url",
    }

    @classmethod
    def get_form_config(
        cls, form_class: FlaskForm, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate complete form configuration from WTForms class.

        Args:
            form_class: The FlaskForm class to analyze
            context: Optional context for dynamic choices (user_id, company_id, etc.)

        Returns:
            Complete form configuration dictionary
        """
        config = {
            "entity_type": cls._get_entity_type(form_class.__name__),
            "title": cls._get_form_title(form_class.__name__),
            "fields": [],
            "validation_rules": {},
            "choices": {},
        }

        # Process each field in the form
        # Get fields from the form class by checking for Field instances
        form_fields = {}
        for attr_name in dir(form_class):
            attr = getattr(form_class, attr_name)
            # Check if this is a WTForms field
            if hasattr(attr, '__class__') and hasattr(attr.__class__, '__mro__'):
                # Check if it's a subclass of Field
                from wtforms import Field
                if any(Field in base.__mro__ for base in attr.__class__.__mro__):
                    form_fields[attr_name] = attr
            
        for field_name, field in form_fields.items():
            field_config = cls._get_field_config(field_name, field, context)
            config["fields"].append(field_config)

            # Extract validation rules
            if field.validators:
                config["validation_rules"][field_name] = cls._get_validation_rules(
                    field.validators
                )

            # Extract choices for select fields
            if hasattr(field, "choices") and field.choices:
                config["choices"][field_name] = cls._get_field_choices(field, context)

        return config

    @classmethod
    def _get_field_config(
        cls, field_name: str, field: Field, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Extract configuration for a single field - DRY approach"""
        field_type = type(field)

        config = {
            "name": field_name,
            "type": cls.FIELD_TYPE_MAP.get(field_type, "text"),
            "label": (
                field.label.text
                if field.label
                else field_name.replace("_", " ").title()
            ),
            "required": cls._is_required(field.validators),
            "placeholder": cls._get_placeholder(field),
        }

        # Add type-specific attributes
        if field_type == TextAreaField:
            config["rows"] = getattr(field, "render_kw", {}).get("rows", 3)

        elif field_type in [IntegerField, DecimalField]:
            render_kw = getattr(field, "render_kw", {})
            if "min" in render_kw:
                config["min"] = render_kw["min"]
            if "max" in render_kw:
                config["max"] = render_kw["max"]
            if "step" in render_kw:
                config["step"] = render_kw["step"]

        elif field_type in [SelectField, SelectMultipleField]:
            config["choices"] = cls._get_field_choices(field, context)

        return config

    @classmethod
    def _get_validation_rules(cls, validators: List) -> Dict[str, Any]:
        """Extract validation rules from WTForms validators - DRY validation"""
        rules = {}

        for validator in validators:
            validator_type = type(validator)

            if validator_type == DataRequired:
                rules["required"] = True

            elif validator_type == Length:
                if hasattr(validator, "min") and validator.min is not None:
                    rules["min_length"] = validator.min
                if hasattr(validator, "max") and validator.max is not None:
                    rules["max_length"] = validator.max

            elif validator_type == NumberRange:
                if hasattr(validator, "min") and validator.min is not None:
                    rules["min_value"] = validator.min
                if hasattr(validator, "max") and validator.max is not None:
                    rules["max_value"] = validator.max

            elif validator_type == Email:
                rules["email"] = True

            elif validator_type == URL:
                rules["url"] = True

        return rules

    @classmethod
    def _get_field_choices(
        cls, field: Field, context: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """Get choices for select fields - supports dynamic choices"""
        if not hasattr(field, "choices"):
            return []

        choices = []
        for choice in field.choices:
            if isinstance(choice, (tuple, list)) and len(choice) == 2:
                choices.append({"value": str(choice[0]), "label": str(choice[1])})
            else:
                # Simple string choice
                choices.append({"value": str(choice), "label": str(choice)})

        return choices

    @classmethod
    def _is_required(cls, validators: List) -> bool:
        """Check if field is required"""
        return (
            any(isinstance(v, DataRequired) for v in validators)
            if validators
            else False
        )

    @classmethod
    def _get_placeholder(cls, field: Field) -> str:
        """Extract placeholder from field render_kw"""
        if hasattr(field, "render_kw") and field.render_kw:
            return field.render_kw.get("placeholder", "")
        return ""

    @classmethod
    def _get_entity_type(cls, form_name: str) -> str:
        """Extract entity type from form class name"""
        return form_name.replace("Form", "").lower()

    @classmethod
    def _get_form_title(cls, form_name: str) -> str:
        """Generate form title from class name"""
        entity_type = cls._get_entity_type(form_name)
        return f"{entity_type.replace('_', ' ').title()} Details"


class DynamicChoiceProvider:
    """
    Provides dynamic choices for form fields based on database state.
    Eliminates hardcoded choices and enables real-time data.
    """

    @staticmethod
    def get_company_choices() -> List[Dict[str, str]]:
        """Get all companies for select fields"""
        from app.models import Company

        companies = Company.query.order_by(Company.name).all()
        return [{"value": str(c.id), "label": c.name} for c in companies]

    @staticmethod
    def get_user_choices() -> List[Dict[str, str]]:
        """Get all users for select fields"""
        from app.models import User

        users = User.query.order_by(User.name).all()
        return [
            {"value": str(u.id), "label": f"{u.name} ({u.job_title})"} for u in users
        ]

    @staticmethod
    def get_stakeholder_choices(
        company_id: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """Get stakeholders, optionally filtered by company"""
        from app.models import Stakeholder

        query = Stakeholder.query
        if company_id:
            query = query.filter_by(company_id=company_id)
        stakeholders = query.order_by(Stakeholder.name).all()
        return [
            {"value": str(s.id), "label": f"{s.name} ({s.job_title})"}
            for s in stakeholders
        ]

    @staticmethod
    def get_meddpicc_role_choices() -> List[Dict[str, str]]:
        """Get MEDDPICC role options - using direct model introspection"""
        from app.models import Stakeholder
        from app.utils.core.model_introspection import ModelIntrospector
        return [
            {"value": value, "label": label} 
            for value, label in ModelIntrospector.get_field_choices(Stakeholder, 'meddpicc_role')
        ]

    @staticmethod
    def get_industry_choices() -> List[Dict[str, str]]:
        """Get industry options - using direct model introspection"""
        from app.models import Company
        from app.utils.core.model_introspection import ModelIntrospector
        return [
            {"value": value, "label": label} 
            for value, label in ModelIntrospector.get_field_choices(Company, 'industry')
        ]

    @staticmethod
    def get_opportunity_stage_choices() -> List[Dict[str, str]]:
        """Get opportunity stage options using model metadata"""
        from app.models import Opportunity
        from app.utils.core.model_introspection import ModelIntrospector
        
        choices = ModelIntrospector.get_field_choices(Opportunity, 'stage')
        return [{"value": "", "label": "Select stage"}] + [
            {"value": value, "label": label} 
            for value, label in choices
        ]

    @staticmethod
    def get_company_size_choices() -> List[Dict[str, str]]:
        """Get company size options that match Company.size_category property"""
        # Define constants that match the Company.size_category property logic
        COMPANY_SIZE_CHOICES = [
            {"value": "unknown", "label": "Unknown Size (0 contacts)"},
            {"value": "small", "label": "Small (1-10 contacts)"},
            {"value": "medium", "label": "Medium (11-50 contacts)"},
            {"value": "large", "label": "Large (50+ contacts)"}
        ]
        return COMPANY_SIZE_CHOICES


class DropdownConfigGenerator:
    """Ultra-DRY dropdown generator using pure model introspection"""
    
    @staticmethod
    def get_model_by_entity_name(entity_name: str):
        """Get model class from entity name - dynamic mapping from model configs"""
        from app.utils.core.model_introspection import get_all_entity_models
        
        # Build mapping dynamically from model configurations
        all_models = get_all_entity_models()
        model_map = {}
        
        for model_class in all_models:
            config = model_class.__entity_config__
            endpoint_name = config.get('endpoint_name', model_class.__tablename__)
            model_map[endpoint_name] = model_class
        
        return model_map.get(entity_name.lower())
    
    @staticmethod
    def generate_entity_dropdown_configs(entity_name: str, 
                                       group_by: str = None,
                                       sort_by: str = None, 
                                       sort_direction: str = 'asc',
                                       primary_filter: List[str] = None) -> Dict[str, Any]:
        """Generate dropdown configs using pure model introspection - no hardcoded data"""
        from app.utils.core.model_introspection import ModelIntrospector
        
        # Get model class
        model_class = DropdownConfigGenerator.get_model_by_entity_name(entity_name)
        if not model_class:
            return {}
        
        # Get options from model metadata
        group_fields = ModelIntrospector.get_groupable_fields(model_class)
        sort_fields = ModelIntrospector.get_sortable_fields(model_class)
        
        # Convert to dropdown format
        group_options = [{'value': field, 'label': label} for field, label in group_fields]
        sort_options = [{'value': field, 'label': label} for field, label in sort_fields]
        
        # Standard sort directions
        sort_direction_options = [
            {'value': 'asc', 'label': 'Ascending'},
            {'value': 'desc', 'label': 'Descending'}
        ]
        
        # Get primary filterable field (first groupable field with choices)
        filter_options = []
        filter_name = 'All Items'
        if group_fields:
            primary_field = group_fields[0][0]  # First groupable field
            choices = ModelIntrospector.get_field_choices(model_class, primary_field)
            if choices:
                filter_options = [{"value": value, "label": label} for value, label in choices]
                # Use model's display_name (which is already plural)
                plural_label = model_class.__entity_config__.get('display_name', 'Items')
                filter_name = f'All {plural_label}'
        
        # HTMX targets using model metadata
        from app.utils.model_registry import ModelRegistry
        metadata = ModelRegistry.get_model_metadata(model_class.__name__.lower())
        singular = metadata.display_name.lower().replace(' ', '-')
        
        hx_target = f'#{singular}-content'
        hx_get = f'/{entity_name}/content'
        
        # Generate dynamic button text based on current selection
        group_button_text = 'Group by'
        if group_by and group_options:
            for option in group_options:
                if option['value'] == group_by:
                    group_button_text = f'Group by: {option["label"]}'
                    break
        elif group_options and not group_by:
            # Default to first option if no selection
            group_button_text = f'Group by: {group_options[0]["label"]}'
            
        sort_button_text = 'Sort by'
        if sort_by and sort_options:
            for option in sort_options:
                if option['value'] == sort_by:
                    sort_button_text = f'Sort by: {option["label"]}'
                    break
        elif sort_options and not sort_by:
            # Default to first option if no selection
            sort_button_text = f'Sort by: {sort_options[0]["label"]}'
        
        return {
            'group_by': {
                'button_text': group_button_text,
                'options': group_options,
                'current_value': group_by or (group_options[0]['value'] if group_options else ''),
                'name': 'group_by',
                'hx_target': hx_target,
                'hx_get': hx_get
            },
            'sort_by': {
                'button_text': sort_button_text,
                'options': sort_options, 
                'current_value': sort_by or (sort_options[0]['value'] if sort_options else ''),
                'name': 'sort_by',
                'hx_target': hx_target,
                'hx_get': hx_get
            },
            'sort_direction': {
                'button_text': 'Order',
                'options': sort_direction_options,
                'current_value': sort_direction,
                'name': 'sort_direction',
                'hx_target': hx_target,
                'hx_get': hx_get
            },
            'primary_filter': {
                'button_text': filter_name,
                'options': filter_options,
                'current_values': primary_filter or [],
                'name': 'primary_filter'
            }
        }


# All form creation now uses DynamicFormBuilder.build_dynamic_form() directly