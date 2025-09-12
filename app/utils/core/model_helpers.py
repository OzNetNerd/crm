"""
Model helper utilities for field definitions and common patterns.
Extracted from legacy files and cleaned up.
"""
from functools import wraps


def create_choice_field_info(display_label, choices, groupable=True, sortable=True, **kwargs):
    """Factory function to create standardized choice field metadata"""
    info = {
        'display_label': display_label,
        'groupable': groupable,
        'sortable': sortable,
        'choices': {}
    }
    
    # Add any additional metadata
    info.update(kwargs)
    
    # Process choices dictionary - normalize format
    for key, choice_data in choices.items():
        if isinstance(choice_data, dict):
            # Already in full format - only keep essential fields
            choice_info = {
                'label': choice_data.get('label', key),
                'description': choice_data.get('description', choice_data.get('label', key))
            }
        else:
            # Simple string - create minimal format
            choice_info = {
                'label': choice_data,
                'description': choice_data
            }
        
        info['choices'][key] = choice_info
    
    return info


def create_date_field_info(display_label, groupable=True, sortable=True, date_groupings=None, **kwargs):
    """Factory function to create standardized date field metadata"""
    info = {
        'display_label': display_label,
        'groupable': groupable,
        'sortable': sortable
    }
    
    # Add any additional metadata
    info.update(kwargs)
    
    # Add default date groupings if provided
    if date_groupings:
        info['date_groupings'] = date_groupings
    
    return info


def create_text_field_info(display_label, sortable=True, groupable=True, required=False, **kwargs):
    """Factory function to create standardized text field metadata"""
    info = {
        'display_label': display_label,
        'sortable': sortable,
        'groupable': groupable
    }
    
    if required:
        info['required'] = True
    
    # Add any additional metadata
    info.update(kwargs)
    
    return info


def create_model_choice_methods(field_names):
    """Class decorator to auto-generate choice and CSS methods for specified fields"""
    def decorator(cls):
        for field_name in field_names:
            # Create get_FIELD_choices method
            def make_choices_method(field):
                @classmethod
                def choices_method(cls):
                    from app.utils.core.model_introspection import ModelIntrospector
                    return ModelIntrospector.get_field_choices(cls, field)
                return choices_method
            
            choices_method_name = f"get_{field_name}_choices"
            setattr(cls, choices_method_name, make_choices_method(field_name))
            
            # Create get_FIELD_css_class method
            def make_css_method(field):
                @classmethod
                def css_method(cls, field_value):
                    from app.utils.core.model_introspection import ModelIntrospector
                    return ModelIntrospector.get_field_css_class(cls, field, field_value)
                return css_method
            
            css_method_name = f"get_{field_name}_css_class"
            setattr(cls, css_method_name, make_css_method(field_name))
        
        return cls
    return decorator


# Predefined choice configurations for common field types
PRIORITY_CHOICES = {
    'high': {
        'label': 'High',
        'description': 'Urgent priority'
    },
    'medium': {
        'label': 'Medium',
        'description': 'Normal priority'
    },
    'low': {
        'label': 'Low',
        'description': 'Low priority'
    }
}

STATUS_CHOICES = {
    'todo': {
        'label': 'To Do',
        'description': 'Not started'
    },
    'in-progress': {
        'label': 'In Progress',
        'description': 'Currently working on'
    },
    'complete': {
        'label': 'Complete',
        'description': 'Finished'
    }
}

NEXT_STEP_TYPE_CHOICES = {
    'call': {
        'label': 'Call',
        'description': 'Phone call'
    },
    'email': {
        'label': 'Email',
        'description': 'Send email'
    },
    'meeting': {
        'label': 'Meeting',
        'description': 'In-person or video meeting'
    },
    'demo': {
        'label': 'Demo',
        'description': 'Product demonstration'
    }
}

TASK_TYPE_CHOICES = {
    'single': {
        'label': 'Single Task',
        'description': 'Standalone task'
    },
    'parent': {
        'label': 'Parent Task',
        'description': 'Task with subtasks'
    },
    'child': {
        'label': 'Child Task',
        'description': 'Subtask of parent'
    }
}

DEPENDENCY_TYPE_CHOICES = {
    'parallel': {
        'label': 'Parallel',
        'description': 'Can run simultaneously'
    },
    'sequential': {
        'label': 'Sequential',
        'description': 'Must complete in order'
    }
}

DUE_DATE_GROUPINGS = {
    'overdue': 'Overdue',
    'today': 'Due Today',
    'this_week': 'This Week',
    'later': 'Later',
    'no_date': 'No Due Date'
}


def create_simple_entity_property(entity_type, property_source, property_name, fallback_value=None):
    """
    Create a simple property that searches linked entities for a specific value
    
    Args:
        entity_type: The type of entity to search for (e.g. 'opportunity', 'company')
        property_source: Where to get the property from ('entity' or 'name' or dict key)
        property_name: The property name to retrieve
        fallback_value: Value to return if not found
    """
    def property_getter(self):
        for entity in self.linked_entities:
            if entity["type"] == entity_type:
                if property_source == "entity" and entity.get("entity"):
                    return getattr(entity["entity"], property_name, fallback_value)
                elif property_source == "name":
                    return entity.get("name", fallback_value)
                elif property_source in entity:
                    return entity[property_source]
        return fallback_value
    
    return property_getter


def auto_serialize(model_instance, include_properties=None, field_transforms=None):
    """
    Auto-serialize a model instance to a dictionary.
    
    Args:
        model_instance: SQLAlchemy model instance
        include_properties: List of property names to include
        field_transforms: Dict of field_name -> transform_function
        
    Returns:
        Dictionary representation of the model
    """
    from datetime import datetime, date
    
    result = {}
    field_transforms = field_transforms or {}
    include_properties = include_properties or []
    
    # Get model columns
    if hasattr(model_instance, '__table__'):
        for column in model_instance.__table__.columns:
            field_name = column.name
            value = getattr(model_instance, field_name, None)
            
            # Apply field transforms if available
            if field_name in field_transforms:
                result[field_name] = field_transforms[field_name](value)
            else:
                # Standard serialization
                if isinstance(value, (datetime, date)):
                    result[field_name] = value.isoformat() if value else None
                else:
                    result[field_name] = value
    
    # Include additional properties
    for prop_name in include_properties:
        if hasattr(model_instance, prop_name):
            prop_value = getattr(model_instance, prop_name)
            result[prop_name] = prop_value
            
    return result