"""
Dynamic Form Configuration System - Single Source of Truth

This module provides a DRY approach to form configuration by automatically 
generating JSON configurations from WTForms definitions. No more duplication
between backend forms and frontend template configs.
"""

from typing import Dict, List, Any, Optional
from flask_wtf import FlaskForm
from wtforms import Field
from wtforms.fields import (
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
)
# Removed constants import - now using model introspection


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
        for field_name, field in form_class._formfields.items():
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
        from app.utils.model_introspection import ModelIntrospector
        return [
            {"value": value, "label": label} 
            for value, label in ModelIntrospector.get_field_choices(Stakeholder, 'meddpicc_role')
        ]

    @staticmethod
    def get_industry_choices() -> List[Dict[str, str]]:
        """Get industry options - using direct model introspection"""
        from app.models import Company
        from app.utils.model_introspection import ModelIntrospector
        return [
            {"value": value, "label": label} 
            for value, label in ModelIntrospector.get_field_choices(Company, 'industry')
        ]

    @staticmethod
    def get_opportunity_stage_choices() -> List[Dict[str, str]]:
        """Get opportunity stage options using model metadata"""
        from app.models import Opportunity
        from app.utils.model_introspection import ModelIntrospector
        
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
        """Get model class from entity name"""
        from app.models import Company, Task, Opportunity, Stakeholder, User
        
        model_map = {
            'companies': Company,
            'tasks': Task, 
            'opportunities': Opportunity,
            'stakeholders': Stakeholder,
            'teams': User  # Teams manage User entities
        }
        return model_map.get(entity_name.lower())
    
    @staticmethod
    def generate_entity_dropdown_configs(entity_name: str, 
                                       group_by: str = None,
                                       sort_by: str = None, 
                                       sort_direction: str = 'asc',
                                       primary_filter: List[str] = None) -> Dict[str, Any]:
        """Generate dropdown configs using pure model introspection - no hardcoded data"""
        from app.utils.model_introspection import ModelIntrospector
        
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
        # Plural mapping for proper English
        plural_map = {
            'opportunity': 'opportunities',
            'company': 'companies', 
            'category': 'categories',
            'activity': 'activities',
            'entity': 'entities',
            'priority': 'priorities',
            'industry': 'industries',
            'stakeholder': 'stakeholders',
            'task': 'tasks',
            'note': 'notes'
        }
        
        filter_options = []
        filter_name = 'All Items'
        if group_fields:
            primary_field = group_fields[0][0]  # First groupable field
            choices = ModelIntrospector.get_field_choices(model_class, primary_field)
            if choices:
                filter_options = [{"value": value, "label": label} for value, label in choices]
                field_label = group_fields[0][1]
                plural_label = plural_map.get(field_label.lower(), field_label + 's')
                filter_name = f'All {plural_label.title()}'
        
        # HTMX targets using proper singular mapping
        singular_map = {
            'companies': 'company',
            'tasks': 'task',
            'opportunities': 'opportunity', 
            'stakeholders': 'stakeholder',
            'teams': 'team'
        }
        singular = singular_map.get(entity_name, entity_name)
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


class EntityConfigGenerator:
    """Ultra-DRY entity configuration generator using model introspection and metadata"""
    
    @staticmethod
    def generate_entity_page_config(entity_name: str, model_class=None) -> Dict[str, Any]:
        """Generate complete entity page configuration from model metadata"""
        
        # Get model class if not provided
        if not model_class:
            model_class = DropdownConfigGenerator.get_model_by_entity_name(entity_name)
            if not model_class:
                raise ValueError(f"Unknown entity: {entity_name}")
        
        # Get entity config from model
        entity_config = getattr(model_class, '__entity_config__', {})
        
        # Use centralized entity icon system
        from app.utils.entity_icons import get_entity_icon_html
        icon_name = entity_config.get('icon', 'plus')
        icon_html = get_entity_icon_html(icon_name, 'button')
        
        # Generate entity buttons with proper HTMX attributes and rendered icons
        entity_buttons = [
            {
                'label': f'New {entity_config.get("display_name_singular", "Item")}',
                'hx_get': f'{entity_config.get("modal_path", "/modals/Item")}/create',
                'hx_target': 'body',
                'hx_swap': 'beforeend', 
                'icon': icon_html,
                'classes': f'btn-new-{entity_name}'
            }
        ]
        
        # Generate entity metadata
        entity_info = {
            'entity_name': entity_config.get('display_name', 'Items'),
            'entity_name_singular': entity_config.get('display_name_singular', 'Item'),
            'entity_description': entity_config.get('description', f'Manage your {entity_name}'),
            'entity_type': entity_name.rstrip('s'),  # Remove trailing 's' for singular
            'entity_endpoint': entity_config.get('endpoint_name', entity_name),
            'entity_buttons': entity_buttons
        }
        
        return entity_info
    
    @staticmethod
    def generate_entity_stats(entity_name: str, entities: List, model_class=None) -> Dict[str, Any]:
        """Generate entity stats based on model metadata and data"""
        
        if not model_class:
            model_class = DropdownConfigGenerator.get_model_by_entity_name(entity_name)
            if not model_class:
                return {}
        
        entity_config = getattr(model_class, '__entity_config__', {})
        display_name = entity_config.get('display_name', 'Items')
        
        # Base stats that work for all entities
        base_stats = [
            {
                'value': len(entities),
                'label': f'Total {display_name}',
                'color_class': 'text-blue-600'
            }
        ]
        
        # Entity-specific stat generators based on entity type
        if entity_name == 'opportunities':
            total_value = sum(getattr(e, 'value', 0) or 0 for e in entities)
            base_stats.extend([
                {
                    'value': f"${total_value:,}",
                    'label': 'Total Pipeline Value',
                    'color_class': 'text-green-600'
                },
                {
                    'value': len([e for e in entities if getattr(e, 'stage', None) == 'closed-won']),
                    'label': 'Closed Won',
                    'color_class': 'text-emerald-600'
                },
                {
                    'value': len(set(getattr(e, 'company_id', None) for e in entities if getattr(e, 'company_id', None))),
                    'label': 'Companies in Pipeline',
                    'color_class': 'text-purple-600'
                }
            ])
        elif entity_name == 'companies':
            base_stats.extend([
                {
                    'value': len([c for c in entities if getattr(c, 'industry', None)]),
                    'label': 'With Industry',
                    'color_class': 'text-green-600'
                },
                {
                    'value': sum(len(getattr(c, 'stakeholders', []) or []) for c in entities),
                    'label': 'Total Stakeholders',
                    'color_class': 'text-purple-600'
                },
                {
                    'value': sum(len(getattr(c, 'opportunities', []) or []) for c in entities),
                    'label': 'Total Opportunities',
                    'color_class': 'text-yellow-600'
                }
            ])
        elif entity_name == 'stakeholders':
            base_stats.extend([
                {
                    'value': len([s for s in entities if getattr(s, 'phone', None)]),
                    'label': 'With Phone',
                    'color_class': 'text-green-600'
                },
                {
                    'value': len([s for s in entities if getattr(s, 'email', None)]),
                    'label': 'With Email',
                    'color_class': 'text-purple-600'
                },
                {
                    'value': len(set([getattr(s, 'company_id', None) for s in entities if getattr(s, 'company_id', None)])),
                    'label': 'Companies Represented',
                    'color_class': 'text-yellow-600'
                }
            ])
        elif entity_name == 'tasks':
            from datetime import datetime
            completed_tasks = len([t for t in entities if getattr(t, 'status', None) == 'completed'])
            overdue_tasks = len([t for t in entities if getattr(t, 'status', None) != 'completed' and hasattr(t, 'due_date') and getattr(t, 'due_date', None) and getattr(t, 'due_date') < datetime.now().date()])
            base_stats.extend([
                {
                    'value': completed_tasks,
                    'label': 'Completed',
                    'color_class': 'text-green-600'
                },
                {
                    'value': len(entities) - completed_tasks,
                    'label': 'Active',
                    'color_class': 'text-blue-600'
                },
                {
                    'value': overdue_tasks,
                    'label': 'Overdue',
                    'color_class': 'text-red-600'
                }
            ])
        
        return {
            'title': f'{display_name} Overview',
            'stats': base_stats
        }
