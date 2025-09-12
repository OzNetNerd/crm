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
            # Already in full format
            choice_info = {
                'groupable': groupable,
                'sortable': sortable,
                **choice_data
            }
        else:
            # Simple string - create full format
            choice_info = {
                'label': choice_data,
                'css_class': f'choice-{key}',
                'groupable': groupable,
                'sortable': sortable,
                'description': choice_data,
                'icon': 'circle',
                'order': len(info['choices']) + 1
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


def create_text_field_info(display_label, sortable=True, required=False, **kwargs):
    """Factory function to create standardized text field metadata"""
    info = {
        'display_label': display_label,
        'sortable': sortable
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
        'css_class': 'priority-urgent',
        'description': 'Urgent priority',
        'icon': 'exclamation',
        'order': 1
    },
    'medium': {
        'label': 'Medium',
        'css_class': 'priority-normal',
        'description': 'Normal priority',
        'icon': 'minus',
        'order': 2
    },
    'low': {
        'label': 'Low',
        'css_class': 'priority-low',
        'description': 'Low priority',
        'icon': 'arrow-down',
        'order': 3
    }
}

STATUS_CHOICES = {
    'todo': {
        'label': 'To Do',
        'css_class': 'status-todo',
        'description': 'Not started',
        'icon': 'circle',
        'order': 1
    },
    'in-progress': {
        'label': 'In Progress',
        'css_class': 'status-progress',
        'description': 'Currently working on',
        'icon': 'clock',
        'order': 2
    },
    'complete': {
        'label': 'Complete',
        'css_class': 'status-complete',
        'description': 'Finished',
        'icon': 'check-circle',
        'order': 3
    }
}

NEXT_STEP_TYPE_CHOICES = {
    'call': {
        'label': 'Call',
        'css_class': 'step-call',
        'description': 'Phone call',
        'icon': 'phone',
        'order': 1
    },
    'email': {
        'label': 'Email',
        'css_class': 'step-email',
        'description': 'Send email',
        'icon': 'mail',
        'order': 2
    },
    'meeting': {
        'label': 'Meeting',
        'css_class': 'step-meeting',
        'description': 'In-person or video meeting',
        'icon': 'users',
        'order': 3
    },
    'demo': {
        'label': 'Demo',
        'css_class': 'step-demo',
        'description': 'Product demonstration',
        'icon': 'presentation-chart-line',
        'order': 4
    }
}

TASK_TYPE_CHOICES = {
    'single': {
        'label': 'Single Task',
        'css_class': 'type-single',
        'description': 'Standalone task',
        'icon': 'document',
        'order': 1
    },
    'parent': {
        'label': 'Parent Task',
        'css_class': 'type-parent',
        'description': 'Task with subtasks',
        'icon': 'folder',
        'order': 2
    },
    'child': {
        'label': 'Child Task',
        'css_class': 'type-child',
        'description': 'Subtask of parent',
        'icon': 'document-duplicate',
        'order': 3
    }
}

DEPENDENCY_TYPE_CHOICES = {
    'parallel': {
        'label': 'Parallel',
        'css_class': 'dep-parallel',
        'description': 'Can run simultaneously',
        'icon': 'arrows-right-left',
        'order': 1
    },
    'sequential': {
        'label': 'Sequential',
        'css_class': 'dep-sequential',
        'description': 'Must complete in order',
        'icon': 'arrow-right',
        'order': 2
    }
}

DUE_DATE_GROUPINGS = {
    'overdue': {'label': 'Overdue', 'css_class': 'date-overdue'},
    'today': {'label': 'Due Today', 'css_class': 'date-today'},
    'this_week': {'label': 'This Week', 'css_class': 'date-soon'},
    'later': {'label': 'Later', 'css_class': 'date-future'},
    'no_date': {'label': 'No Due Date', 'css_class': 'date-missing'}
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