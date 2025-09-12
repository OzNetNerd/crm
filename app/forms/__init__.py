from .base_forms import BaseForm, FieldFactory, FormConstants
from .task_forms import TaskForm, QuickTaskForm, MultiTaskForm
from .entity_forms import NoteForm

# Lazy imports for dynamic forms - will be created when accessed
def __getattr__(name):
    if name in ['CompanyForm', 'StakeholderForm', 'OpportunityForm']:
        from .entity_forms import __getattr__ as entity_getattr
        return entity_getattr(name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "BaseForm",
    "FieldFactory", 
    "FormConstants",
    "TaskForm",
    "QuickTaskForm",
    "MultiTaskForm",
    "CompanyForm",
    "StakeholderForm", 
    "OpportunityForm",
    "NoteForm",
]
