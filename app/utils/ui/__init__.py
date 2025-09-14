"""
UI-specific utilities for modals, templates, and user interface components.
"""

# from .modal_service import ModalService  # Temporarily commented to avoid circular import

# Modal configs removed - replaced by forms.py and ModelRegistry

from .template_filters import (
    style_task_description,
    safe_tojson,
    register_template_filters
)

from .template_globals import (
    get_field_options,
    get_sortable_fields,
    get_groupable_fields,
    get_model_form_fields,
    get_model_config,
    PRIORITY_OPTIONS,
    SIZE_OPTIONS
)

# index_helpers removed - functionality replaced by simplified patterns

__all__ = [
    # 'ModalService',  # Temporarily removed
    'style_task_description',
    'safe_tojson',
    'register_template_filters',
    'get_field_options',
    'get_sortable_fields',
    'get_groupable_fields',
    'get_model_form_fields',
    'get_model_config',
    'PRIORITY_OPTIONS',
    'SIZE_OPTIONS'
]