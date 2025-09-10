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
from app.models import Task
from app.utils.dynamic_form_builder import DynamicFormBuilder


class TaskForm(FlaskForm):
    description = TextAreaField(
        "Description",
        validators=[DataRequired(), Length(min=1, max=500)],
        render_kw={"placeholder": "What needs to be done?", "rows": 3},
    )

    due_date = DynamicFormBuilder.build_date_field(Task, 'due_date')

    priority = DynamicFormBuilder.build_select_field(Task, 'priority')

    status = DynamicFormBuilder.build_select_field(Task, 'status')

    next_step_type = DynamicFormBuilder.build_select_field(
        Task, 'next_step_type',
        validators=[Optional()]
    )

    # Multi-entity selection - JSON string of selected entities
    linked_entities = StringField(
        "Linked Entities",
        validators=[Optional()],
        render_kw={
            "data-entity-selector": "true",
            "placeholder": "Select companies, contacts, or opportunities",
        },
    )

    task_type = DynamicFormBuilder.build_select_field(Task, 'task_type')

    parent_task_id = IntegerField(
        "Parent Task", validators=[Optional(), NumberRange(min=1)]
    )

    sequence_order = IntegerField(
        "Sequence Order", validators=[Optional(), NumberRange(min=0)], default=0
    )

    dependency_type = DynamicFormBuilder.build_select_field(Task, 'dependency_type')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        # Validate linked_entities JSON if provided
        if self.linked_entities.data:
            try:
                import json

                entities = json.loads(self.linked_entities.data)
                if not isinstance(entities, list):
                    self.linked_entities.errors.append("Linked entities must be a list")
                    return False
                for entity in entities:
                    if (
                        not isinstance(entity, dict)
                        or "type" not in entity
                        or "id" not in entity
                    ):
                        self.linked_entities.errors.append(
                            "Each linked entity must have 'type' and 'id' fields"
                        )
                        return False
            except json.JSONDecodeError:
                self.linked_entities.errors.append(
                    "Invalid JSON format for linked entities"
                )
                return False

        # If task_type is child, parent_task_id must be provided
        if self.task_type.data == "child" and not self.parent_task_id.data:
            self.parent_task_id.errors.append("Parent task is required for child tasks")
            return False

        return True


class QuickTaskForm(FlaskForm):
    """Simplified form for quick task creation"""

    description = StringField(
        "Task",
        validators=[DataRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "Add a quick task...", "class": "form-control"},
    )

    priority = DynamicFormBuilder.build_select_field(Task, 'priority')


class ChildTaskForm(FlaskForm):
    """Form for child tasks in Multi Task creation"""

    description = TextAreaField(
        "Description",
        validators=[DataRequired(), Length(min=1, max=500)],
        render_kw={"placeholder": "Child task description...", "rows": 2},
    )

    due_date = DateField("Due Date", validators=[Optional()], default=None)

    priority = DynamicFormBuilder.build_select_field(Task, 'priority')

    next_step_type = DynamicFormBuilder.build_select_field(
        Task, 'next_step_type',
        validators=[Optional()]
    )


class MultiTaskForm(FlaskForm):
    """Form for creating parent tasks with multiple child tasks"""

    description = TextAreaField(
        "Parent Task Description",
        validators=[DataRequired(), Length(min=1, max=500)],
        render_kw={"placeholder": "What is the overall goal?", "rows": 3},
    )

    due_date = DateField("Overall Due Date", validators=[Optional()], default=None)

    priority = DynamicFormBuilder.build_select_field(Task, 'priority')

    # Multi-entity selection for parent task
    linked_entities = StringField(
        "Linked Entities",
        validators=[Optional()],
        render_kw={
            "data-entity-selector": "true",
            "placeholder": "Select companies, contacts, or opportunities",
        },
    )

    dependency_type = DynamicFormBuilder.build_select_field(Task, 'dependency_type')

    child_tasks = FieldList(
        FormField(ChildTaskForm), label="Child Tasks", min_entries=2, max_entries=10
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        # Validate linked_entities JSON if provided
        if self.linked_entities.data:
            try:
                import json

                entities = json.loads(self.linked_entities.data)
                if not isinstance(entities, list):
                    self.linked_entities.errors.append("Linked entities must be a list")
                    return False
                for entity in entities:
                    if (
                        not isinstance(entity, dict)
                        or "type" not in entity
                        or "id" not in entity
                    ):
                        self.linked_entities.errors.append(
                            "Each linked entity must have 'type' and 'id' fields"
                        )
                        return False
            except json.JSONDecodeError:
                self.linked_entities.errors.append(
                    "Invalid JSON format for linked entities"
                )
                return False

        # Ensure at least 2 child tasks
        if len(self.child_tasks.data) < 2:
            self.child_tasks.errors.append(
                "Multi Tasks must have at least 2 child tasks"
            )
            return False

        return True
