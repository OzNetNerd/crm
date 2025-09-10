from datetime import datetime
from . import db


# Junction table for task-entity relationships
task_entities = db.Table(
    "task_entities",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), nullable=False),
    db.Column("entity_type", db.String(50), nullable=False),
    db.Column("entity_id", db.Integer, nullable=False),
    db.Column("created_at", db.DateTime, default=datetime.utcnow),
)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(
        db.Date,
        info={
            'display_label': 'Due Date',
            'groupable': True,
            'sortable': True,
            'date_groupings': {
                'overdue': {'label': 'Overdue', 'css_class': 'date-overdue'},
                'today': {'label': 'Due Today', 'css_class': 'date-today'},
                'this_week': {'label': 'This Week', 'css_class': 'date-soon'},
                'later': {'label': 'Later', 'css_class': 'date-future'},
                'no_date': {'label': 'No Due Date', 'css_class': 'date-missing'}
            }
        }
    )
    priority = db.Column(
        db.String(10), 
        default="medium",
        info={
            'display_label': 'Priority',
            'choices': {
                'high': {
                    'label': 'High',
                    'css_class': 'priority-urgent',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Urgent priority',
                    'icon': 'exclamation',
                    'order': 1
                },
                'medium': {
                    'label': 'Medium',
                    'css_class': 'priority-normal',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Normal priority',
                    'icon': 'minus',
                    'order': 2
                },
                'low': {
                    'label': 'Low',
                    'css_class': 'priority-low',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Low priority',
                    'icon': 'arrow-down',
                    'order': 3
                }
            }
        }
    )  # high/medium/low
    status = db.Column(
        db.String(20), 
        default="todo",
        info={
            'display_label': 'Status',
            'choices': {
                'todo': {
                    'label': 'To Do',
                    'css_class': 'status-todo',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Not started',
                    'icon': 'circle',
                    'order': 1
                },
                'in-progress': {
                    'label': 'In Progress',
                    'css_class': 'status-progress',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Currently working on',
                    'icon': 'clock',
                    'order': 2
                },
                'complete': {
                    'label': 'Complete',
                    'css_class': 'status-complete',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Finished',
                    'icon': 'check-circle',
                    'order': 3
                }
            }
        }
    )  # todo/in-progress/complete
    next_step_type = db.Column(
        db.String(20),
        info={
            'display_label': 'Next Step Type',
            'choices': {
                'call': {
                    'label': 'Call',
                    'css_class': 'step-call',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Phone call',
                    'icon': 'phone',
                    'order': 1
                },
                'email': {
                    'label': 'Email',
                    'css_class': 'step-email',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Send email',
                    'icon': 'mail',
                    'order': 2
                },
                'meeting': {
                    'label': 'Meeting',
                    'css_class': 'step-meeting',
                    'groupable': True,
                    'sortable': True,
                    'description': 'In-person or video meeting',
                    'icon': 'users',
                    'order': 3
                },
                'demo': {
                    'label': 'Demo',
                    'css_class': 'step-demo',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Product demonstration',
                    'icon': 'presentation-chart-line',
                    'order': 4
                }
            }
        }
    )  # meeting/demo/call/email
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Legacy entity linking removed - now using task_entities junction table

    # Multi Task support
    task_type = db.Column(
        db.String(20), 
        default="single",
        info={
            'display_label': 'Task Type',
            'choices': {
                'single': {
                    'label': 'Single Task',
                    'css_class': 'type-single',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Standalone task',
                    'icon': 'document',
                    'order': 1
                },
                'parent': {
                    'label': 'Parent Task',
                    'css_class': 'type-parent',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Task with subtasks',
                    'icon': 'folder',
                    'order': 2
                },
                'child': {
                    'label': 'Child Task',
                    'css_class': 'type-child',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Subtask of parent',
                    'icon': 'document-duplicate',
                    'order': 3
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
            'choices': {
                'parallel': {
                    'label': 'Parallel',
                    'css_class': 'dep-parallel',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Can run simultaneously',
                    'icon': 'arrows-right-left',
                    'order': 1
                },
                'sequential': {
                    'label': 'Sequential',
                    'css_class': 'dep-sequential',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Must complete in order',
                    'icon': 'arrow-right',
                    'order': 2
                }
            }
        }
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

    @property
    def opportunity_value(self):
        """Get opportunity value from linked opportunities"""
        for entity in self.linked_entities:
            if entity["type"] == "opportunity" and entity["entity"]:
                return entity["entity"].value
        return None

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

    @property
    def opportunity_stage(self):
        """Get opportunity stage from linked opportunities"""
        for entity in self.linked_entities:
            if entity["type"] == "opportunity" and entity["entity"]:
                return entity["entity"].stage
        return None

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

    @classmethod
    def get_priority_choices(cls):
        """Get priority choices from model metadata"""
        from app.utils.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_choices(cls, 'priority')
    
    @classmethod
    def get_status_choices(cls):
        """Get status choices from model metadata"""
        from app.utils.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_choices(cls, 'status')
    
    @classmethod
    def get_priority_css_class(cls, priority_value):
        """Get CSS class for a priority value"""
        from app.utils.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_css_class(cls, 'priority', priority_value)
    
    @classmethod
    def get_status_css_class(cls, status_value):
        """Get CSS class for a status value"""
        from app.utils.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_css_class(cls, 'status', status_value)

    def to_dict(self):
        """Convert task to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "priority_css_class": self.get_priority_css_class(self.priority),
            "status": self.status,
            "status_css_class": self.get_status_css_class(self.status),
            "next_step_type": self.next_step_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "entity_name": self.entity_name,
            "task_type": self.task_type,
            "parent_task_id": self.parent_task_id,
            "sequence_order": self.sequence_order,
            "dependency_type": self.dependency_type,
            "is_overdue": self.is_overdue,
            "opportunity_value": self.opportunity_value,
            "company_name": self.company_name,
            "opportunity_name": self.opportunity_name,
            "opportunity_stage": self.opportunity_stage,
            "stakeholder_opportunity_name": self.stakeholder_opportunity_name,
            "stakeholder_opportunity_value": self.stakeholder_opportunity_value,
            "task_type_badge": self.task_type_badge,
            "can_start": self.can_start,
            "completion_percentage": self.completion_percentage,
            "linked_entities": [
                {"type": entity["type"], "id": entity["id"], "name": entity["name"]}
                for entity in self.linked_entities
            ],
        }

    def __repr__(self):
        return f"<Task {self.task_type}: {self.description[:50]}>"
