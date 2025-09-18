"""
Centralized Forms Module

This module provides all form classes and utilities for the CRM application.
All form-related code has been consolidated here for better maintainability.
"""

# Base form components
from .base.base_forms import BaseForm

# Task forms
from .tasks.task_forms import TaskForm, QuickTaskForm, ChildTaskForm, MultiTaskForm

# Entity forms
from .entities.notes import NoteForm


def get_field_choices(field_name):
    """Get choices for a specific field from the appropriate model."""
    # Map field names to models that contain them
    field_model_map = {
        "industry": "Company",
        "size": "Company",
        "status": "Opportunity",
        "stage": "Opportunity",
        "priority": "Task",
        "type": "Stakeholder",
    }

    model_name = field_model_map.get(field_name)
    if not model_name:
        return {}

    try:
        if model_name == "Company":
            from app.models.company import Company

            choices = Company.get_field_choices(field_name)
        elif model_name == "Opportunity":
            from app.models.opportunity import Opportunity

            choices = Opportunity.get_field_choices(field_name)
        elif model_name == "Task":
            from app.models.task import Task

            choices = Task.get_field_choices(field_name)
        elif model_name == "Stakeholder":
            from app.models.stakeholder import Stakeholder

            choices = Stakeholder.get_field_choices(field_name)
        else:
            return {}

        # Convert WTForms choices to our format
        choice_dict = {}
        for value, label in choices:
            if value:  # Skip empty values
                choice_dict[value] = {
                    "label": label,
                    "description": "",  # Could be enhanced later
                }

        return choice_dict
    except Exception:
        return {}


# Lazy imports for dynamic forms - will be created when accessed
def __getattr__(name):
    if name == "CompanyForm":
        from .entities.company import CompanyForm

        return CompanyForm
    elif name == "StakeholderForm":
        from .entities.stakeholder import StakeholderForm

        return StakeholderForm
    elif name == "OpportunityForm":
        from .entities.opportunity import OpportunityForm

        return OpportunityForm
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # Base components
    "BaseForm",
    # Task forms
    "TaskForm",
    "QuickTaskForm",
    "ChildTaskForm",
    "MultiTaskForm",
    # Entity forms
    "CompanyForm",
    "StakeholderForm",
    "OpportunityForm",
    "NoteForm",
]
