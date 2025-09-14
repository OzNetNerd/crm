"""
Task Modal Form

Explicit form class for Task modals with controlled field ordering and layout.
Layout: Entity (top) -> Description -> Priority/Due Date (side by side) -> Comments
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Optional
from app.models.task import Task


class TaskModalForm(FlaskForm):
    """
    Task modal form with explicit field ordering:
    1. Entity (searchable - Company, Opportunity, or Stakeholder)
    2. Description (required textarea)
    3. Priority (left) and Due Date (right) - side by side
    4. Comments (textarea)
    """

    # Field 1: Entity (simple search field)
    entity = StringField(
        'Related To',
        validators=[Optional()],
        render_kw={'placeholder': 'Search companies, contacts, opportunities...'}
    )

    # Field 2: Description (required, large text area)
    description = TextAreaField(
        'Description',
        validators=[DataRequired(), Length(max=1000)],
        render_kw={'rows': 3, 'placeholder': 'Describe the task...'}
    )

    # Field 3a: Priority (left side)
    priority = SelectField(
        'Priority',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    # Field 3b: Due Date (right side)
    due_date = DateField(
        'Due Date',
        validators=[Optional()],
        render_kw={'type': 'date'}
    )

    # Field 4: Comments (textarea, at bottom)
    comments = TextAreaField(
        'Comments',
        validators=[Optional()],
        render_kw={'rows': 3, 'placeholder': 'Additional notes...'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get priority choices from Task model metadata
        priority_choices = Task.get_field_choices('priority')
        self.priority.choices = [('', 'Select priority')] + priority_choices