"""
Unified Entity Button Generator

DRY implementation for generating "New Entity" buttons consistently
across dashboard, index pages, and entity detail pages.

Eliminates hardcoded button configurations by leveraging model __entity_config__.
"""

from typing import List, Dict, Any, Union, Optional


class EntityButtonGenerator:
    """
    Unified generator for entity action buttons using model configurations.
    
    Replaces hardcoded button arrays and inconsistent URL generation
    with a single source of truth from model __entity_config__.
    """
    
    @staticmethod
    def get_model_by_entity_name(entity_name: str):
        """Get model class from entity name - dynamic mapping from model configs"""
        from app.utils.core.model_introspection import get_all_entity_models
        
        # Build mapping dynamically from model configurations
        all_models = get_all_entity_models()
        model_map = {}
        
        for model_class in all_models:
            config = model_class.__entity_config__
            endpoint_name = config.get('endpoint_name', model_class.__tablename__)
            model_map[endpoint_name] = model_class
        
        return model_map.get(entity_name.lower())
    
    @classmethod
    def generate_single_button(cls, entity_name: str) -> Dict[str, Any]:
        """
        Generate a single "New Entity" button from model configuration.
        
        Args:
            entity_name: Entity type (e.g., 'companies', 'teams')
            
        Returns:
            Button configuration dict ready for template use
        """
        model_class = cls.get_model_by_entity_name(entity_name)
        if not model_class:
            # Fallback for unknown entities
            return {
                'label': f'New {entity_name.title().rstrip("s")}',
                'hx_get': f'/modals/{entity_name.title().rstrip("s")}/create',
                'hx_target': 'body',
                'hx_swap': 'beforeend',
                'entity': entity_name
            }
        
        # Use model __entity_config__ for consistent URLs and labels
        entity_config = model_class.__entity_config__
        
        return {
            'label': f'New {entity_config.get("display_name_singular", "Item")}',
            'hx_get': f'{entity_config.get("modal_path", "/modals/Item")}/create',
            'hx_target': 'body',
            'hx_swap': 'beforeend',
            'entity': entity_name
        }
    
    @classmethod
    def generate_button_array(cls, entity_names: List[str]) -> List[Dict[str, Any]]:
        """
        Generate array of "New Entity" buttons from entity names.
        
        Args:
            entity_names: List of entity types (e.g., ['companies', 'teams'])
            
        Returns:
            List of button configuration dicts
        """
        return [cls.generate_single_button(entity_name) for entity_name in entity_names]
    
    @classmethod
    def generate_dashboard_buttons(cls) -> List[Dict[str, Any]]:
        """
        Generate standard dashboard buttons using model configurations.
        
        Returns:
            List of button configurations for all dashboard entities
        """
        from app.utils.core.model_introspection import get_all_entity_models
        
        # Get all models and filter for dashboard display
        all_models = get_all_entity_models()
        dashboard_entities = []
        
        for model_class in all_models:
            entity_config = model_class.__entity_config__
            if entity_config.get('show_dashboard_button', True):
                # Map model back to entity name
                entity_name = entity_config.get('endpoint_name', model_class.__tablename__)
                dashboard_entities.append(entity_name)
        
        return cls.generate_button_array(dashboard_entities)
    
    @classmethod
    def generate_relationship_buttons(cls, entity_relationships: List[str]) -> List[Dict[str, Any]]:
        """
        Generate buttons for entity relationship sections (e.g., company detail page).
        
        Args:
            entity_relationships: List of related entity types for this page
            
        Returns:
            List of button configurations for relationship entities
        """
        return cls.generate_button_array(entity_relationships)


class LegacyButtonConverter:
    """
    Converter for migrating from old hardcoded button patterns.
    
    Helps identify and convert legacy button configurations to use
    the new unified generator.
    """
    
    @staticmethod
    def convert_string_array_to_buttons(entity_strings: List[str]) -> List[Dict[str, Any]]:
        """
        Convert old string array format to new button configurations.
        
        Legacy: ['companies', 'tasks', 'opportunities']
        New: [{'label': 'New Company', 'hx_get': '/modals/Company/create', ...}, ...]
        
        Args:
            entity_strings: Legacy entity string array
            
        Returns:
            Modern button configuration array
        """
        return EntityButtonGenerator.generate_button_array(entity_strings)
    
    @staticmethod
    def validate_button_config(button_config: Dict[str, Any]) -> bool:
        """
        Validate that button config follows new DRY standards.
        
        Args:
            button_config: Button configuration to validate
            
        Returns:
            True if config follows DRY patterns, False if hardcoded
        """
        required_keys = ['label', 'hx_get', 'hx_target', 'hx_swap', 'entity']
        
        # Check for required keys
        if not all(key in button_config for key in required_keys):
            return False
        
        # Check for signs of hardcoded paths (should use model configs)
        hx_get = button_config.get('hx_get', '')
        if '/modals/' in hx_get and '/create' in hx_get:
            # Valid pattern, but check if it matches model config
            entity_name = button_config.get('entity', '')
            if entity_name:
                expected_button = EntityButtonGenerator.generate_single_button(entity_name)
                return button_config['hx_get'] == expected_button['hx_get']
        
        return False


# Convenience functions for backward compatibility during migration
def generate_entity_buttons(entity_names: Union[List[str], str]) -> List[Dict[str, Any]]:
    """
    Generate entity buttons from names or single name.
    
    Args:
        entity_names: Either list of entity names or single entity name
        
    Returns:
        List of button configurations
    """
    if isinstance(entity_names, str):
        return [EntityButtonGenerator.generate_single_button(entity_names)]
    return EntityButtonGenerator.generate_button_array(entity_names)


def get_dashboard_action_buttons() -> List[Dict[str, Any]]:
    """
    Get standard dashboard action buttons.
    
    Returns:
        List of dashboard button configurations
    """
    return EntityButtonGenerator.generate_dashboard_buttons()