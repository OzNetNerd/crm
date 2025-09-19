from datetime import datetime
from typing import Dict, Any
from . import db
from .base import BaseModel
from ..utils.task_utils import (
    get_linked_entities,
    get_entity_attr,
    get_company_name,
    can_task_start,
    get_completion_percentage,
    get_next_available_child,
    add_linked_entity,
    remove_linked_entity,
    set_linked_entities,
)


# Junction table for task-entity relationships
task_entities = db.Table(
    "task_entities",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), nullable=False),
    db.Column("entity_type", db.String(50), nullable=False),
    db.Column("entity_id", db.Integer, nullable=False),
    db.Column("created_at", db.DateTime, default=datetime.utcnow),
)


class Task(BaseModel):
    """Task model with entity relationships and hierarchy management."""

    __tablename__ = "tasks"
    __display_name__ = "Task"
    __display_field__ = "description"
    __search_config__ = {
        "title_field": "description",
        "subtitle_fields": ["due_date", "priority", "status"],
    }

    # Serialization configuration
    __include_properties__ = [
        "is_overdue",
        "opportunity_value",
        "company_name",
        "opportunity_name",
        "opportunity_stage",
        "stakeholder_opportunity_name",
        "stakeholder_opportunity_value",
        "task_type_badge",
        "can_start",
        "completion_percentage",
    ]
    __relationship_transforms__ = {
        "linked_entities": lambda self: [
            {"type": entity["type"], "id": entity["id"], "name": entity["name"]}
            for entity in self.linked_entities
        ]
    }

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(
        db.Text,
        nullable=False,
        info={"display_label": "Description", "required": True, "form_include": True},
    )
    due_date = db.Column(
        db.Date,
        info={
            "display_label": "Due Date",
            "groupable": True,
            "sortable": True,
            "form_include": True,
            "date_groupings": {
                "overdue": "Overdue",
                "today": "Due Today",
                "this_week": "This Week",
                "later": "Later",
                "no_date": "No Due Date",
            },
        },
    )
    priority = db.Column(
        db.String(10),
        default="medium",
        info={
            "display_label": "Priority",
            "groupable": True,
            "sortable": True,
            "form_include": True,
            "choices": {
                "high": {"label": "High", "description": "Urgent priority"},
                "medium": {"label": "Medium", "description": "Normal priority"},
                "low": {"label": "Low", "description": "Low priority"},
            },
        },
    )
    status = db.Column(
        db.String(20),
        default="todo",
        info={
            "display_label": "Status",
            "groupable": True,
            "sortable": True,
            "choices": {
                "todo": {"label": "To Do", "description": "Not started"},
                "in-progress": {
                    "label": "In Progress",
                    "description": "Currently working on",
                },
                "complete": {"label": "Complete", "description": "Finished"},
            },
        },
    )
    next_step_type = db.Column(
        db.String(20),
        info={
            "display_label": "Next Step Type",
            "groupable": True,
            "sortable": True,
            "choices": {
                "call": {"label": "Call", "description": "Phone call"},
                "email": {"label": "Email", "description": "Send email"},
                "meeting": {
                    "label": "Meeting",
                    "description": "In-person or video meeting",
                },
                "demo": {"label": "Demo", "description": "Product demonstration"},
            },
        },
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Multi Task support
    task_type = db.Column(
        db.String(20),
        default="single",
        info={
            "display_label": "Task Type",
            "groupable": True,
            "sortable": True,
            "choices": {
                "parent": {"label": "Parent Task", "description": "Task with subtasks"},
                "child": {"label": "Child Task", "description": "Subtask of parent"},
            },
        },
    )
    parent_task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    sequence_order = db.Column(db.Integer, default=0)
    dependency_type = db.Column(
        db.String(20),
        default="parallel",
        info={
            "display_label": "Dependency Type",
            "groupable": True,
            "sortable": True,
            "choices": {
                "sequential": {
                    "label": "Sequential",
                    "description": "Must complete in order",
                }
            },
        },
    )

    comments = db.Column(
        db.Text, info={"display_label": "Comments", "form_include": True, "rows": 3, "sortable": False}
    )

    # Parent-child task relationships
    parent_task = db.relationship(
        "Task", remote_side="Task.id", back_populates="child_tasks"
    )
    child_tasks = db.relationship(
        "Task",
        back_populates="parent_task",
        order_by="Task.sequence_order",
        lazy="select",
    )

    # Properties using utility functions
    is_overdue = property(
        lambda self: bool(
            self.due_date
            and self.status != "complete"
            and self.due_date < datetime.utcnow().date()
        )
    )
    linked_entities = property(lambda self: get_linked_entities(self.id))
    opportunity_value = property(
        lambda self: get_entity_attr(self.id, "opportunity", "value")
    )
    company_name = property(lambda self: get_company_name(self.id))
    opportunity_name = property(
        lambda self: get_entity_attr(self.id, "opportunity", "name")
    )
    opportunity_stage = property(
        lambda self: get_entity_attr(self.id, "opportunity", "stage")
    )
    task_type_badge = property(
        lambda self: {"parent": "Parent", "child": "Child"}.get(
            self.task_type, "Single"
        )
    )
    can_start = property(lambda self: can_task_start(self))
    completion_percentage = property(lambda self: get_completion_percentage(self))
    next_available_child = property(lambda self: get_next_available_child(self))

    @property
    def stakeholder_opportunity_name(self):
        """Get primary opportunity name for contact tasks"""
        return self.opportunity_name or next(
            (
                entity["entity"].opportunities[0].name
                for entity in get_linked_entities(self.id)
                if entity["type"] == "contact"
                and entity["entity"]
                and entity["entity"].opportunities
            ),
            None,
        )

    @property
    def stakeholder_opportunity_value(self):
        """Get primary opportunity value for contact tasks"""
        return self.opportunity_value or next(
            (
                entity["entity"].opportunities[0].value
                for entity in get_linked_entities(self.id)
                if entity["type"] == "contact"
                and entity["entity"]
                and entity["entity"].opportunities
            ),
            None,
        )

    @property
    def due_date_display(self) -> str:
        """Format due date for display with relative time information."""
        if not self.due_date:
            return "No due date"
        from app.utils import format_date_with_relative

        return f"Due: {format_date_with_relative(self.due_date)}"

    def add_linked_entity(self, entity_type, entity_id):
        """Add a linked entity to this task."""
        add_linked_entity(self.id, entity_type, entity_id)

    def remove_linked_entity(self, entity_type, entity_id):
        """Remove a linked entity from this task."""
        remove_linked_entity(self.id, entity_type, entity_id)

    def set_linked_entities(self, entities):
        """Set the linked entities for this task (replaces all existing links)."""
        set_linked_entities(self.id, entities)

    def to_display_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary with pre-formatted display fields."""
        result = self.to_dict()

        # Add display-friendly versions using comprehension
        display_fields = [
            "status",
            "priority",
            "next_step_type",
            "task_type",
            "dependency_type",
        ]
        for field in display_fields:
            value = getattr(self, field, None)
            result[f"{field}_display"] = (
                value.replace("-", " ").replace("_", " ").title() if value else ""
            )

        return result

    def __repr__(self) -> str:
        """Return string representation of the task."""
        return f"<Task {self.task_type}: {self.description[:50]}>"
