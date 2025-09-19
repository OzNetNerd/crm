"""
Task form - For creating and editing tasks.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DateField,
    HiddenField,
    RadioField,
    SelectField,
    ValidationError,
)
from wtforms.validators import DataRequired, Optional, Length


class TaskForm(FlaskForm):
    """Form for creating/editing tasks."""

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
        validators=[Optional()],
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

    due_date = DateField("Due Date", validators=[Optional()], format="%Y-%m-%d")

    # Related entities
    assigned_to_id = StringField(
        "Assignees",
        validators=[Optional()],
        render_kw={
            "data-search-type": "assignment",
            "placeholder": "Search assignees...",
            "autocomplete": "off",
        },
    )

    company_id = StringField(
        "Company",
        validators=[Optional()],
        render_kw={
            "data-search-type": "company",
            "placeholder": "Search companies...",
            "autocomplete": "off",
        },
    )

    opportunity_id = StringField(
        "Opportunity",
        validators=[Optional()],
        render_kw={
            "data-search-type": "opportunity",
            "placeholder": "Search opportunities...",
            "autocomplete": "off",
        },
    )

    parent_task_id = HiddenField("Parent Task ID")

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
            "assigned_to_id",  # Assignees
            "name",  # Task Name
            "task_type",  # Task Type (first in inline group)
            "priority",  # Priority (second in inline group)
            "status",  # Status (third in inline group)
            "description",  # Description
            "due_date",  # Due Date with enhancements
            # Note: parent_task_id is excluded (HiddenField should not display)
        ]
