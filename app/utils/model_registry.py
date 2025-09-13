"""
Universal Model Registry - ADR-016 Implementation

Centralized model discovery and metadata management system that replaces
scattered __entity_config__ access with unified registry pattern.
"""

from typing import Dict, List, Any, Optional, Type
from .model_metadata import ModelMetadata


class ModelRegistry:
    """
    Universal model registry for dynamic model access and metadata management
    
    Replaces direct model access patterns with centralized registry system
    following ADR-016 dynamic model and metadata management patterns.
    """
    _models: Dict[str, Type] = {}
    _metadata_cache: Dict[str, ModelMetadata] = {}
    
    @classmethod
    def register_model(cls, model_class: Type, name: str = None) -> Type:
        """
        Register a model class for dynamic access
        
        Args:
            model_class: The model class to register
            name: Optional custom name (defaults to lowercase class name)
            
        Returns:
            The registered model class (for use as decorator)
        """
        model_name = name or model_class.__name__.lower()
        cls._models[model_name] = model_class
        
        # Cache metadata on registration
        cls._metadata_cache[model_name] = ModelMetadata(model_class)
        
        return model_class
    
    @classmethod
    def get_model(cls, model_name: str) -> Type:
        """
        Get model class by name
        
        Args:
            model_name: Name of the model to retrieve
            
        Returns:
            Model class
            
        Raises:
            ValueError: If model not registered
        """
        if model_name not in cls._models:
            raise ValueError(f"Model '{model_name}' not registered in ModelRegistry")
        return cls._models[model_name]
    
    @classmethod
    def get_model_metadata(cls, model_name: str) -> ModelMetadata:
        """
        Get cached metadata for model
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelMetadata instance with comprehensive field and model information
        """
        if model_name not in cls._metadata_cache:
            model_class = cls.get_model(model_name)
            cls._metadata_cache[model_name] = ModelMetadata(model_class)
        return cls._metadata_cache[model_name]
    
    @classmethod
    def list_models(cls) -> List[str]:
        """
        Get all registered model names
        
        Returns:
            List of registered model names
        """
        return list(cls._models.keys())
    
    @classmethod
    def create_instance(cls, model_name: str, **kwargs) -> Any:
        """
        Create model instance with validation
        
        Args:
            model_name: Name of the model
            **kwargs: Field values for the instance
            
        Returns:
            New model instance
        """
        model_class = cls.get_model(model_name)
        metadata = cls.get_model_metadata(model_name)
        
        # Apply field validation from metadata
        validated_data = metadata.validate_data(kwargs)
        return model_class(**validated_data)
    
    @classmethod
    def get_entity_endpoint(cls, model_name: str) -> str:
        """
        Get API endpoint for entity
        
        Args:
            model_name: Name of the model
            
        Returns:
            API endpoint string
        """
        metadata = cls.get_model_metadata(model_name)
        return metadata.api_endpoint
    
    @classmethod
    def get_display_names(cls, model_name: str) -> Dict[str, str]:
        """
        Get display names for entity
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict with 'singular' and 'plural' display names
        """
        metadata = cls.get_model_metadata(model_name)
        return {
            'singular': metadata.display_name,
            'plural': metadata.display_name_plural
        }
    
    @classmethod
    def auto_register_from_entity_config(cls):
        """
        Auto-register models that have __entity_config__ (transitional method)
        
        This method provides backward compatibility during migration from
        legacy __entity_config__ patterns to the new registry system.
        """
        # Import here to avoid circular dependencies
        try:
            from app.utils.core.model_introspection import get_all_entity_models
            
            all_models = get_all_entity_models()
            for model_class in all_models:
                if hasattr(model_class, '__entity_config__'):
                    # Use endpoint_name from entity config as registry key
                    config = model_class.__entity_config__
                    endpoint_name = config.get('endpoint_name', model_class.__name__.lower())
                    
                    # Register with both endpoint name and class name
                    cls.register_model(model_class, endpoint_name)
                    cls.register_model(model_class, model_class.__name__.lower())
                    
                    # Also register plural forms for common patterns
                    if endpoint_name.endswith('s'):
                        singular_name = endpoint_name.rstrip('s')
                        if singular_name not in cls._models:
                            cls._models[singular_name] = model_class
                    else:
                        plural_name = endpoint_name + 's'
                        if plural_name not in cls._models:
                            cls._models[plural_name] = model_class
                            
        except ImportError:
            # Graceful fallback if model_introspection not available
            pass
    
    @classmethod
    def clear_cache(cls):
        """Clear metadata cache - useful for testing"""
        cls._metadata_cache.clear()
    
    @classmethod
    def refresh_metadata(cls, model_name: str):
        """
        Refresh cached metadata for a model
        
        Args:
            model_name: Name of the model to refresh
        """
        if model_name in cls._models:
            cls._metadata_cache[model_name] = ModelMetadata(cls._models[model_name])


# Initialize registry with existing models
ModelRegistry.auto_register_from_entity_config()