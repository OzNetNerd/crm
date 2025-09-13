"""Clean template global functions - no more string-based hacks."""

from app.models import db
from app.utils.core.model_introspection import ModelIntrospector, get_model_by_name
from app.config.entity_config import (
    get_entity_config, 
    get_entity_icon, 
    get_entity_labels, 
    get_empty_state_config
)
# Modal configs removed - using WTForms modal system now (keeping main branch approach)
# from app.utils.ui.modal_configs import get_modal_config, get_detail_modal_config, MODAL_CONFIGS, DETAIL_MODAL_CONFIGS
from app.utils.ui.button_generator import get_dashboard_action_buttons, generate_entity_buttons
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


def get_sortable_fields(model_class, exclude=None):
    """Get sortable field options for a model."""
    from app.models import Task, Opportunity, Company, Stakeholder, User
    
    exclude = exclude or ["id", "created_at", "updated_at"]
    options = []

    for column in model_class.__table__.columns:
        if column.name not in exclude:
            label = column.name.replace("_", " ").title()
            options.append({"value": column.name, "label": label})

    # Add computed fields based on model
    if model_class == Task:
        options.append({"value": "due_date", "label": "Due Date"})
    elif model_class == Opportunity:
        options.append({"value": "close_date", "label": "Close Date"})
        options.append({"value": "company_name", "label": "Company"})
    elif model_class == Company:
        options.append({"value": "name", "label": "Name"})
    elif model_class == Stakeholder:
        options.append({"value": "name", "label": "Name"})
        options.append({"value": "company_name", "label": "Company"})
    elif model_class == User:
        options.append({"value": "name", "label": "Name"})
        options.append({"value": "email", "label": "Email"})
        options.append({"value": "job_title", "label": "Job Title"})

    return sorted(options, key=lambda x: x["label"])


def get_groupable_fields(model_class):
    """Get fields suitable for grouping."""
    from app.models import Task, Opportunity, Company, Stakeholder, User
    
    options = []

    if model_class == Company:
        options = [
            {"value": "industry", "label": "Industry"},
            {"value": "size", "label": "Company Size"},
        ]
    elif model_class == Stakeholder:
        options = [
            {"value": "company_name", "label": "Company"},
            {"value": "role", "label": "Role"},
        ]
    elif model_class == Opportunity:
        options = [
            {"value": "stage", "label": "Pipeline Stage"},
            {"value": "priority", "label": "Priority"},
            {"value": "company_name", "label": "Company"},
        ]
    elif model_class == Task:
        options = [
            {"value": "status", "label": "Status"},
            {"value": "priority", "label": "Priority"},
            {"value": "entity_type", "label": "Entity Type"},
        ]
    elif model_class == User:
        options = [
            {"value": "job_title", "label": "Job Title"},
        ]

    return options


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


# Dashboard buttons now generated in templates using Jinja macros with entity names
