"""Clean template global functions - no more string-based hacks."""

from app.models import db, Company, Stakeholder, Task, Opportunity
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

    return sorted(options, key=lambda x: x["label"])


def get_groupable_fields(model_class):
    """Get fields suitable for grouping."""
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
