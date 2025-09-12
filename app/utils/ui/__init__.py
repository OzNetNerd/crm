"""
UI-specific utilities for modals, templates, and user interface components.
"""

# from .modal_service import ModalService  # Temporarily commented to avoid circular import

from .modal_configs import (
    get_modal_config,
    get_detail_modal_config,
    MODAL_CONFIGS,
    DETAIL_MODAL_CONFIGS
)

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

from .index_helpers import (
    UniversalIndexHelper
)

__all__ = [
    # 'ModalService',  # Temporarily removed
    'get_modal_config',
    'get_detail_modal_config',
    'MODAL_CONFIGS',
    'DETAIL_MODAL_CONFIGS',
    'style_task_description',
    'safe_tojson',
    'register_template_filters',
    'get_field_options',
    'get_sortable_fields',
    'get_groupable_fields',
    'get_model_form_fields',
    'get_model_config',
    'UniversalIndexHelper',
    'PRIORITY_OPTIONS',
    'SIZE_OPTIONS'
]