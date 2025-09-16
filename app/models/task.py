from datetime import datetime, date
from typing import Dict, Any, List, Optional
from . import db
from .base import BaseModel


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
    """
    Task model representing work items and activities in the CRM system.

    This model provides comprehensive task management functionality including
    parent-child task hierarchies, entity linking, dependency management,
    and progress tracking. Tasks can be linked to multiple entities (companies,
    opportunities, stakeholders) and support both single tasks and multi-task
    projects with sequential or parallel execution.

    Attributes:
        id: Primary key identifier.
        description: Task description/title (required).
        due_date: Task due date.
        priority: Priority level (high, medium, low).
        status: Current status (todo, in-progress, complete).
        next_step_type: Type of next step (meeting, demo, call, email).
        created_at: Task creation timestamp.
        completed_at: Task completion timestamp.
        task_type: Task hierarchy type (single, parent, child).
        parent_task_id: Parent task foreign key for child tasks.
        sequence_order: Execution order for child tasks.
        dependency_type: Execution dependency (sequential, parallel).
    """
    __tablename__ = "tasks"
    __display_name__ = "Task"
    __display_field__ = 'description'
    __search_config__ = {
        'title_field': 'description',  # Tasks use description as title
        'subtitle_fields': ['due_date', 'priority', 'status']
    }

    # Serialization configuration
    __include_properties__ = [
        "is_overdue", "opportunity_value", "company_name",
        "opportunity_name", "opportunity_stage", "stakeholder_opportunity_name",
        "stakeholder_opportunity_value", "task_type_badge", "can_start",
        "completion_percentage"
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
        info={
            'display_label': 'Description',
            'required': True,
            'form_include': True
        }
    )
    due_date = db.Column(
        db.Date,
        info={
            'display_label': 'Due Date',
            'groupable': True,
            'sortable': True,
            'form_include': True,
            'date_groupings': {
                'overdue': 'Overdue',
                'today': 'Due Today',
                'this_week': 'This Week',
                'later': 'Later',
                'no_date': 'No Due Date'
            }
        }
    )
    priority = db.Column(
        db.String(10),
        default="medium",
        info={
            'display_label': 'Priority',
            'groupable': True,
            'sortable': True,
            'form_include': True,
            'choices': {
                'high': {
                    'label': 'High',
                    'description': 'Urgent priority'
                },
                'medium': {
                    'label': 'Medium',
                    'description': 'Normal priority'
                },
                'low': {
                    'label': 'Low',
                    'description': 'Low priority'
                }
            }
        }
    )  # high/medium/low
    status = db.Column(
        db.String(20),
        default="todo",
        info={
            'display_label': 'Status',
            'groupable': True,
            'sortable': True,
            'choices': {
                'todo': {
                    'label': 'To Do',
                    'description': 'Not started'
                },
                'in-progress': {
                    'label': 'In Progress',
                    'description': 'Currently working on'
                },
                'complete': {
                    'label': 'Complete',
                    'description': 'Finished'
                }
            }
        }
    )  # todo/in-progress/complete
    next_step_type = db.Column(
        db.String(20),
        info={
            'display_label': 'Next Step Type',
            'groupable': True,
            'sortable': True,
            'choices': {
                'call': {
                    'label': 'Call',
                    'description': 'Phone call'
                },
                'email': {
                    'label': 'Email',
                    'description': 'Send email'
                },
                'meeting': {
                    'label': 'Meeting',
                    'description': 'In-person or video meeting'
                },
                'demo': {
                    'label': 'Demo',
                    'description': 'Product demonstration'
                }
            }
        }
    )  # meeting/demo/call/email
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)


    # Multi Task support
    task_type = db.Column(
        db.String(20),
        default="single",
        info={
            'display_label': 'Task Type',
            'groupable': True,
            'sortable': True,
            'choices': {
                'single': {
                    'label': 'Single Task',
                    'description': 'Standalone task'
                },
                'parent': {
                    'label': 'Parent Task',
                    'description': 'Task with subtasks'
                },
                'child': {
                    'label': 'Child Task',
                    'description': 'Subtask of parent'
                }
            }
        }
    )  # 'single', 'parent', 'child'
    parent_task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    sequence_order = db.Column(db.Integer, default=0)  # For ordering child tasks
    dependency_type = db.Column(
        db.String(20),
        default="parallel",
        info={
            'display_label': 'Dependency Type',
            'groupable': True,
            'sortable': True,
            'choices': {
                'parallel': {
                    'label': 'Parallel',
                    'description': 'Can run simultaneously'
                },
                'sequential': {
                    'label': 'Sequential',
                    'description': 'Must complete in order'
                }
            }
        }
    )  # 'sequential', 'parallel'

    comments = db.Column(
        db.Text,
        info={
            'display_label': 'Comments',
            'form_include': True,
            'rows': 3
        }
    )

    @property
    def is_overdue(self) -> bool:
        """
        Check if the task is overdue.

        A task is considered overdue if it has a due date that has passed
        and the task is not yet complete.

        Returns:
            True if task is overdue, False otherwise.
            Returns False if no due date is set or task is complete.

        Example:
            >>> task = Task(due_date=date(2023, 1, 1), status="todo")
            >>> # Assuming current date is after 2023-01-01
            >>> task.is_overdue
            True
        """
        if not self.due_date or self.status == "complete":
            return False
        return self.due_date < datetime.utcnow().date()

    @property
    def due_date_display(self) -> str:
        """Format due date for display with relative time information."""
        if not self.due_date:
            return "No due date"

        from datetime import date
        today = date.today()
        days_diff = (self.due_date - today).days
        formatted_date = self.due_date.strftime('%d/%m/%y')

        if days_diff < 0:
            days_ago = abs(days_diff)
            return f"Due: {formatted_date} ({days_ago} day{'s' if days_ago != 1 else ''} ago)"
        elif days_diff == 0:
            return f"Due: {formatted_date} (Today)"
        else:
            return f"Due: {formatted_date} ({days_diff} day{'s' if days_diff != 1 else ''} left)"



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

    def _get_entity_attr(self, entity_type, attr_name):
        """Get attribute from first matching linked entity"""
        for entity in self.linked_entities:
            if entity["type"] == entity_type and entity.get("entity"):
                return getattr(entity["entity"], attr_name, None)
        return None

    opportunity_value = property(lambda self: self._get_entity_attr("opportunity", "value"))

    @property
    def company_name(self):
        """Get company name from any linked entity"""
        for entity in self.linked_entities:
            if entity["type"] == "company":
                return entity["name"]
            elif entity["type"] == "contact" and entity["entity"]:
                return (
                    entity["entity"].company.name if entity["entity"].company else None
                )
            elif entity["type"] == "opportunity" and entity["entity"]:
                return (
                    entity["entity"].company.name if entity["entity"].company else None
                )
        return None

    @property
    def opportunity_name(self):
        """Get opportunity name from linked opportunities"""
        for entity in self.linked_entities:
            if entity["type"] == "opportunity":
                return entity["name"]
        return None

    opportunity_stage = property(lambda self: self._get_entity_attr("opportunity", "stage"))

    @property
    def stakeholder_opportunity_name(self):
        """Get primary opportunity name for contact tasks"""
        # First check for direct opportunity links
        opp_name = self.opportunity_name
        if opp_name:
            return opp_name

        # Then check for contact with opportunities
        for entity in self.linked_entities:
            if entity["type"] == "contact" and entity["entity"]:
                contact = entity["entity"]
                if contact.opportunities:
                    return contact.opportunities[0].name
        return None

    @property
    def stakeholder_opportunity_value(self):
        """Get primary opportunity value for contact tasks"""
        # First check for direct opportunity links
        opp_value = self.opportunity_value
        if opp_value:
            return opp_value

        # Then check for contact with opportunities
        for entity in self.linked_entities:
            if entity["type"] == "contact" and entity["entity"]:
                contact = entity["entity"]
                if contact.opportunities:
                    return contact.opportunities[0].value
        return None

    @property
    def task_type_badge(self):
        """Get appropriate badge text for task type"""
        if self.task_type == "parent":
            return "Parent"
        elif self.task_type == "child":
            return "Child"
        return "Single"

    @property
    def can_start(self):
        """Check if task can be started based on dependencies"""
        if self.task_type != "child" or self.dependency_type != "sequential":
            return True

        # For sequential child tasks, check if previous tasks are complete
        if not self.parent_task:
            return True

        # Get all child tasks with lower sequence_order
        previous_tasks = Task.query.filter(
            Task.parent_task_id == self.parent_task_id,
            Task.sequence_order < self.sequence_order,
        ).all()

        # All previous tasks must be complete
        return all(task.status == "complete" for task in previous_tasks)

    @property
    def completion_percentage(self):
        """For parent tasks, calculate completion percentage based on child tasks"""
        if self.task_type != "parent":
            return 100 if self.status == "complete" else 0

        # Force fresh query to avoid stale relationship data
        child_tasks = Task.query.filter(Task.parent_task_id == self.id).all()

        if not child_tasks:
            return 0

        completed_count = sum(1 for child in child_tasks if child.status == "complete")
        return int((completed_count / len(child_tasks)) * 100)

    @property
    def next_available_child(self):
        """For parent tasks, get the next child that can be started"""
        if self.task_type != "parent":
            return None

        for child in self.child_tasks:
            if child.status != "complete" and child.can_start:
                return child
        return None

    @property
    def linked_entities(self):
        """Get all entities linked to this task"""
        # Return empty list if task has no ID yet
        if not self.id:
            return []

        # Query the junction table for this task's linked entities using ORM
        linked = (
            db.session.query(task_entities.c.entity_type, task_entities.c.entity_id)
            .filter(task_entities.c.task_id == self.id)
            .all()
        )

        entities = []
        for entity_type, entity_id in linked:
            # Get the actual entity object
            entity = self._get_entity_by_type_and_id(entity_type, entity_id)
            if entity:
                entities.append(
                    {
                        "type": entity_type,
                        "id": entity_id,
                        "name": entity.name,
                        "entity": entity,
                    }
                )

        return entities

    def _get_entity_by_type_and_id(self, entity_type, entity_id):
        """Helper method to get entity by type and id"""
        if entity_type == "company":
            from .company import Company

            return Company.query.get(entity_id)
        elif entity_type == "stakeholder":
            from .stakeholder import Stakeholder

            return Stakeholder.query.get(entity_id)
        elif entity_type == "opportunity":
            from .opportunity import Opportunity

            return Opportunity.query.get(entity_id)
        return None

    def add_linked_entity(self, entity_type, entity_id):
        """Add a linked entity to this task"""
        # Check if already linked using ORM
        existing = (
            db.session.query(task_entities)
            .filter(task_entities.c.task_id == self.id)
            .filter(task_entities.c.entity_type == entity_type)
            .filter(task_entities.c.entity_id == entity_id)
            .first()
        )

        if not existing:
            # Insert new entity link using ORM
            insert_stmt = task_entities.insert().values(
                task_id=self.id,
                entity_type=entity_type,
                entity_id=entity_id,
                created_at=datetime.utcnow()
            )
            db.session.execute(insert_stmt)
            db.session.commit()

    def remove_linked_entity(self, entity_type, entity_id):
        """Remove a linked entity from this task"""
        delete_stmt = task_entities.delete().where(
            (task_entities.c.task_id == self.id) &
            (task_entities.c.entity_type == entity_type) &
            (task_entities.c.entity_id == entity_id)
        )
        db.session.execute(delete_stmt)
        db.session.commit()

    def set_linked_entities(self, entities):
        """Set the linked entities for this task (replaces all existing links)"""
        # Clear existing links
        delete_stmt = task_entities.delete().where(task_entities.c.task_id == self.id)
        db.session.execute(delete_stmt)

        # Add new links
        for entity in entities:
            insert_stmt = task_entities.insert().values(
                task_id=self.id,
                entity_type=entity["type"],
                entity_id=entity["id"],
                created_at=datetime.utcnow()
            )
            db.session.execute(insert_stmt)
        db.session.commit()


    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        return super().to_dict()

    def to_display_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary with pre-formatted display fields.

        Extends the basic dictionary representation with formatted
        fields optimized for display in user interfaces. This includes
        formatted currency values for linked opportunities and other
        UI-specific formatting.

        Returns:
            Dictionary with all standard fields plus display-formatted versions
            of fields that benefit from special formatting:
            - status_display: Human-readable status (e.g., "In Progress" instead of "in-progress")
            - priority_display: Human-readable priority
            - next_step_type_display: Human-readable next step type
            - task_type_display: Human-readable task type
            - dependency_type_display: Human-readable dependency type

        Example:
            >>> task = Task(description="Big deal follow-up", status="in-progress")
            >>> display_data = task.to_display_dict()
            >>> print(display_data.get('opportunity_value_formatted'))
            '$50,000'
            >>> print(display_data['status_display'])
            'In Progress'
        """
        # Get base dictionary
        result = self.to_dict()

        # Add display-friendly versions of choice fields
        result['status_display'] = self.status.replace('-', ' ').replace('_', ' ').title() if self.status else ''
        result['priority_display'] = self.priority.replace('-', ' ').replace('_', ' ').title() if self.priority else ''
        result['next_step_type_display'] = self.next_step_type.replace('-', ' ').replace('_', ' ').title() if self.next_step_type else ''
        result['task_type_display'] = self.task_type.replace('-', ' ').replace('_', ' ').title() if self.task_type else ''
        result['dependency_type_display'] = self.dependency_type.replace('-', ' ').replace('_', ' ').title() if self.dependency_type else ''

        return result

    def __repr__(self) -> str:
        """Return string representation of the task."""
        return f"<Task {self.task_type}: {self.description[:50]}>"
