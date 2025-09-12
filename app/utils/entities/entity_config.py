"""
Entity Configuration Generator

Auto-generates API entity configurations from model metadata,
eliminating manual field lists and using model introspection instead.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
from sqlalchemy import inspect


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
        from app.utils.core.base_handlers import GenericAPIHandler
        from app.utils.core.model_introspection import ModelIntrospector
        
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

    @staticmethod
    def generate_entity_page_config(entity_name: str, model_class=None) -> Dict[str, Any]:
        """Generate complete entity page configuration from model metadata"""
        from app.utils.forms.form_builder import DropdownConfigGenerator
        
        # Get model class if not provided
        if not model_class:
            model_class = DropdownConfigGenerator.get_model_by_entity_name(entity_name)
            if not model_class:
                raise ValueError(f"Unknown entity: {entity_name}")
        
        # Get entity config from model
        entity_config = getattr(model_class, '__entity_config__', {})
        
        # Use centralized entity icon system
        from app.utils.entities.entity_icons import get_entity_icon_html
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
        from app.utils.forms.form_builder import DropdownConfigGenerator
        
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
                'color_class': 'text-color-default'
            }
        ]
        
        # Entity-specific stat generators based on entity type
        if entity_name == 'opportunities':
            total_value = sum(getattr(e, 'value', 0) or 0 for e in entities)
            base_stats.extend([
                {
                    'value': f"${total_value:,}",
                    'label': 'Total Pipeline Value',
                    'color_class': 'text-color-company'
                },
                {
                    'value': len([e for e in entities if getattr(e, 'stage', None) == 'closed-won']),
                    'label': 'Closed Won',
                    'color_class': 'text-emerald-600'
                },
                {
                    'value': len(set(getattr(e, 'company_id', None) for e in entities if getattr(e, 'company_id', None))),
                    'label': 'Companies in Pipeline',
                    'color_class': 'text-color-opportunity'
                }
            ])
        elif entity_name == 'companies':
            base_stats.extend([
                {
                    'value': len([c for c in entities if getattr(c, 'industry', None)]),
                    'label': 'With Industry',
                    'color_class': 'text-color-company'
                },
                {
                    'value': sum(len(getattr(c, 'stakeholders', []) or []) for c in entities),
                    'label': 'Total Stakeholders',
                    'color_class': 'text-color-opportunity'
                },
                {
                    'value': sum(len(getattr(c, 'opportunities', []) or []) for c in entities),
                    'label': 'Total Opportunities',
                    'color_class': 'text-color-stakeholder'
                }
            ])
        elif entity_name == 'stakeholders':
            base_stats.extend([
                {
                    'value': len([s for s in entities if getattr(s, 'phone', None)]),
                    'label': 'With Phone',
                    'color_class': 'text-color-company'
                },
                {
                    'value': len([s for s in entities if getattr(s, 'email', None)]),
                    'label': 'With Email',
                    'color_class': 'text-color-opportunity'
                },
                {
                    'value': len(set([getattr(s, 'company_id', None) for s in entities if getattr(s, 'company_id', None)])),
                    'label': 'Companies Represented',
                    'color_class': 'text-color-stakeholder'
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
                    'color_class': 'text-color-company'
                },
                {
                    'value': len(entities) - completed_tasks,
                    'label': 'Active',
                    'color_class': 'text-color-default'
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