"""
Opportunity Forms

Dynamic opportunity form creation using DRY patterns.
"""

from ..base.base_forms import BaseForm
from ..base.builders import DynamicFormBuilder


# Lazy form creation with caching
_opportunity_form_cache = None

def _get_opportunity_form():
    """Lazy opportunity form creation with caching"""
    global _opportunity_form_cache
    if _opportunity_form_cache is None:
        # Dynamic import to avoid circular imports
        from app.models.opportunity import Opportunity
        _opportunity_form_cache = DynamicFormBuilder.build_dynamic_form(Opportunity, BaseForm)
    return _opportunity_form_cache

def __getattr__(name):
    """Lazy form creation for backward compatibility"""
    if name == 'OpportunityForm':
        return _get_opportunity_form()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Export for direct access
OpportunityForm = None  # Will be set via __getattr__ when accessed