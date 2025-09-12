"""
Stakeholder Forms

Dynamic stakeholder form creation using DRY patterns.
"""

from ..base.base_forms import BaseForm
from ..base.builders import DynamicFormBuilder


# Lazy form creation with caching
_stakeholder_form_cache = None

def _get_stakeholder_form():
    """Lazy stakeholder form creation with caching"""
    global _stakeholder_form_cache
    if _stakeholder_form_cache is None:
        # Dynamic import to avoid circular imports
        from app.models.stakeholder import Stakeholder
        _stakeholder_form_cache = DynamicFormBuilder.build_dynamic_form(Stakeholder, BaseForm)
    return _stakeholder_form_cache

def __getattr__(name):
    """Lazy form creation for backward compatibility"""
    if name == 'StakeholderForm':
        return _get_stakeholder_form()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Export for direct access
StakeholderForm = None  # Will be set via __getattr__ when accessed