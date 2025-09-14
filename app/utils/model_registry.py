"""
Simple Model Registry - DRY auto-generation approach

Eliminates manual configuration by auto-generating entity configs from class names.
Uses simple dictionaries instead of complex metadata framework.
"""

from typing import Dict, Type, Any

# Global model registry - populated automatically via EntityModel.__init_subclass__
MODELS: Dict[str, Type] = {}

# Pluralization mapping with fallback to +s
PLURAL_FORMS = {
    'Company': 'Companies',
    'User': 'Teams',
    'Opportunity': 'Opportunities',
    'Task': 'Tasks',
    'Stakeholder': 'Stakeholders'
}


def get_plural_form(singular_word: str) -> str:
    """Get plural form with fallback to +s"""
    return PLURAL_FORMS.get(singular_word, singular_word + 's')


def get_entity_config(model_class: Type) -> Dict[str, Any]:
    """Auto-generate entity config from class name - no manual config needed"""
    class_name = model_class.__name__
    plural_form = get_plural_form(class_name)

    return {
        'display_name_singular': class_name,
        'display_name': plural_form,
        'endpoint_name': plural_form.lower()
    }


def register_model(model_class: Type) -> None:
    """Register model in MODELS dict with auto-generated config"""
    config = get_entity_config(model_class)

    # Register with multiple lookup keys
    MODELS[model_class.__name__.lower()] = model_class
    MODELS[config['endpoint_name']] = model_class

    # Also register singular/plural display names for template usage
    MODELS[config['display_name_singular'].lower()] = model_class
    MODELS[config['display_name'].lower()] = model_class


def get_model(name: str) -> Type:
    """Get model class by name"""
    model_class = MODELS.get(name.lower())
    if not model_class:
        raise ValueError(f"Model '{name}' not registered in model registry")
    return model_class


def list_models() -> list:
    """Get all registered model names"""
    return list(MODELS.keys())


def get_display_names(model_name: str) -> Dict[str, str]:
    """Get display names for entity - compatibility with existing code"""
    model_class = get_model(model_name)
    config = get_entity_config(model_class)
    return {
        'singular': config['display_name_singular'],
        'plural': config['display_name']
    }