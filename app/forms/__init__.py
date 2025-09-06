# from .task_forms import TaskForm, QuickTaskForm  # Disabled due to missing flask_wtf
from .entity_forms import CompanyForm, ContactForm, OpportunityForm, NoteForm

__all__ = [
    # 'TaskForm', 'QuickTaskForm',  # Disabled due to missing flask_wtf
    'CompanyForm', 'ContactForm', 'OpportunityForm', 'NoteForm'
]