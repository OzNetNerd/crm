"""
Model Introspection System for Self-Describing Models

This module provides utilities to extract configuration from SQLAlchemy model
column metadata, enabling models to be the single source of truth for all
UI behavior, choices, CSS classes, grouping, and sorting.
"""

from typing import Dict, List, Tuple, Any, Optional, Union
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
            attr = getattr(model_class, attr_name)
            if hasattr(attr.property, 'columns'):
                column = attr.property.columns[0]
                info = column.info
                
                # Check if field has groupable choices
                choices_config = info.get('choices', {})
                if isinstance(choices_config, dict):
                    has_groupable = any(
                        config.get('groupable', False) 
                        for config in choices_config.values()
                    )
                    if has_groupable:
                        label = info.get('display_label', attr_name.replace('_', ' ').title())
                        groupable_fields.append((attr_name, label))
                
                # Check if field is explicitly marked as groupable
                elif info.get('groupable', False):
                    label = info.get('display_label', attr_name.replace('_', ' ').title())
                    groupable_fields.append((attr_name, label))
        
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
            attr = getattr(model_class, attr_name)
            if hasattr(attr.property, 'columns'):
                column = attr.property.columns[0]
                info = column.info
                
                # Check if field has sortable choices
                choices_config = info.get('choices', {})
                if isinstance(choices_config, dict):
                    has_sortable = any(
                        config.get('sortable', True)  # Default to sortable
                        for config in choices_config.values()
                    )
                    if has_sortable:
                        label = info.get('display_label', attr_name.replace('_', ' ').title())
                        sortable_fields.append((attr_name, label))
                
                # Check if field is explicitly marked as sortable (default True)
                elif info.get('sortable', True):
                    label = info.get('display_label', attr_name.replace('_', ' ').title())
                    sortable_fields.append((attr_name, label))
        
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
            attr = getattr(model_class, attr_name)
            if hasattr(attr.property, 'columns'):
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


def get_model_by_name(model_name: str):
    """
    Get a model class by its name.
    
    Args:
        model_name: String name of the model (e.g., 'Opportunity', 'Task')
        
    Returns:
        Model class or None if not found
    """
    from app.models import Company, Stakeholder, Opportunity, Task
    
    model_map = {
        'Company': Company,
        'company': Company,
        'Stakeholder': Stakeholder,
        'stakeholder': Stakeholder,
        'Contact': Stakeholder,  # Legacy support
        'contact': Stakeholder,
        'Opportunity': Opportunity,
        'opportunity': Opportunity,
        'Task': Task,
        'task': Task,
    }
    
    return model_map.get(model_name)


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