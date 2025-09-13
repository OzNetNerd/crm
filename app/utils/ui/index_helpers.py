"""
Universal Index Helper - DRY consolidation for all entity index routes

Eliminates duplicate parameter parsing, data fetching, and context building
across all entity index functions by providing a single, consistent interface.
"""

from flask import request
# Lazy import to avoid circular dependency
def _get_dropdown_generator():
    from app.forms.base.builders import DropdownConfigGenerator
    return DropdownConfigGenerator


class UniversalIndexHelper:
    """
    Universal helper for standardized entity index routes
    
    Provides consistent parameter parsing, dropdown generation, and context building
    for all entity types, eliminating code duplication across routes.
    """
    
    @classmethod
    def parse_request_parameters(cls):
        """
        Extract and standardize filter parameters from request
        
        Returns:
            dict: Standardized parameters for all entity types
        """
        return {
            'group_by': request.args.get("group_by", ""),
            'sort_by': request.args.get("sort_by", ""),
            'sort_direction': request.args.get("sort_direction", "asc"),
            'show_completed': request.args.get("show_completed", "false").lower() == "true",
            'primary_filter': (
                request.args.get("primary_filter", "").split(",")
                if request.args.get("primary_filter")
                else []
            ),
            'secondary_filter': (
                request.args.get("secondary_filter", "").split(",")
                if request.args.get("secondary_filter")
                else []
            ),
            'entity_filter': (
                request.args.get("entity_filter", "").split(",")
                if request.args.get("entity_filter")
                else []
            )
        }
    
    @classmethod
    def generate_entity_context(cls, entity_name, default_group_by=None, default_sort_by=None):
        """
        Generate complete context for entity index pages using DRY generators
        
        Args:
            entity_name (str): Entity type (e.g., 'companies', 'tasks', 'opportunities')
            default_group_by (str, optional): Default grouping field
            default_sort_by (str, optional): Default sorting field
            
        Returns:
            dict: Complete context for entity index template
        """
        params = cls.parse_request_parameters()
        
        # Apply defaults
        if default_group_by and not params['group_by']:
            params['group_by'] = default_group_by
        if default_sort_by and not params['sort_by']:
            params['sort_by'] = default_sort_by
            
        # Generate dropdown configurations
        dropdown_configs = _get_dropdown_generator().generate_entity_dropdown_configs(
            entity_name=entity_name,
            group_by=params['group_by'],
            sort_by=params['sort_by'],
            sort_direction=params['sort_direction'],
            primary_filter=params['primary_filter']
        )
        
        # Generate entity configuration directly from model
        model_class = _get_dropdown_generator().get_model_by_entity_name(entity_name)
        if not model_class:
            raise ValueError(f"Unknown entity: {entity_name}")
        
        # Use unified button generator for consistency
        from app.utils.ui.button_generator import EntityButtonGenerator
        
        entity_config = {
            'entity_name': model_class.__entity_config__.get('display_name', 'Items'),
            'entity_name_singular': model_class.__entity_config__.get('display_name_singular', 'Item'),
            'entity_description': model_class.__entity_config__.get('description', f'Manage your {entity_name}'),
            'entity_type': entity_name.rstrip('s'),
            'entity_endpoint': model_class.__entity_config__.get('endpoint_name', entity_name),
            'entity_buttons': [EntityButtonGenerator.generate_single_button(entity_name)]
        }
        
        # Add relationship labels for dynamic pluralization
        relationship_labels = cls._build_relationship_labels()
        
        # Combine all context
        context = {
            **entity_config,
            'dropdown_configs': dropdown_configs,
            'request_params': params,
            'relationship_labels': relationship_labels
        }
        
        return context
    
    @classmethod
    def _build_relationship_labels(cls):
        """
        Build relationship labels dynamically from all model configs
        
        Returns:
            Dict mapping relationship names to singular/plural labels
        """
        from app.utils.core.model_introspection import get_all_entity_models
        
        # Get all models with entity configs dynamically
        all_models = get_all_entity_models()
        labels = {}
        
        for model_class in all_models:
            config = model_class.__entity_config__
            endpoint_name = config.get('endpoint_name', model_class.__tablename__)
            
            # Add primary endpoint mapping
            labels[endpoint_name] = {
                'singular': config['display_name_singular'],
                'plural': config['display_name']
            }
            
            # Add common aliases based on model type
            if hasattr(model_class, '__name__'):
                if model_class.__name__ == 'Stakeholder':
                    labels['contacts'] = {
                        'singular': config['display_name_singular'],
                        'plural': config['display_name']
                    }
                elif model_class.__name__ == 'User':
                    labels['team_members'] = {
                        'singular': config['display_name_singular'],
                        'plural': config['display_name']
                    }
        
        return labels
    
    @classmethod
    def get_standardized_index_context(cls, entity_name, default_group_by=None, default_sort_by=None, additional_context=None):
        """
        Get complete standardized context for entity index routes
        
        Args:
            entity_name (str): Entity type
            default_group_by (str, optional): Default grouping
            default_sort_by (str, optional): Default sorting  
            additional_context (dict, optional): Extra context specific to entity
            
        Returns:
            dict: Complete context ready for entity_index.html template
        """
        context = cls.generate_entity_context(entity_name, default_group_by, default_sort_by)
        
        # Merge any additional context
        if additional_context:
            context.update(additional_context)
            
        return context