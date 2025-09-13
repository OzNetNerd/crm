"""
Model Registry - Simple model lookup and metadata management
"""

from typing import Dict, List, Type
from .model_metadata import ModelMetadata


class ModelRegistry:
    """Simple model registry for dynamic model access"""
    _models: Dict[str, Type] = {}
    _metadata_cache: Dict[str, ModelMetadata] = {}

    @classmethod
    def register_model(cls, model_class: Type, name: str = None) -> Type:
        """Register a model class for dynamic access"""
        model_name = name or model_class.__name__.lower()
        cls._models[model_name] = model_class
        cls._metadata_cache[model_name] = ModelMetadata(model_class)
        return model_class

    @classmethod
    def get_model(cls, model_name: str) -> Type:
        """Get model class by name"""
        if model_name not in cls._models:
            raise ValueError(f"Model '{model_name}' not registered in ModelRegistry")
        return cls._models[model_name]

    @classmethod
    def get_model_metadata(cls, model_name: str) -> ModelMetadata:
        """Get cached metadata for model"""
        if model_name not in cls._metadata_cache:
            model_class = cls.get_model(model_name)
            cls._metadata_cache[model_name] = ModelMetadata(model_class)
        return cls._metadata_cache[model_name]

    @classmethod
    def list_models(cls) -> List[str]:
        """Get all registered model names"""
        return list(cls._models.keys())

    @classmethod
    def get_display_names(cls, model_name: str) -> Dict[str, str]:
        """Get display names for entity"""
        metadata = cls.get_model_metadata(model_name)
        return {
            'singular': metadata.display_name,
            'plural': metadata.display_name_plural
        }