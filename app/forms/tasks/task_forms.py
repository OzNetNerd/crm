"""
Task Forms

DRY task form definitions using centralized FieldFactory and BaseForm patterns.
Eliminates duplication by leveraging common field creation methods.
"""

from flask_wtf import FlaskForm
from wtforms import FieldList, FormField
from wtforms.validators import Optional as OptionalValidator
from ..base.base_forms import BaseForm, FieldFactory, FormConstants


class TaskForm(BaseForm):
    """Complete task form with all available fields"""
    
    description = FieldFactory.create_description_field(
        placeholder="What needs to be done?"
    )
    due_date = FieldFactory.create_due_date_field()
    priority = FieldFactory.create_priority_field()
    status = FieldFactory.create_status_field()
    next_step_type = FieldFactory.create_next_step_type_field()
    linked_entities = FieldFactory.create_linked_entities_field()
    task_type = FieldFactory.create_task_type_field()
    parent_task_id = FieldFactory.create_parent_task_field()
    sequence_order = FieldFactory.create_sequence_order_field()
    dependency_type = FieldFactory.create_dependency_type_field()

    def validate(self, extra_validators=None):
        """DRY validation using base class methods"""
        if not super().validate(extra_validators):
            return False

        # Validate linked_entities JSON if provided
        if not self.validate_linked_entities_json(self.linked_entities):
            return False

        # Validate parent-child task relationship
        if not self.validate_parent_task_relationship(self.parent_task_id, self.task_type):
            return False

        return True


class QuickTaskForm(BaseForm):
    """Simplified form for quick task creation - DRY using FieldFactory"""
    
    description = FieldFactory.create_quick_task_field()
    priority = FieldFactory.create_priority_field()


class ChildTaskForm(BaseForm):
    """Form for child tasks in Multi Task creation - DRY field configuration"""
    
    description = FieldFactory.create_description_field(
        placeholder="Child task description...",
        rows=FormConstants.CHILD_TASK_ROWS
    )
    due_date = FieldFactory.create_due_date_field(label="Due Date")
    priority = FieldFactory.create_priority_field()
    next_step_type = FieldFactory.create_next_step_type_field()


class MultiTaskForm(BaseForm):
    """Form for creating parent tasks with multiple child tasks - DRY implementation"""
    
    description = FieldFactory.create_description_field(
        label="Parent Task Description",
        placeholder="What is the overall goal?"
    )
    due_date = FieldFactory.create_due_date_field(label="Overall Due Date")
    priority = FieldFactory.create_priority_field()
    dependency_type = FieldFactory.create_dependency_type_field()
    
    # Entity selection using FieldFactory
    entity_type, entity_id = FieldFactory.create_entity_selection_fields()
    
    child_tasks = FieldList(
        FormField(ChildTaskForm), 
        label="Child Tasks", 
        min_entries=2, 
        max_entries=10
    )

    def validate(self, extra_validators=None):
        """DRY validation using base class methods"""
        if not super().validate(extra_validators):
            return False

        # Validate minimum child tasks using base class method
        if not self.validate_multi_task_children(self.child_tasks, min_children=2):
            return False

        return True