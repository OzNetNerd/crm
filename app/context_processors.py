"""
Flask Context Processors
Automatically makes data available to all templates without explicit passing
"""

from app.utils.model_introspection import get_all_model_configs


def inject_model_configs():
    """
    Make model configurations available to all templates.
    This provides JavaScript with server-side model metadata for dynamic configuration.
    
    Returns:
        dict: Template variables including model_configs
    """
    try:
        model_configs = get_all_model_configs()
        return {
            'model_configs': model_configs
        }
    except Exception as e:
        # Graceful degradation - return empty configs if there's an error
        print(f"Warning: Failed to load model configs in context processor: {e}")
        return {
            'model_configs': {}
        }