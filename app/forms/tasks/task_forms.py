"""
Task Forms

Direct, simple task form definitions using standard WTForms.
No unnecessary abstractions or factory methods.
"""

from wtforms import (
    StringField,
    TextAreaField,
    DateField,
    IntegerField,
    SelectField,
    FieldList,
    FormField,
    RadioField,
    ValidationError,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional as OptionalValidator,
    NumberRange,
)
from ..base.base_forms import BaseForm


class TaskForm(BaseForm):
    """Complete task form with all available fields"""

    # Task category selector
    task_category = RadioField(
        "Task Category",
        choices=[("opportunity", "Opportunity"), ("internal", "Internal")],
        default="opportunity",
        validators=[DataRequired()],
    )

    name = StringField(
        "Task Name",
        validators=[DataRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "Enter task name"},
    )

    description = TextAreaField(
        "Description",
        validators=[OptionalValidator()],
        render_kw={"placeholder": "Task description", "rows": 4},
    )

    task_type = SelectField(
        "Task Type",
        validators=[DataRequired()],
        choices=[],  # Will be populated in __init__
        render_kw={"class": "form-select"},
    )

    status = SelectField(
        "Status",
        validators=[DataRequired()],
        choices=[],  # Will be populated in __init__
        default="todo",
        render_kw={"class": "form-select"},
    )

    priority = SelectField(
        "Priority",
        validators=[DataRequired()],
        choices=[],  # Will be populated in __init__
        default="medium",
        render_kw={"class": "form-select"},
    )

    due_date = DateField("Due Date", validators=[OptionalValidator()])

    # Related entities
    assigned_to_id = StringField(
        "Assigned To",
        validators=[OptionalValidator()],
        render_kw={
            "placeholder": "Search team members...",
            "autocomplete": "off",
        },
    )

    company_id = StringField(
        "Company",
        validators=[OptionalValidator()],
        render_kw={
            "placeholder": "Search companies...",
            "autocomplete": "off",
        },
    )

    opportunity_id = StringField(
        "Opportunity",
        validators=[OptionalValidator()],
        render_kw={
            "placeholder": "Search opportunities...",
            "autocomplete": "off",
        },
    )

    next_step_type = SelectField(
        "Next Step Type", validators=[OptionalValidator()], choices=[]
    )
    linked_entities = StringField(
        "Linked Entities",
        validators=[OptionalValidator()],
        render_kw={
            "data-entity-selector": "true",
            "placeholder": "Select companies, contacts, or opportunities",
        },
    )
    parent_task_id = IntegerField(
        "Parent Task", validators=[OptionalValidator(), NumberRange(min=1)]
    )
    sequence_order = IntegerField(
        "Sequence Order",
        validators=[OptionalValidator(), NumberRange(min=0)],
        default=0,
    )
    dependency_type = SelectField(
        "Dependency Type", validators=[OptionalValidator()], choices=[]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices from model
        from app.models.task import Task
        from app.services import MetadataService

        # Get Task field metadata for choices
        metadata = MetadataService.get_field_metadata(Task)

        # Populate task_type choices
        if "task_type" in metadata and metadata["task_type"].get("choices"):
            self.task_type.choices = [
                (key, data["label"])
                for key, data in metadata["task_type"]["choices"].items()
            ]

        # Populate status choices
        if "status" in metadata and metadata["status"].get("choices"):
            self.status.choices = [
                (key, data["label"])
                for key, data in metadata["status"]["choices"].items()
            ]

        # Populate priority choices
        if "priority" in metadata and metadata["priority"].get("choices"):
            self.priority.choices = [
                (key, data["label"])
                for key, data in metadata["priority"]["choices"].items()
            ]

        # Populate remaining SelectField choices
        self.next_step_type.choices = [
            ("", "Select next step type")
        ] + Task.get_field_choices("next_step_type")
        self.dependency_type.choices = [
            ("", "Select dependency type")
        ] + Task.get_field_choices("dependency_type")

    def validate_company_id(self, field):
        """Validate that Company is required for Opportunity tasks."""
        if self.task_category.data == "opportunity" and not field.data:
            raise ValidationError("Company is required for Opportunity tasks.")

    def get_display_fields(self):
        """Define field order for modal display."""
        return [
            "task_category",  # Radio buttons at top
            "company_id",  # Company (conditional)
            "opportunity_id",  # Opportunity (conditional)
            "name",  # Task Name
            "description",  # Description
            "task_type",  # Task Type (first in inline group)
            "priority",  # Priority (second in inline group)
            "status",  # Status (third in inline group)
            "due_date",  # Due Date with enhancements
            "assigned_to_id",  # Assigned To
        ]

    def validate(self, extra_validators=None):
        """Validation using base class methods"""
        if not super().validate(extra_validators):
            return False

        # Validate linked_entities JSON if provided
        if not self.validate_linked_entities_json(self.linked_entities):
            return False

        # Validate parent-child task relationship
        if not self.validate_parent_task_relationship(
            self.parent_task_id, self.task_type
        ):
            return False

        return True


class QuickTaskForm(BaseForm):
    """Simplified form for quick task creation"""

    description = StringField(
        "Task",
        validators=[DataRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "Add a quick task...", "class": "form-control"},
    )
    priority = SelectField("Priority", validators=[OptionalValidator()], choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models.task import Task

        self.priority.choices = [("", "Select priority")] + Task.get_field_choices(
            "priority"
        )


class ChildTaskForm(BaseForm):
    """Form for child tasks in Multi Task creation"""

    description = TextAreaField(
        "Description",
        validators=[DataRequired()],
        render_kw={"placeholder": "Child task description...", "rows": 2},
    )
    due_date = DateField("Due Date", validators=[OptionalValidator()])
    priority = SelectField("Priority", validators=[OptionalValidator()], choices=[])
    next_step_type = SelectField(
        "Next Step Type", validators=[OptionalValidator()], choices=[]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models.task import Task

        self.priority.choices = [("", "Select priority")] + Task.get_field_choices(
            "priority"
        )
        self.next_step_type.choices = [
            ("", "Select next step type")
        ] + Task.get_field_choices("next_step_type")


class MultiTaskForm(BaseForm):
    """Form for creating parent tasks with multiple child tasks"""

    description = TextAreaField(
        "Parent Task Description",
        validators=[DataRequired()],
        render_kw={"placeholder": "What is the overall goal?", "rows": 3},
    )
    due_date = DateField("Overall Due Date", validators=[OptionalValidator()])
    priority = SelectField("Priority", validators=[OptionalValidator()], choices=[])
    dependency_type = SelectField(
        "Dependency Type", validators=[OptionalValidator()], choices=[]
    )

    # Entity selection
    entity_type = SelectField(
        "Related To",
        choices=[
            ("", "None"),
            ("company", "Company"),
            ("stakeholder", "Stakeholder"),
            ("opportunity", "Opportunity"),
        ],
        validators=[OptionalValidator()],
    )
    entity_id = IntegerField("Select Entity", validators=[OptionalValidator()])

    child_tasks = FieldList(FormField(ChildTaskForm), min_entries=2, max_entries=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models.task import Task

        self.priority.choices = [("", "Select priority")] + Task.get_field_choices(
            "priority"
        )
        self.dependency_type.choices = [
            ("", "Select dependency type")
        ] + Task.get_field_choices("dependency_type")

    def validate(self, extra_validators=None):
        """Validation for multi-task requirements"""
        if not super().validate(extra_validators):
            return False

        # Validate minimum child tasks
        if not self.validate_multi_task_children(self.child_tasks, min_children=2):
            return False

        return True
