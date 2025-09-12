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

    due_date = DateField("Due Date", validators=[Optional()])

    priority = SelectField(
        "Priority", 
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], 
        validators=[Optional()]
    )

    status = SelectField(
        "Status",
        choices=[("todo", "To Do"), ("in-progress", "In Progress"), ("complete", "Complete")],
        validators=[Optional()]
    )

    next_step_type = SelectField(
        "Next Step Type",
        choices=[("call", "Call"), ("email", "Email"), ("meeting", "Meeting"), ("demo", "Demo")],
        validators=[Optional()]
    )

    # Multi-entity selection - JSON string of selected entities
    linked_entities = FieldFactory.create_linked_entities_field()

    task_type = SelectField(
        "Task Type",
        choices=[("single", "Single Task"), ("parent", "Parent Task"), ("child", "Child Task")],
        validators=[Optional()]
    )

    parent_task_id = IntegerField(
        "Parent Task", validators=[Optional(), NumberRange(min=1)]
    )

    sequence_order = IntegerField(
        "Sequence Order", validators=[Optional(), NumberRange(min=0)], default=0
    )

    dependency_type = SelectField(
        "Dependency Type",
        choices=[("parallel", "Parallel"), ("sequential", "Sequential")],
        validators=[Optional()]
    )

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

    priority = SelectField(
        "Priority", 
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], 
        validators=[Optional()]
    )


class ChildTaskForm(BaseForm):
    """Form for child tasks in Multi Task creation"""

    description = FieldFactory.create_description_field(
        placeholder="Child task description...",
        rows=FormConstants.CHILD_TASK_ROWS
    )

    due_date = FieldFactory.create_due_date_field(label="Due Date")

    priority = SelectField(
        "Priority", 
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], 
        validators=[Optional()]
    )

    next_step_type = SelectField(
        "Next Step Type",
        choices=[("call", "Call"), ("email", "Email"), ("meeting", "Meeting"), ("demo", "Demo")],
        validators=[Optional()]
    )


class MultiTaskForm(BaseForm):
    """Form for creating parent tasks with multiple child tasks"""

    description = FieldFactory.create_description_field(
        label="Parent Task Description",
        placeholder="What is the overall goal?"
    )

    due_date = FieldFactory.create_due_date_field(label="Overall Due Date")

    priority = SelectField(
        "Priority", 
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], 
        validators=[Optional()]
    )

    # Simple entity selection for parent task
    entity_type = SelectField(
        "Related To",
        choices=[
            ("", "None"),
            ("company", "Company"),
            ("stakeholder", "Stakeholder"), 
            ("opportunity", "Opportunity")
        ],
        validators=[Optional()]
    )
    
    entity_id = IntegerField(
        "Select Entity",
        validators=[Optional()]
    )

    dependency_type = SelectField(
        "Dependency Type",
        choices=[("parallel", "Parallel"), ("sequential", "Sequential")],
        validators=[Optional()]
    )

    child_tasks = FieldList(
        FormField(ChildTaskForm), label="Child Tasks", min_entries=2, max_entries=10
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        # Validate linked_entities JSON if provided
        if not self.validate_linked_entities_json(self.linked_entities):
            return False

        # Ensure at least 2 child tasks
        if len(self.child_tasks.data) < 2:
            self.child_tasks.errors.append(
                "Multi Tasks must have at least 2 child tasks"
            )
            return False

        return True
