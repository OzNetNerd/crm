"""
Flask Context Processors
Automatically makes data available to all templates without explicit passing
"""

from app.utils.model_introspection import get_all_model_configs
from app.utils.modal_configs import MODAL_CONFIGS
from app.utils.detail_modal_configs import DETAIL_MODAL_CONFIGS


def inject_model_configs():
    """
    Make model and modal configurations available to all templates.
    This provides templates with server-side metadata for dynamic configuration.
    
    Returns:
        dict: Template variables including model_configs, modal_configs, and detail_modal_configs
    """
    try:
        model_configs = get_all_model_configs()
        return {
            'model_configs': model_configs,
            'modal_configs': MODAL_CONFIGS,
            'detail_modal_configs': DETAIL_MODAL_CONFIGS
        }
    except Exception as e:
        # Graceful degradation - return empty configs if there's an error
        print(f"Warning: Failed to load configs in context processor: {e}")
        return {
            'model_configs': {},
            'modal_configs': {},
            'detail_modal_configs': {}
        }