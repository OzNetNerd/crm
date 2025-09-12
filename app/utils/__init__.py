"""
App Utils - Reorganized for better maintainability

This package provides utilities organized by logical function:
- core/: Core system utilities (model introspection, base handlers)
- forms/: Form-related utilities (dynamic forms, configs)
- entities/: Entity management (helpers, icons, configs)
- ui/: UI-specific helpers (modals, templates, index helpers)
- legacy/: Deprecated files (for backwards compatibility)

Key imports available at package level for backwards compatibility:
"""

# Core utilities
from .core import (
    ModelIntrospector,
    get_model_by_name,
    get_all_model_configs,
    BaseRouteHandler,
    GenericAPIHandler,
    NotesAPIHandler,
    EntityFilterManager,
    EntityGrouper,
    parse_date_field,
    parse_int_field,
    get_entity_data_for_forms
)

# Form utilities  
from .forms import (
    DynamicFormBuilder,
    FormConfigManager,
    DynamicChoiceProvider,
    DropdownConfigGenerator,
    create_form_for_model
)

# Entity utilities
from .entities import (
    EntityManager,
    StakeholderManager,
    TeamManager,
    TaskEntityManager,
    get_entities_for_forms,
    assign_stakeholder_role,
    get_entity_tasks,
    get_entity_icon_name,
    get_icon_function_name,
    get_entity_icon_html,
    get_entity_semantic,
    get_dashboard_entities,
    generate_entity_buttons,
)

# UI utilities
from .ui import (
    # ModalService,  # Temporarily removed to avoid circular import
    get_modal_config,
    get_detail_modal_config,
    MODAL_CONFIGS,
    DETAIL_MODAL_CONFIGS,
    style_task_description,
    safe_tojson,
    register_template_filters,
    get_field_options,
    get_sortable_fields,
    get_groupable_fields,
    get_model_form_fields,
    get_model_config,
    UniversalIndexHelper,
    PRIORITY_OPTIONS,
    SIZE_OPTIONS
)

# Auto serialize utility from model_helpers
from .old_legacy.model_helpers import auto_serialize

# Make commonly used functions available at package level
__all__ = [
    # Core
    'ModelIntrospector',
    'get_model_by_name',
    'BaseRouteHandler',
    'GenericAPIHandler',
    'EntityFilterManager',
    'EntityGrouper',
    
    # Forms
    'DynamicFormBuilder',
    'DropdownConfigGenerator',
    'create_form_for_model',
    
    # Entities
    'EntityManager',
    'get_entities_for_forms',
    'get_dashboard_entities',
    
    # UI
    # 'ModalService',  # Temporarily removed
    'get_modal_config',
    'get_detail_modal_config',
    'register_template_filters',
    'UniversalIndexHelper',
    
    # Utils
    'auto_serialize',
    'parse_date_field',
    'parse_int_field'
]