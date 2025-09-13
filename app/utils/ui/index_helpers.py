"""
Modernized Universal Index Helper - ADR-016/017 Compliant

Metadata-driven context builder using configuration objects and model registry.
Eliminates legacy patterns in favor of universal DRY principles.
"""

from typing import Dict, List, Any, Optional
from ..context_builders import UniversalContextBuilder
from ..frontend_contracts import FrontendContractValidator, ContextTransformer


class UniversalIndexHelper:
    """
    Modernized universal helper for entity index routes - ADR-016/017 compliant
    
    Uses metadata-driven configuration objects and model registry instead of
    legacy __entity_config__ patterns. Follows DRY principles from ADR-008.
    """
    
    @classmethod
    def parse_request_parameters(cls) -> Dict[str, Any]:
        """
        DEPRECATED: Use UniversalContextBuilder._parse_request_params() instead
        
        This method maintained for backward compatibility during transition.
        Will be removed in future version.
        
        Returns:
            dict: Standardized parameters for all entity types
        """
        return UniversalContextBuilder._parse_request_params()
    
    @classmethod
    def generate_entity_context(cls, entity_name: str, 
                              default_group_by: str = None, 
                              default_sort_by: str = None) -> Dict[str, Any]:
        """
        DEPRECATED: Use UniversalContextBuilder.build_entity_index_context() instead
        
        This method maintained for backward compatibility during transition.
        New implementation uses metadata-driven configuration objects.
        
        Args:
            entity_name: Entity type (e.g., 'companies', 'tasks', 'opportunities')
            default_group_by: Default grouping field
            default_sort_by: Default sorting field
            
        Returns:
            dict: Complete context for entity index template
        """
        return UniversalContextBuilder.build_entity_index_context(
            entity_name=entity_name,
            default_group_by=default_group_by,
            default_sort_by=default_sort_by
        )
    
    @classmethod
    def get_standardized_index_context(cls, entity_name: str, 
                                     entities_data: List[Dict] = None,
                                     default_group_by: str = None, 
                                     default_sort_by: str = None, 
                                     additional_context: Dict = None) -> Dict[str, Any]:
        """
        Get complete standardized context for entity index routes - ADR-017 compliant
        
        Uses new UniversalContextBuilder with configuration objects and validation.
        
        Args:
            entity_name: Entity type
            entities_data: List of entity data
            default_group_by: Default grouping
            default_sort_by: Default sorting  
            additional_context: Extra context specific to entity
            
        Returns:
            dict: Complete context ready for entity_index.html template
        """
        # Use new modernized context builder
        context = UniversalContextBuilder.get_standardized_index_context(
            entity_name=entity_name,
            entities_data=entities_data,
            default_group_by=default_group_by,
            default_sort_by=default_sort_by,
            additional_context=additional_context
        )
        
        # Validate context against frontend contracts
        is_valid = FrontendContractValidator.validate_and_report(
            context, f"{entity_name}_index_context"
        )
        
        if not is_valid:
            # Log validation errors but don't break functionality
            import logging
            logging.warning(f"Context validation failed for {entity_name} index")
        
        return context
    
    @classmethod
    def get_javascript_config(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get JavaScript-friendly configuration from context - ADR-017
        
        Args:
            context: Server-side context dictionary
            
        Returns:
            dict: JavaScript-ready configuration object
        """
        js_config = ContextTransformer.to_javascript_config(context)
        return js_config.to_json_safe()
    
    # Backward compatibility methods (deprecated)
    @classmethod
    def _build_relationship_labels(cls) -> Dict[str, Dict[str, str]]:
        """
        DEPRECATED: Use UniversalContextBuilder._build_relationship_labels() instead
        
        Maintained for backward compatibility during transition.
        """
        return UniversalContextBuilder._build_relationship_labels()


# Backward compatibility alias
class ModernizedIndexHelper(UniversalIndexHelper):
    """
    Modernized index helper - preferred class name for new implementations
    
    This class provides the same functionality as UniversalIndexHelper but
    with a name that clearly indicates it follows the new ADR standards.
    """
    pass