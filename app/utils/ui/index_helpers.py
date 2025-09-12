"""
Universal Index Helper - DRY consolidation for all entity index routes

Eliminates duplicate parameter parsing, data fetching, and context building
across all entity index functions by providing a single, consistent interface.
"""

from flask import request
from app.utils.forms.form_builder import DropdownConfigGenerator
from app.utils.entities.entity_config import EntityConfigGenerator


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
        dropdown_configs = DropdownConfigGenerator.generate_entity_dropdown_configs(
            entity_name=entity_name,
            group_by=params['group_by'],
            sort_by=params['sort_by'],
            sort_direction=params['sort_direction'],
            primary_filter=params['primary_filter']
        )
        
        # Generate entity configuration  
        model_class = DropdownConfigGenerator.get_model_by_entity_name(entity_name)
        entity_config = EntityConfigGenerator.generate_entity_page_config(entity_name, model_class)
        
        # Combine all context
        context = {
            **entity_config,
            'dropdown_configs': dropdown_configs,
            'request_params': params
        }
        
        return context
    
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