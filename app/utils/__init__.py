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

# Core utilities - ModelIntrospector removed (use model methods directly)

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
    # UniversalIndexHelper removed - using DRY route helpers instead
    PRIORITY_OPTIONS,
    SIZE_OPTIONS
)

# Auto serialize moved to BaseModel - no longer needed here

# Make commonly used functions available at package level
__all__ = [
    # Core - ModelIntrospector removed, use model methods directly

    # Forms (moved to app.forms module)
    # Import from app.forms for new code

    # Entities
    'EntityManager',
    'get_entities_for_forms',

    # UI
    # 'ModalService',  # Temporarily removed
    'register_template_filters',
    # 'UniversalIndexHelper', # removed - using DRY route helpers instead

    # Utils
    'auto_serialize'
]