"""
Company Forms

Dynamic company form creation using DRY patterns.
"""

from ..base.base_forms import BaseForm
from ..base.builders import DynamicFormBuilder


# Lazy form creation with caching
_company_form_cache = None

def _get_company_form():
    """Lazy company form creation with caching"""
    global _company_form_cache
    if _company_form_cache is None:
        # Dynamic import to avoid circular imports
        from app.models.company import Company
        _company_form_cache = DynamicFormBuilder.build_dynamic_form(Company, BaseForm)
    return _company_form_cache

def __getattr__(name):
    """Lazy form creation for backward compatibility"""
    if name == 'CompanyForm':
        return _get_company_form()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Export for direct access
CompanyForm = None  # Will be set via __getattr__ when accessed