"""
Model Introspection System for Self-Describing Models

This module provides utilities to extract configuration from SQLAlchemy model
column metadata, enabling models to be the single source of truth for all
UI behavior, choices, CSS classes, grouping, and sorting.
"""

from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime
from sqlalchemy import Column
from flask import current_app


class ModelIntrospector:
    """
    Universal model introspection system that extracts configuration
    from SQLAlchemy column.info metadata.
    """
    
    @staticmethod
    def get_field_choices(model_class, field_name: str) -> List[Tuple[str, str]]:
        """
        Get form choices for a field from column metadata.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field
            
        Returns:
            List of (value, label) tuples for form choices
        """
        column = getattr(model_class, field_name, None)
        if not column or not hasattr(column.property, 'columns'):
            return []
            
        info = column.property.columns[0].info
        choices_config = info.get('choices', {})
        
        if isinstance(choices_config, dict):
            # New format: {'value': {'label': 'Label', ...}}
            return [
                (value, config['label']) 
                for value, config in choices_config.items()
            ]
        elif isinstance(choices_config, list):
            # Legacy format: [('value', 'label'), ...]
            return choices_config
        
        return []
    
    @staticmethod
    def get_field_choices_with_metadata(model_class, field_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Get complete choice configuration including CSS classes, icons, etc.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field
            
        Returns:
            Dict of {value: {label, css_class, icon, ...}} 
        """
        column = getattr(model_class, field_name, None)
        if not column or not hasattr(column.property, 'columns'):
            return {}
            
        info = column.property.columns[0].info
        choices_config = info.get('choices', {})
        
        if isinstance(choices_config, dict):
            return choices_config
        
        return {}
    
    @staticmethod
    def get_field_css_class(model_class, field_name: str, value: str) -> str:
        """
        Get CSS class for a specific field value.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field
            value: Field value
            
        Returns:
            CSS class name or empty string if not found
        """
        choices = ModelIntrospector.get_field_choices_with_metadata(model_class, field_name)
        choice_config = choices.get(value, {})
        return choice_config.get('css_class', '')
    
    @staticmethod
    def get_field_icon(model_class, field_name: str, value: str) -> str:
        """
        Get icon for a specific field value.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field  
            value: Field value
            
        Returns:
            Icon name or empty string if not found
        """
        choices = ModelIntrospector.get_field_choices_with_metadata(model_class, field_name)
        choice_config = choices.get(value, {})
        return choice_config.get('icon', '')
    
    @staticmethod
    def get_groupable_fields(model_class) -> List[Tuple[str, str]]:
        """
        Get all fields that can be grouped by.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            List of (field_name, display_label) tuples
        """
        groupable_fields = []
        
        for attr_name in dir(model_class):
            # Skip private/system attributes
            if attr_name.startswith('_') or attr_name in ['metadata', 'registry', 'query', 'query_class']:
                continue
                
            try:
                attr = getattr(model_class, attr_name)
                if hasattr(attr, 'property') and hasattr(attr.property, 'columns') and len(attr.property.columns) > 0:
                    column = attr.property.columns[0]
                    info = column.info
                    
                    # Check if field has groupable choices
                    if 'choices' in info:
                        choices_config = info['choices']
                        if isinstance(choices_config, dict) and choices_config:
                            has_groupable = any(
                                config.get('groupable', False) 
                                for config in choices_config.values()
                            )
                            if has_groupable:
                                label = info.get('display_label', attr_name.replace('_', ' ').title())
                                groupable_fields.append((attr_name, label))
                    
                    # Check if field is explicitly marked as groupable
                    if info.get('groupable', False):
                        label = info.get('display_label', attr_name.replace('_', ' ').title())
                        groupable_fields.append((attr_name, label))
            except (AttributeError, TypeError):
                continue
        
        return sorted(groupable_fields, key=lambda x: x[1])
    
    @staticmethod
    def get_sortable_fields(model_class) -> List[Tuple[str, str]]:
        """
        Get all fields that can be sorted by.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            List of (field_name, display_label) tuples
        """
        sortable_fields = []
        
        for attr_name in dir(model_class):
            # Skip private/system attributes
            if attr_name.startswith('_') or attr_name in ['metadata', 'registry', 'query', 'query_class']:
                continue
                
            try:
                attr = getattr(model_class, attr_name)
                if hasattr(attr, 'property') and hasattr(attr.property, 'columns') and len(attr.property.columns) > 0:
                    column = attr.property.columns[0]
                    info = column.info
                    
                    # Check if field has sortable choices
                    if 'choices' in info:
                        choices_config = info['choices']
                        if isinstance(choices_config, dict) and choices_config:
                            has_sortable = any(
                                config.get('sortable', True)  # Default to sortable
                                for config in choices_config.values()
                            )
                            if has_sortable:
                                label = info.get('display_label', attr_name.replace('_', ' ').title())
                                sortable_fields.append((attr_name, label))
                    
                    # Check if field is explicitly marked as sortable (default True)
                    if info.get('sortable', True):
                        label = info.get('display_label', attr_name.replace('_', ' ').title())
                        sortable_fields.append((attr_name, label))
            except (AttributeError, TypeError):
                continue
        
        return sorted(sortable_fields, key=lambda x: x[1])
    
    @staticmethod
    def get_ordered_choices(model_class, field_name: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get choices ordered by their 'order' property.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field
            
        Returns:
            List of (value, config_dict) tuples ordered by 'order' property
        """
        choices = ModelIntrospector.get_field_choices_with_metadata(model_class, field_name)
        
        ordered_choices = sorted(
            choices.items(),
            key=lambda x: x[1].get('order', 999)  # Put items without order at end
        )
        
        return ordered_choices
    
    @staticmethod
    def get_model_config(model_class) -> Dict[str, Any]:
        """
        Get complete configuration for a model.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            Complete model configuration dictionary
        """
        config = {
            'model_name': model_class.__name__,
            'table_name': model_class.__tablename__,
            'fields': {},
            'groupable_fields': ModelIntrospector.get_groupable_fields(model_class),
            'sortable_fields': ModelIntrospector.get_sortable_fields(model_class)
        }
        
        # Add field-specific configuration
        for attr_name in dir(model_class):
            # Skip private/system attributes
            if attr_name.startswith('_') or attr_name in ['metadata', 'registry', 'query', 'query_class']:
                continue
                
            try:
                attr = getattr(model_class, attr_name)
                # Check if it's a SQLAlchemy column
                if hasattr(attr, 'property') and hasattr(attr.property, 'columns') and len(attr.property.columns) > 0:
                    column = attr.property.columns[0]
                    info = column.info
                    
                    if info:  # Only include fields with metadata
                        config['fields'][attr_name] = {
                            'choices': ModelIntrospector.get_field_choices_with_metadata(model_class, attr_name),
                            'form_choices': ModelIntrospector.get_field_choices(model_class, attr_name),
                            'display_label': info.get('display_label', attr_name.replace('_', ' ').title()),
                            'groupable': info.get('groupable', False),
                            'sortable': info.get('sortable', True)
                        }
            except (AttributeError, TypeError):
                # Skip attributes that can't be introspected
                continue
        
        return config
    
    @staticmethod
    def get_field_default_value(model_class, field_name: str) -> Any:
        """
        Get the default value for a field.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Name of the field
            
        Returns:
            Default value or None
        """
        column = getattr(model_class, field_name, None)
        if not column or not hasattr(column.property, 'columns'):
            return None
            
        db_column = column.property.columns[0]
        if db_column.default:
            if hasattr(db_column.default, 'arg'):
                return db_column.default.arg
            return db_column.default
        
        return None
    
    @staticmethod
    def get_form_fields(model_class) -> List[Dict[str, Any]]:
        """
        Get form field definitions for all model fields suitable for forms.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            List of form field definitions with name, type, label, choices, etc.
        """
        fields = []
        
        for attr_name in dir(model_class):
            # Skip private/system attributes and relationships
            if attr_name.startswith('_') or attr_name in ['metadata', 'registry', 'query', 'query_class', 'id']:
                continue
                
            try:
                attr = getattr(model_class, attr_name)
                # Check if it's a SQLAlchemy column (not relationship)
                if hasattr(attr, 'property') and hasattr(attr.property, 'columns') and len(attr.property.columns) > 0:
                    column = attr.property.columns[0]
                    info = column.info
                    
                    # Skip auto-generated fields typically not in forms
                    if attr_name in ['created_at', 'completed_at', 'updated_at']:
                        continue
                    
                    # Determine field type based on SQLAlchemy column type
                    field_type = 'text'  # default
                    if hasattr(column.type, 'python_type'):
                        python_type = column.type.python_type
                        if python_type == int:
                            field_type = 'number'
                        elif python_type == bool:
                            field_type = 'checkbox'
                        elif python_type == datetime:
                            field_type = 'datetime-local'
                        elif hasattr(column.type, 'name'):
                            if column.type.name.upper() == 'DATE':
                                field_type = 'date'
                            elif column.type.name.upper() == 'TEXT':
                                field_type = 'textarea'
                    
                    # Check if field has choices - use select instead
                    choices = ModelIntrospector.get_field_choices(model_class, attr_name)
                    if choices:
                        field_type = 'select'
                    
                    # Build field definition
                    field_def = {
                        'name': attr_name,
                        'type': field_type,
                        'label': info.get('display_label', attr_name.replace('_', ' ').title()),
                        'required': not column.nullable and not column.default,
                        'default': ModelIntrospector.get_field_default_value(model_class, attr_name),
                        'choices': choices,
                        'description': info.get('description', ''),
                        'placeholder': info.get('placeholder', ''),
                    }
                    
                    # Add field-specific attributes
                    if field_type == 'textarea':
                        field_def['rows'] = info.get('rows', 3)
                    elif field_type == 'number':
                        field_def['min'] = info.get('min')
                        field_def['max'] = info.get('max')
                        field_def['step'] = info.get('step')
                    
                    fields.append(field_def)
                    
            except (AttributeError, TypeError):
                # Skip attributes that can't be introspected
                continue
        
        # Sort fields by a logical form order
        form_order = {
            'description': 1, 'name': 1, 'title': 1,
            'due_date': 2, 'start_date': 2, 'end_date': 2,
            'priority': 3, 'status': 3, 'stage': 3,
            'type': 4, 'category': 4,
            'value': 5, 'amount': 5, 'price': 5,
            'notes': 10, 'comments': 10
        }
        
        def get_sort_key(field):
            return form_order.get(field['name'], 6)
        
        return sorted(fields, key=get_sort_key)
    
    @staticmethod
    def get_card_config(model_class) -> Dict[str, Any]:
        """
        Extract card rendering configuration from model metadata.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            Card configuration dictionary for template rendering
        """
        config = {
            'title_field': 'name',  # Standard across all models
            'badge_field': None,
            'value_field': None, 
            'secondary_fields': [],
            'metadata_fields': []
        }
        
        # Find primary status/stage field for badge
        badge_candidates = ['stage', 'status', 'priority', 'job_title', 'industry']
        for field_name in badge_candidates:
            if hasattr(model_class, field_name):
                column = getattr(model_class, field_name)
                if hasattr(column.property, 'columns') and len(column.property.columns) > 0:
                    info = column.property.columns[0].info
                    choices = info.get('choices', {})
                    if choices:  # Field has choices, good for badge
                        config['badge_field'] = field_name
                        break
        
        # Find value field (for deals, amounts, etc.)
        value_candidates = ['value', 'amount', 'price', 'salary']
        for field_name in value_candidates:
            if hasattr(model_class, field_name):
                config['value_field'] = field_name
                break
        
        # Find relationship fields for secondary info
        relationship_fields = []
        for attr_name in dir(model_class):
            if attr_name.startswith('_'):
                continue
            try:
                attr = getattr(model_class, attr_name)
                # Check for relationships
                if hasattr(attr, 'property') and hasattr(attr.property, 'mapper'):
                    # This is a relationship - add common sub-fields
                    relationship_fields.extend([
                        {'field': f'{attr_name}.name', 'type': 'text'},
                        {'field': f'{attr_name}.email', 'type': 'email'}
                    ])
                    break  # Limit to first relationship to avoid clutter
            except (AttributeError, TypeError):
                continue
        
        config['secondary_fields'] = relationship_fields[:2]  # Max 2 secondary fields
        
        # Find date fields for metadata
        date_fields = []
        date_candidates = ['created_at', 'due_date', 'expected_close_date', 'start_date', 'end_date', 'completed_at']
        for field_name in date_candidates:
            if hasattr(model_class, field_name):
                date_fields.append({
                    'field': field_name, 
                    'type': 'date', 
                    'format': '%m/%d/%y'
                })
                if len(date_fields) >= 2:  # Max 2 date fields
                    break
        
        config['metadata_fields'] = date_fields
        
        return config
    
    @staticmethod
    def extract_field_value(entity, field_path: str):
        """
        Extract a field value from an entity using dot notation.
        
        Args:
            entity: Model instance
            field_path: Field path like 'name' or 'company.name'
            
        Returns:
            Field value or None if not found
        """
        try:
            # Split field path and traverse
            parts = field_path.split('.')
            value = entity
            
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return None
            
            return value
        except (AttributeError, TypeError):
            return None
    
    @staticmethod
    def format_field_value(value, field_type: str, format_string: str = None) -> str:
        """
        Format a field value based on its type.
        
        Args:
            value: Raw field value
            field_type: Type hint ('date', 'currency', 'text', etc.)
            format_string: Optional format string
            
        Returns:
            Formatted string value
        """
        if value is None:
            return ""
        
        try:
            if field_type == 'date' and hasattr(value, 'strftime'):
                format_str = format_string or '%m/%d/%y'
                return value.strftime(format_str)
            elif field_type == 'currency' and isinstance(value, (int, float)):
                return f"${value:,.0f}"
            elif field_type == 'email' and value:
                return f"<a href='mailto:{value}' class='text-blue-600 hover:text-blue-800'>{value}</a>"
            else:
                return str(value)
        except (AttributeError, ValueError, TypeError):
            return str(value) if value else ""


def get_model_by_name(model_name: str):
    """
    Get a model class by its name.
    
    Args:
        model_name: String name of the model (e.g., 'Opportunity', 'Task')
        
    Returns:
        Model class or None if not found
    """
    from app.models import Company, Stakeholder, Opportunity, Task, User
    
    model_map = {
        'company': Company,
        'stakeholder': Stakeholder,
        'contact': Stakeholder,  # Legacy support
        'opportunity': Opportunity,
        'task': Task,
        'User': User,
        'user': User,
        'TeamMember': User,  # Alias for teams
        'team_member': User,
    }
    
    return model_map.get(model_name.lower())


def get_all_model_configs() -> Dict[str, Dict[str, Any]]:
    """
    Get configuration for all models.
    
    Returns:
        Dict mapping model names to their configurations
    """
    from app.models import Company, Stakeholder, Opportunity, Task
    
    models = [Company, Stakeholder, Opportunity, Task]
    configs = {}
    
    for model in models:
        configs[model.__name__] = ModelIntrospector.get_model_config(model)
    
    return configs