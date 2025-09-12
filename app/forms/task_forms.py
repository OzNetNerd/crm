from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    DateField,
    IntegerField,
    FieldList,
    FormField,
)
from wtforms.validators import DataRequired, Length, Optional, NumberRange
# Task will be imported lazily to avoid circular imports
from app.utils.forms.form_builder import DynamicFormBuilder
from .base_forms import BaseForm, FieldFactory, FormConstants


class TaskForm(BaseForm):
    description = FieldFactory.create_description_field(
        placeholder="What needs to be done?"
    )

    due_date = FieldFactory.create_due_date_field()

    priority = FieldFactory.create_priority_field()

    status = FieldFactory.create_status_field()

    next_step_type = FieldFactory.create_next_step_type_field()

    # Multi-entity selection - JSON string of selected entities
    linked_entities = FieldFactory.create_linked_entities_field()

    task_type = FieldFactory.create_task_type_field()

    parent_task_id = IntegerField(
        "Parent Task", validators=[Optional(), NumberRange(min=1)]
    )

    sequence_order = IntegerField(
        "Sequence Order", validators=[Optional(), NumberRange(min=0)], default=0
    )

    dependency_type = FieldFactory.create_dependency_type_field()

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        # Validate linked_entities JSON if provided
        if not self.validate_linked_entities_json(self.linked_entities):
            return False

        # If task_type is child, parent_task_id must be provided
        if self.task_type.data == "child" and not self.parent_task_id.data:
            self.parent_task_id.errors.append("Parent task is required for child tasks")
            return False

        return True


class QuickTaskForm(BaseForm):
    """Simplified form for quick task creation"""

    description = StringField(
        "Task",
        validators=[DataRequired(), Length(min=1, max=FormConstants.QUICK_TASK_MAX_LENGTH)],
        render_kw={"placeholder": "Add a quick task...", "class": "form-control"},
    )

    priority = FieldFactory.create_priority_field()


class ChildTaskForm(BaseForm):
    """Form for child tasks in Multi Task creation"""

    description = FieldFactory.create_description_field(
        placeholder="Child task description...",
        rows=FormConstants.CHILD_TASK_ROWS
    )

    due_date = FieldFactory.create_due_date_field(label="Due Date")

    priority = FieldFactory.create_priority_field()

    next_step_type = FieldFactory.create_next_step_type_field()


class MultiTaskForm(BaseForm):
    """Form for creating parent tasks with multiple child tasks"""

    description = FieldFactory.create_description_field(
        label="Parent Task Description",
        placeholder="What is the overall goal?"
    )

    due_date = FieldFactory.create_due_date_field(label="Overall Due Date")

    priority = FieldFactory.create_priority_field()

    # Simple entity selection for parent task
    entity_type = SelectField(
        "Related To",
        choices=FormConstants.ENTITY_TYPE_CHOICES,
        validators=[Optional()]
    )
    
    entity_id = IntegerField(
        "Select Entity",
        validators=[Optional()]
    )

    dependency_type = FieldFactory.create_dependency_type_field()

    child_tasks = FieldList(
        FormField(ChildTaskForm), label="Child Tasks", min_entries=2, max_entries=10
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        # Ensure at least 2 child tasks
        if len(self.child_tasks.data) < 2:
            self.child_tasks.errors.append(
                "Multi Tasks must have at least 2 child tasks"
            )
            return False

        return True
