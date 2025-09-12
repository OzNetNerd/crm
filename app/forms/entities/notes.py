"""
Notes Forms

Note form with DRY field creation patterns.
"""

from wtforms import SelectField
from ..base.base_forms import BaseForm, FieldFactory, FormConstants


class NoteForm(BaseForm):
    """Note form using DRY FieldFactory patterns"""
    
    content = FieldFactory.create_note_content_field()
    
    is_internal = SelectField(
        "Note Type",
        choices=FormConstants.NOTE_TYPE_CHOICES,
        default="1",
        coerce=lambda x: x == "1"
    )