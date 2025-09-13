"""
Universal Context Builders - ADR-017 Implementation

Configuration object classes and universal context builder that replaces
ad-hoc dictionary building with typed, extensible configuration objects.
"""

from typing import Dict, List, Any, Optional
from flask import request
from .model_registry import ModelRegistry


class UniversalContextBuilder:
    """
    Universal context builder using configuration objects - ADR-017
    
    Replaces UniversalIndexHelper with metadata-driven approach that follows
    configuration object patterns and DRY principles from ADR-008.
    """
    
    @staticmethod
    def build_entity_index_context(entity_name: str, 
                                 entities_data: List[Dict] = None,
                                 default_group_by: str = None,
                                 default_sort_by: str = None,
                                 **kwargs) -> Dict[str, Any]:
        """
        Build standardized context for entity index pages - ADR-017
        
        Returns configuration objects for complex data,
        individual variables for simple data
        
        Args:
            entity_name: Entity type (e.g., 'companies', 'tasks')
            entities_data: List of entity data dictionaries
            default_group_by: Default grouping field
            default_sort_by: Default sorting field
            **kwargs: Additional configuration options
            
        Returns:
            Dict with configuration objects and simple variables
        """
        entities_data = entities_data or []
        
        # Parse request parameters (simple data - use individual variables)
        request_params = UniversalContextBuilder._parse_request_params()
        
        # Apply defaults
        if default_group_by and not request_params['group_by']:
            request_params['group_by'] = default_group_by
        if default_sort_by and not request_params['sort_by']:
            request_params['sort_by'] = default_sort_by
        
        # Build entity configuration from metadata
        entity_config = UniversalContextBuilder._build_entity_config(entity_name)
        
        # Build UI configuration
        ui_config = UniversalContextBuilder._build_ui_config(entity_name, request_params, **kwargs)
        
        # Build dropdown configurations  
        dropdown_configs = UniversalContextBuilder._build_dropdown_configs(
            entity_name, request_params
        )
        
        # Build relationship labels
        relationship_labels = UniversalContextBuilder._build_relationship_labels()
        
        return {
            # Simplified direct dictionary building - no need for dataclass overhead
            'entity_config': entity_config,
            'ui_config': ui_config,
            'dropdown_configs': dropdown_configs,

            # Individual entity variables for template compatibility
            'entity_name': entity_config['entity_name'],
            'entity_name_singular': entity_config['entity_name_singular'],
            'entity_description': entity_config['entity_description'],
            'entity_type': entity_config['entity_type'],
            'entity_endpoint': entity_config['entity_endpoint'],
            'entity_buttons': entity_config['entity_buttons'],

            # Individual variables for simple, stable data
            'current_page': request.args.get('page', 1, type=int),
            'total_items': len(entities_data),
            'has_items': len(entities_data) > 0,
            
            # Request parameters as simple variables
            'group_by': request_params['group_by'],
            'sort_by': request_params['sort_by'],
            'sort_direction': request_params['sort_direction'],
            'show_completed': request_params['show_completed'],
            'primary_filter': request_params['primary_filter'],
            'secondary_filter': request_params['secondary_filter'],
            'entity_filter': request_params['entity_filter'],
            
            # Relationship labels for dynamic pluralization
            'relationship_labels': relationship_labels
        }
    
    @staticmethod
    def _parse_request_params() -> Dict[str, Any]:
        """Parse request parameters into simple variables - ADR-017"""
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
    
    @staticmethod
    def _build_entity_config(entity_name: str) -> Dict[str, Any]:
        """Build entity configuration from model metadata - ADR-016"""
        # Use registry instead of direct model access
        metadata = ModelRegistry.get_model_metadata(entity_name)

        # Simple entity button - no complex generator needed
        entity_buttons = [entity_name]  # Template will derive button properties

        return {
            'entity_name': metadata.display_name_plural,
            'entity_name_singular': metadata.display_name,
            'entity_description': metadata.description or f"Manage your {metadata.display_name_plural.lower()}",
            'entity_type': metadata.display_name.lower(),
            'entity_endpoint': metadata.api_endpoint,
            'entity_buttons': entity_buttons
        }
    @staticmethod
    def _build_ui_config(entity_name: str, request_params: Dict, **kwargs) -> Dict[str, Any]:
        """Build UI configuration with defaults and overrides - ADR-017"""
        metadata = ModelRegistry.get_model_metadata(entity_name)

        return {
            'show_filters': kwargs.get('show_filters', True),
            'show_grouping': kwargs.get('show_grouping', True),
            'show_sorting': kwargs.get('show_sorting', True),
            'show_search': kwargs.get('show_search', True),
            'items_per_page': kwargs.get('items_per_page', metadata.list_per_page),
            'default_view': kwargs.get('default_view', 'card'),
            'available_filters': metadata.list_filters,
            'active_filters': {k: v for k, v in request_params.items() if v and k.endswith('_filter')},
            'available_sorts': [field for field, meta in metadata.fields.items()
                               if meta.sortable],
            'active_sort': {'field': request_params['sort_by'], 'direction': request_params['sort_direction']}
                           if request_params['sort_by'] else None,
            'available_groups': [field for field, meta in metadata.fields.items()
                                if meta.filterable and field != 'id'],
            'active_group': request_params['group_by'] if request_params['group_by'] else None
        }
    @staticmethod
    def _build_dropdown_configs(entity_name: str, request_params: Dict) -> Dict[str, Dict[str, Any]]:
        """Build dropdown configurations using ModelIntrospector"""
        from app.utils.core.model_introspection import ModelIntrospector, get_model_by_name

        model_class = get_model_by_name(entity_name)
        if not model_class:
            return {}

        dropdown_configs = {}

        # Build group_by dropdown
        groupable_fields = ModelIntrospector.get_groupable_fields(model_class)
        if groupable_fields:
            options = [{'value': field, 'label': label} for field, label in groupable_fields]
            dropdown_configs['group_by'] = {
                'options': options,
                'selected_values': [request_params.get('group_by', '')] if request_params.get('group_by') else [],
                'placeholder': 'Group by...'
            }

        # Build sort_by dropdown
        sortable_fields = ModelIntrospector.get_sortable_fields(model_class)
        if sortable_fields:
            options = [{'value': field, 'label': label} for field, label in sortable_fields]
            dropdown_configs['sort_by'] = {
                'options': options,
                'selected_values': [request_params.get('sort_by', '')] if request_params.get('sort_by') else [],
                'placeholder': 'Sort by...'
            }

        # Build sort_direction dropdown
        dropdown_configs['sort_direction'] = {
            'options': [
                {'value': 'asc', 'label': 'Ascending'},
                {'value': 'desc', 'label': 'Descending'}
            ],
            'selected_values': [request_params.get('sort_direction', 'asc')],
            'placeholder': 'Order'
        }

        return dropdown_configs
    
    @staticmethod
    def _build_relationship_labels() -> Dict[str, Dict[str, str]]:
        """
        Build relationship labels dynamically from all registered models - ADR-016
        
        Returns:
            Dict mapping relationship names to singular/plural labels
        """
        labels = {}
        
        # Get all registered models from registry
        for model_name in ModelRegistry.list_models():
            try:
                metadata = ModelRegistry.get_model_metadata(model_name)
                
                # Add primary endpoint mapping
                labels[model_name] = {
                    'singular': metadata.display_name,
                    'plural': metadata.display_name_plural
                }
                
                # Add common aliases based on model type
                model_class = ModelRegistry.get_model(model_name)
                if hasattr(model_class, '__name__'):
                    if model_class.__name__ == 'Stakeholder':
                        labels['contacts'] = {
                            'singular': metadata.display_name,
                            'plural': metadata.display_name_plural
                        }
                    elif model_class.__name__ == 'User':
                        labels['team_members'] = {
                            'singular': metadata.display_name,
                            'plural': metadata.display_name_plural
                        }
                        
            except Exception:
                # Skip models that can't be processed
                continue
        
        return labels
    
    @staticmethod
    def get_standardized_index_context(entity_name: str, 
                                     entities_data: List[Dict] = None,
                                     default_group_by: str = None, 
                                     default_sort_by: str = None, 
                                     additional_context: Dict = None) -> Dict[str, Any]:
        """
        Get complete standardized context for entity index routes - ADR-017
        
        Args:
            entity_name: Entity type
            entities_data: List of entity data
            default_group_by: Default grouping
            default_sort_by: Default sorting  
            additional_context: Extra context specific to entity
            
        Returns:
            Complete context ready for entity_index.html template
        """
        context = UniversalContextBuilder.build_entity_index_context(
            entity_name=entity_name,
            entities_data=entities_data,
            default_group_by=default_group_by,
            default_sort_by=default_sort_by
        )
        
        # Merge any additional context
        if additional_context:
            context.update(additional_context)
            
        return context