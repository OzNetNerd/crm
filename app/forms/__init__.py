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

# Lazy imports for dynamic forms - will be created when accessed
def __getattr__(name):
    if name == 'CompanyForm':
        from .entities.company import CompanyForm
        return CompanyForm
    elif name == 'StakeholderForm':
        from .entities.stakeholder import StakeholderForm
        return StakeholderForm
    elif name == 'OpportunityForm':
        from .entities.opportunity import OpportunityForm
        return OpportunityForm
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Base components
    'BaseForm',

    # Task forms
    'TaskForm', 'QuickTaskForm', 'ChildTaskForm', 'MultiTaskForm',

    # Entity forms
    'CompanyForm', 'StakeholderForm', 'OpportunityForm', 'NoteForm',
]
