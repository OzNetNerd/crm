"""
Simple Model Registry - DRY model lookup without unnecessary abstraction.

Uses the existing get_entity_config() auto-generation instead of duplicating
field discovery and pluralization logic.
"""

# Simple dict to store model classes
MODELS = {}


def register_model(model_class, name=None):
    """
    Register a model class for dynamic access.

    Args:
        model_class: The model class to register
        name: Optional custom name (defaults to class name lowercased)

    Returns:
        The model class (for decorator usage)
    """
    name = name or model_class.__name__.lower()
    MODELS[name] = model_class
    return model_class


def get_model(name):
    """
    Get model class by name.

    Args:
        name: Model name (case-insensitive)

    Returns:
        Model class or None if not found
    """
    return MODELS.get(name.lower())


def list_models():
    """
    Get all registered model names.

    Returns:
        List of registered model names
    """
    return list(MODELS.keys())


# Alias for backward compatibility
get_model_by_name = get_model