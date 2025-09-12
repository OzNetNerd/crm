from datetime import datetime
from . import db
from app.utils.core.model_helpers import (
    create_choice_field_info,
    create_date_field_info,
    create_model_choice_methods,
    PRIORITY_CHOICES,
    STATUS_CHOICES,
    NEXT_STEP_TYPE_CHOICES,
    TASK_TYPE_CHOICES,
    DEPENDENCY_TYPE_CHOICES,
    DUE_DATE_GROUPINGS
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


@create_model_choice_methods(['priority', 'status'])
class Task(db.Model):
    __tablename__ = "tasks"
    
    __entity_config__ = {
        'display_name': 'Tasks',
        'display_name_singular': 'Task',
        'description': 'Manage your tasks and projects',
        'endpoint_name': 'tasks',
        'modal_path': '/modals/Task',
        'show_dashboard_button': True
    }

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(
        db.Date,
        info=create_date_field_info('Due Date', date_groupings=DUE_DATE_GROUPINGS)
    )
    priority = db.Column(
        db.String(10), 
        default="medium",
        info=create_choice_field_info('Priority', PRIORITY_CHOICES)
    )  # high/medium/low
    status = db.Column(
        db.String(20), 
        default="todo",
        info=create_choice_field_info('Status', STATUS_CHOICES)
    )  # todo/in-progress/complete
    next_step_type = db.Column(
        db.String(20),
        info=create_choice_field_info('Next Step Type', NEXT_STEP_TYPE_CHOICES)
    )  # meeting/demo/call/email
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)


    # Multi Task support
    task_type = db.Column(
        db.String(20), 
        default="single",
        info=create_choice_field_info('Task Type', TASK_TYPE_CHOICES)
    )  # 'single', 'parent', 'child'
    parent_task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    sequence_order = db.Column(db.Integer, default=0)  # For ordering child tasks
    dependency_type = db.Column(
        db.String(20), 
        default="parallel",
        info=create_choice_field_info('Dependency Type', DEPENDENCY_TYPE_CHOICES)
    )  # 'sequential', 'parallel'

    @property
    def is_overdue(self):
        if not self.due_date or self.status == "complete":
            return False
        return self.due_date < datetime.utcnow().date()

    @property
    def entity_name(self):
        """Get primary entity name for backward compatibility"""
        entities = self.linked_entities
        return entities[0]["name"] if entities else None

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


    def to_dict(self):
        """Convert task to dictionary for JSON serialization"""
        from app.utils.model_helpers import auto_serialize
        
        # Define properties to include beyond database columns
        include_properties = [
            "is_overdue", "entity_name", "opportunity_value", "company_name", 
            "opportunity_name", "opportunity_stage", "stakeholder_opportunity_name", 
            "stakeholder_opportunity_value", "task_type_badge", "can_start", 
            "completion_percentage"
        ]
        
        # Define custom transforms for specific fields
        field_transforms = {
            "priority": lambda val: val,  # Keep as-is but add CSS class separately
            "status": lambda val: val,    # Keep as-is but add CSS class separately
            "linked_entities": lambda _: [
                {"type": entity["type"], "id": entity["id"], "name": entity["name"]}
                for entity in self.linked_entities
            ]
        }
        
        result = auto_serialize(self, include_properties, field_transforms)
        
        # Add CSS classes for status and priority
        result["priority_css_class"] = self.get_priority_css_class(self.priority)
        result["status_css_class"] = self.get_status_css_class(self.status)
        
        return result

    def to_display_dict(self):
        """Convert task to dictionary with pre-formatted display fields"""
        from app.utils.ui.formatters import create_display_dict
        
        # Get base dictionary
        result = self.to_dict()
        
        # Add formatted display fields at source
        display_fields = create_display_dict(self)
        result.update(display_fields)
        
        # Add task-specific formatted fields
        if self.opportunity_value:
            from app.utils.ui.formatters import DisplayFormatter
            result['opportunity_value_formatted'] = DisplayFormatter.format_currency(self.opportunity_value)
        
        return result

    def __repr__(self):
        return f"<Task {self.task_type}: {self.description[:50]}>"
