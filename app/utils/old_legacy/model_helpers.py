"""
Model helper utilities for DRY field definitions and common patterns
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


def create_model_choice_methods(field_names):
    """Class decorator to auto-generate choice and CSS methods for specified fields"""
    def decorator(cls):
        for field_name in field_names:
            # Create get_FIELD_choices method
            def make_choices_method(field):
                @classmethod
                def choices_method(cls):
                    from app.utils.model_introspection import ModelIntrospector
                    return ModelIntrospector.get_field_choices(cls, field)
                return choices_method
            
            choices_method_name = f"get_{field_name}_choices"
            setattr(cls, choices_method_name, make_choices_method(field_name))
            
            # Create get_FIELD_css_class method
            def make_css_method(field):
                @classmethod
                def css_method(cls, field_value):
                    from app.utils.model_introspection import ModelIntrospector
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


def auto_serialize(model_instance, include_properties=None, field_transforms=None, exclude_fields=None):
    """
    Automatically serialize a SQLAlchemy model instance to dictionary.
    
    Args:
        model_instance: The SQLAlchemy model instance to serialize
        include_properties: List of property names to include (computed properties)
        field_transforms: Dict mapping field names to custom transform functions
        exclude_fields: Set of field names to exclude from serialization
    
    Returns:
        Dictionary representation of the model instance
    """
    from sqlalchemy import inspect
    from datetime import datetime, date
    
    if not model_instance:
        return None
        
    result = {}
    inspector = inspect(model_instance.__class__)
    
    # Serialize database columns
    for column in inspector.columns:
        field_name = column.name
        
        # Skip excluded fields
        if exclude_fields and field_name in exclude_fields:
            continue
            
        field_value = getattr(model_instance, field_name, None)
        
        # Handle datetime/date objects
        if isinstance(field_value, (datetime, date)):
            field_value = field_value.isoformat() if field_value else None
        
        # Apply custom transform if specified
        if field_transforms and field_name in field_transforms:
            field_value = field_transforms[field_name](field_value)
            
        result[field_name] = field_value
    
    # Add specified properties
    if include_properties:
        for prop_name in include_properties:
            if hasattr(model_instance, prop_name):
                prop_value = getattr(model_instance, prop_name)
                
                # Apply custom transform if specified
                if field_transforms and prop_name in field_transforms:
                    prop_value = field_transforms[prop_name](prop_value)
                    
                result[prop_name] = prop_value
    
    return result


class EntityConfigGenerator:
    """
    Utility class to auto-generate API entity configurations from model metadata.
    Eliminates manual field lists and uses model introspection instead.
    """
    
    @staticmethod
    def generate_config(model_class, entity_name, overrides=None):
        """
        Generate complete entity configuration from model metadata.
        
        Args:
            model_class: SQLAlchemy model class
            entity_name: Plural entity name (e.g., 'companies', 'tasks')  
            overrides: Dict of configuration overrides
            
        Returns:
            Complete entity configuration dict
        """
        from app.utils.route_helpers import GenericAPIHandler
        from app.utils.model_introspection import ModelIntrospector
        
        overrides = overrides or {}
        
        # Generate base configuration
        config = {
            "model": model_class,
            "handler": GenericAPIHandler(model_class, entity_name[:-1]),  # Remove 's' for singular
            "route_param": f"{entity_name[:-1]}_id",  # Remove 's' and add '_id'
        }
        
        # Auto-generate field lists from model introspection
        form_fields = ModelIntrospector.get_form_fields(model_class)
        
        # Separate create vs update fields based on requirements
        create_fields = []
        update_fields = []
        
        for field in form_fields:
            field_name = field['name']
            # Skip auto-generated fields
            if field_name in ['id', 'created_at', 'updated_at', 'completed_at']:
                continue
                
            # All non-auto fields can be updated
            update_fields.append(field_name)
            
            # Required fields and some optional ones are needed for creation
            if field['required'] or field_name in ['company_id', 'task_type', 'stage', 'priority', 'status']:
                create_fields.append(field_name)
        
        config["create_fields"] = create_fields
        config["update_fields"] = update_fields
        
        # Generate list serializer using to_dict with field filtering
        config["list_serializer"] = EntityConfigGenerator._create_list_serializer(model_class)
        
        # Apply any overrides
        config.update(overrides)
        
        return config
    
    @staticmethod
    def _create_list_serializer(model_class):
        """
        Create a generic list serializer that uses the model's to_dict method
        but filters to essential fields for dropdown/list usage.
        """
        def list_serializer(entity):
            full_dict = entity.to_dict()
            
            # Essential fields for lists/dropdowns
            essential_fields = {
                'id': full_dict.get('id'),
                'name': full_dict.get('name', full_dict.get('description')),  # Fallback to description for tasks
            }
            
            # Add model-specific fields
            model_name = model_class.__name__.lower()
            if model_name == 'stakeholder':
                essential_fields.update({
                    'job_title': full_dict.get('job_title'),
                    'company_name': full_dict.get('company_name'),
                    'meddpicc_roles': full_dict.get('meddpicc_roles'),
                })
            elif model_name == 'company':
                essential_fields.update({
                    'industry': full_dict.get('industry'),
                })
            elif model_name == 'opportunity':
                essential_fields.update({
                    'stage': full_dict.get('stage'),
                    'company_name': full_dict.get('company_name'),
                })
            elif model_name == 'task':
                essential_fields.update({
                    'status': full_dict.get('status'),
                    'priority': full_dict.get('priority'),
                    'due_date': full_dict.get('due_date'),
                })
                
            return essential_fields
            
        return list_serializer
    
    @staticmethod
    def generate_all_configs():
        """
        Generate configurations for all standard entities.
        
        Returns:
            Dict of entity configurations keyed by entity name
        """
        from app.models import Task, Stakeholder, Company, Opportunity
        
        configs = {}
        
        # Define entities with their models and any special overrides
        entities = [
            ("tasks", Task, {
                "has_custom_create": True,  # Tasks have complex creation logic
            }),
            ("stakeholders", Stakeholder, {}),
            ("companies", Company, {}), 
            ("opportunities", Opportunity, {}),
        ]
        
        for entity_name, model_class, overrides in entities:
            configs[entity_name] = EntityConfigGenerator.generate_config(
                model_class, entity_name, overrides
            )
            
        return configs