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
from datetime import date


class TaskForm(FlaskForm):
    description = TextAreaField(
        "Description",
        validators=[DataRequired(), Length(min=1, max=500)],
        render_kw={"placeholder": "What needs to be done?", "rows": 3},
    )

    due_date = DateField("Due Date", validators=[Optional()], default=None)

    priority = SelectField(
        "Priority",
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
        validators=[DataRequired()],
    )

    status = SelectField(
        "Status",
        choices=[
            ("todo", "To Do"),
            ("in-progress", "In Progress"),
            ("complete", "Complete"),
        ],
        default="todo",
        validators=[DataRequired()],
    )

    next_step_type = SelectField(
        "Next Step Type",
        choices=[
            ("", "None"),
            ("call", "Call"),
            ("email", "Email"),
            ("meeting", "Meeting"),
            ("demo", "Demo"),
        ],
        default="",
        validators=[Optional()],
    )

    entity_type = SelectField(
        "Related To",
        choices=[
            ("", "None"),
            ("company", "Company"),
            ("contact", "Contact"),
            ("opportunity", "Opportunity"),
        ],
        default="",
        validators=[Optional()],
    )

    entity_id = IntegerField("Entity ID", validators=[Optional(), NumberRange(min=1)])

    task_type = SelectField(
        "Task Type",
        choices=[
            ("single", "Single Task"),
            ("parent", "Parent Task"),
            ("child", "Child Task"),
        ],
        default="single",
        validators=[DataRequired()],
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
        default="parallel",
        validators=[DataRequired()],
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        # If entity_type is specified, entity_id must be provided
        if self.entity_type.data and not self.entity_id.data:
            self.entity_id.errors.append(
                "Entity ID is required when entity type is specified"
            )
            return False

        # If task_type is child, parent_task_id must be provided
        if self.task_type.data == "child" and not self.parent_task_id.data:
            self.parent_task_id.errors.append("Parent task is required for child tasks")
            return False

        # Due date cannot be in the past for new tasks
        if self.due_date.data and self.due_date.data < date.today():
            # Allow past dates for existing tasks being updated
            pass

        return True


class QuickTaskForm(FlaskForm):
    """Simplified form for quick task creation"""

    description = StringField(
        "Task",
        validators=[DataRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "Add a quick task...", "class": "form-control"},
    )

    priority = SelectField(
        "Priority",
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
    )


class ChildTaskForm(FlaskForm):
    """Form for child tasks in Multi Task creation"""

    description = TextAreaField(
        "Description",
        validators=[DataRequired(), Length(min=1, max=500)],
        render_kw={"placeholder": "Child task description...", "rows": 2},
    )

    due_date = DateField("Due Date", validators=[Optional()], default=None)

    priority = SelectField(
        "Priority",
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
        validators=[DataRequired()],
    )

    next_step_type = SelectField(
        "Next Step Type",
        choices=[
            ("", "None"),
            ("call", "Call"),
            ("email", "Email"),
            ("meeting", "Meeting"),
            ("demo", "Demo"),
        ],
        default="",
        validators=[Optional()],
    )


class MultiTaskForm(FlaskForm):
    """Form for creating parent tasks with multiple child tasks"""

    description = TextAreaField(
        "Parent Task Description",
        validators=[DataRequired(), Length(min=1, max=500)],
        render_kw={"placeholder": "What is the overall goal?", "rows": 3},
    )

    due_date = DateField("Overall Due Date", validators=[Optional()], default=None)

    priority = SelectField(
        "Priority",
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
        validators=[DataRequired()],
    )

    entity_type = SelectField(
        "Related To",
        choices=[
            ("", "None"),
            ("company", "Company"),
            ("contact", "Contact"),
            ("opportunity", "Opportunity"),
        ],
        default="",
        validators=[Optional()],
    )

    entity_id = IntegerField("Entity ID", validators=[Optional(), NumberRange(min=1)])

    dependency_type = SelectField(
        "Child Task Dependencies",
        choices=[
            ("parallel", "Parallel (can run simultaneously)"),
            ("sequential", "Sequential (must complete in order)"),
        ],
        default="parallel",
        validators=[DataRequired()],
    )

    child_tasks = FieldList(
        FormField(ChildTaskForm), label="Child Tasks", min_entries=2, max_entries=10
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        # If entity_type is specified, entity_id must be provided
        if self.entity_type.data and not self.entity_id.data:
            self.entity_id.errors.append(
                "Entity ID is required when entity type is specified"
            )
            return False

        # Ensure at least 2 child tasks
        if len(self.child_tasks.data) < 2:
            self.child_tasks.errors.append(
                "Multi Tasks must have at least 2 child tasks"
            )
            return False

        return True
