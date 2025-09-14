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

# Entity utilities - EntityManager removed, use MODEL_REGISTRY from app.models instead

# UI utilities
# All UI template functions have been removed - models now handle their own choices

# Auto serialize moved to BaseModel - no longer needed here

# Make commonly used functions available at package level
__all__ = [
    # Core - ModelIntrospector removed, use model methods directly

    # Forms (moved to app.forms module)
    # Import from app.forms for new code

    # Entities - removed, use MODEL_REGISTRY from app.models

    # UI
    # 'ModalService',  # Temporarily removed
    # 'UniversalIndexHelper', # removed - using DRY route helpers instead

    # Utils
    'auto_serialize'
]