"""
App Utils - Reorganized for better maintainability

This package provides utilities organized by logical function:
- core/: Core system utilities (model introspection, base handlers)
- forms/: Form-related utilities (dynamic forms, configs)
- entities/: Entity management (helpers, icons, configs)
- ui/: UI-specific helpers (modals, templates)
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

# Form utilities have been moved to app.forms module
# Import directly from app.forms for new code

# Entity utilities
from .entities import (
    EntityManager,
    StakeholderManager,
    TeamManager,
    TaskEntityManager,
    get_entities_for_forms,
    assign_stakeholder_role,
    get_entity_tasks,
)

# UI utilities
from .ui import (
    # ModalService,  # Temporarily removed to avoid circular import
    style_task_description,
    safe_tojson,
    register_template_filters,
    get_field_options,
    get_sortable_fields,
    get_groupable_fields,
    get_model_form_fields,
    get_model_config,
    PRIORITY_OPTIONS,
    SIZE_OPTIONS
)

# Auto serialize utility from model_helpers
from .core.model_helpers import auto_serialize

# Make commonly used functions available at package level
__all__ = [
    # Core
    'ModelIntrospector',
    'get_model_by_name',
    'BaseRouteHandler',
    'GenericAPIHandler',
    'EntityFilterManager',
    'EntityGrouper',
    
    # Forms (moved to app.forms module)
    # Import from app.forms for new code
    
    # Entities
    'EntityManager',
    'get_entities_for_forms',
    
    # UI
    # 'ModalService',  # Temporarily removed
    'register_template_filters',
    
    # Utils
    'auto_serialize',
    'parse_date_field',
    'parse_int_field'
]