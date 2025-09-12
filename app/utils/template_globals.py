"""Clean template global functions - no more string-based hacks."""

from app.models import db, Company, Stakeholder, Task, Opportunity, User
from app.utils.model_introspection import ModelIntrospector, get_model_by_name
# Modal configs removed - using WTForms modal system now
# from app.utils.detail_modal_configs import get_detail_modal_config, DETAIL_MODAL_CONFIGS
from sqlalchemy import distinct


def get_field_options(model_class, field_name):
    """Get distinct values from a model field for filter dropdowns."""
    if not hasattr(model_class, field_name):
        return []

    field = getattr(model_class, field_name)
    distinct_values = db.session.query(distinct(field)).filter(field.isnot(None)).all()

    options = []
    for (value,) in distinct_values:
        if value:  # Skip empty/null values
            label = value.title() if isinstance(value, str) else str(value)
            options.append({"value": value, "label": label})

    return sorted(options, key=lambda x: x["label"])






# Standard priority options
PRIORITY_OPTIONS = [
    {"value": "low", "label": "Low"},
    {"value": "medium", "label": "Medium"},
    {"value": "high", "label": "High"},
]

# Standard size options for companies
SIZE_OPTIONS = [
    {"value": "startup", "label": "Startup"},
    {"value": "small", "label": "Small"},
    {"value": "medium", "label": "Medium"},
    {"value": "large", "label": "Large"},
    {"value": "enterprise", "label": "Enterprise"},
]


def get_model_form_fields(model_name):
    """
    Get form field definitions for a model by name.
    
    Args:
        model_name: String name of the model (e.g., 'Task', 'Company')
        
    Returns:
        List of form field definitions with name, type, label, choices, etc.
    """
    model_class = get_model_by_name(model_name)
    if not model_class:
        return []
    
    return ModelIntrospector.get_form_fields(model_class)


def get_model_config(model_class):
    """Get complete model configuration for templates."""
    return ModelIntrospector.get_model_config(model_class)


# Modal config functions removed - using WTForms modal system now
# def get_create_modal_config(entity_type):
#     """Get create modal configuration for a specific entity type."""
#     return get_modal_config(entity_type)

# def get_detail_modal_config(entity_type):
#     """Get detail modal configuration for a specific entity type."""  
#     return get_detail_modal_config(entity_type)


# Modal config functions removed - using WTForms modal system now
# def get_all_modal_configs():
#     """Get all modal configurations for bulk operations."""
#     return MODAL_CONFIGS

# def get_all_detail_modal_configs():
#     """Get all detail modal configurations for bulk operations.""" 
#     return DETAIL_MODAL_CONFIGS


def get_dashboard_buttons():
    """Get centralized dashboard buttons for DRY system."""
    from app.utils.entity_icons import get_dashboard_buttons
    return get_dashboard_buttons()
