"""
Base Form Classes and Utilities

Provides common base classes, field factories, and constants for all forms.
Eliminates duplication by centralizing common patterns.
"""

import json
from typing import Any, Optional
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional as OptionalValidator, NumberRange


class BaseForm(FlaskForm):
    """Base form class with common validation methods and utilities"""
    
    def validate_linked_entities_json(self, field):
        """Validate linked_entities JSON field format"""
        if field.data:
            try:
                entities = json.loads(field.data)
                if not isinstance(entities, list):
                    raise ValueError("Linked entities must be a list")
                
                for entity in entities:
                    if (
                        not isinstance(entity, dict)
                        or "type" not in entity
                        or "id" not in entity
                    ):
                        raise ValueError("Each linked entity must have 'type' and 'id' fields")
                        
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for linked entities")
            except ValueError as e:
                field.errors.append(str(e))
                return False
        return True

    def validate_parent_task_relationship(self, parent_task_id_field, task_type_field):
        """DRY validation for parent-child task relationships"""
        if task_type_field.data == "child" and not parent_task_id_field.data:
            parent_task_id_field.errors.append("Parent task is required for child tasks")
            return False
        return True

    def validate_multi_task_children(self, child_tasks_field, min_children=2):
        """DRY validation for multi-task child requirements"""
        if len(child_tasks_field.data) < min_children:
            child_tasks_field.errors.append(
                f"Multi Tasks must have at least {min_children} child tasks"
            )
            return False
        return True


class FieldFactory:
    """Factory methods for common field patterns - DRY field creation"""
    
    @staticmethod
    def create_description_field(
        label: str = "Description", 
        max_length: int = None,
        rows: int = None,
        placeholder: str = None,
        required: bool = True
    ) -> TextAreaField:
        """Create a standardized description TextAreaField"""
        max_length = max_length or FormConstants.DESCRIPTION_MAX_LENGTH
        rows = rows or FormConstants.DESCRIPTION_ROWS
        placeholder = placeholder or "Enter description..."
        
        validators = [DataRequired() if required else OptionalValidator()]
        if max_length:
            validators.append(Length(min=1 if required else 0, max=max_length))
        
        return TextAreaField(
            label,
            validators=validators,
            render_kw={"placeholder": placeholder, "rows": rows},
        )
    
    @staticmethod
    def create_quick_task_field(
        label: str = "Task",
        placeholder: str = "Add a quick task..."
    ) -> StringField:
        """Create a standardized quick task field - DRY for QuickTaskForm"""
        return StringField(
            label,
            validators=[DataRequired(), Length(min=1, max=FormConstants.QUICK_TASK_MAX_LENGTH)],
            render_kw={"placeholder": placeholder, "class": "form-control"},
        )
    
    @staticmethod
    def create_note_content_field(
        label: str = "Note Content",
        placeholder: str = "Enter your note...",
        rows: int = None
    ) -> TextAreaField:
        """Create a standardized note content field - DRY for NoteForm"""
        rows = rows or FormConstants.NOTE_ROWS
        return TextAreaField(
            label,
            validators=[DataRequired(), Length(min=1, max=FormConstants.NOTE_MAX_LENGTH)],
            render_kw={"placeholder": placeholder, "rows": rows}
        )
    
    @staticmethod
    def create_linked_entities_field(placeholder: str = None) -> StringField:
        """Create a standardized linked_entities StringField"""
        placeholder = placeholder or FormConstants.ENTITY_SELECTOR_PLACEHOLDER
        return StringField(
            "Linked Entities",
            validators=[OptionalValidator()],
            render_kw={
                "data-entity-selector": "true",
                "placeholder": placeholder,
            },
        )
    
    @staticmethod
    def create_entity_selection_fields():
        """Create standardized entity type/id selection fields - DRY for MultiTaskForm"""
        entity_type = SelectField(
            "Related To",
            choices=FormConstants.ENTITY_TYPE_CHOICES,
            validators=[OptionalValidator()]
        )
        
        entity_id = IntegerField(
            "Select Entity",
            validators=[OptionalValidator()]
        )
        
        return entity_type, entity_id
    
    @staticmethod
    def create_sequence_order_field(default: int = 0) -> IntegerField:
        """Create a standardized sequence order field"""
        return IntegerField(
            "Sequence Order",
            validators=[OptionalValidator(), NumberRange(min=0)],
            default=default
        )

    @staticmethod
    def create_parent_task_field() -> IntegerField:
        """Create a standardized parent task field"""
        return IntegerField(
            "Parent Task",
            validators=[OptionalValidator(), NumberRange(min=1)]
        )

    # Dynamic field creation methods using ModelIntrospector
    @staticmethod
    def create_priority_field(model_class = None, **kwargs) -> SelectField:
        """Create a standardized priority SelectField"""
        from app.utils.core.model_introspection import ModelIntrospector

        if model_class is None:
            # Use Task model as default
            from app.models.task import Task
            model_class = Task

        choices = ModelIntrospector.get_field_choices(model_class, 'priority')
        label = kwargs.pop('label', 'Priority')

        return SelectField(
            label,
            choices=[('', f'Select {label.lower()}')] + choices,
            validators=[OptionalValidator()],
            **kwargs
        )

    @staticmethod
    def create_status_field(model_class = None, **kwargs) -> SelectField:
        """Create a standardized status SelectField"""
        from app.utils.core.model_introspection import ModelIntrospector

        if model_class is None:
            # Use Task model as default
            from app.models.task import Task
            model_class = Task

        choices = ModelIntrospector.get_field_choices(model_class, 'status')
        label = kwargs.pop('label', 'Status')

        return SelectField(
            label,
            choices=[('', f'Select {label.lower()}')] + choices,
            validators=[OptionalValidator()],
            **kwargs
        )

    @staticmethod
    def create_due_date_field(label: str = "Due Date", **kwargs) -> DateField:
        """Create a standardized due date field"""
        return DateField(label, validators=[OptionalValidator()], default=None, **kwargs)

    @staticmethod
    def create_next_step_type_field(**kwargs) -> SelectField:
        """Create a standardized next step type SelectField"""
        from app.utils.core.model_introspection import ModelIntrospector
        from app.models.task import Task

        choices = ModelIntrospector.get_field_choices(Task, 'next_step_type')
        label = kwargs.pop('label', 'Next Step Type')

        return SelectField(
            label,
            choices=[('', f'Select {label.lower()}')] + choices,
            validators=[OptionalValidator()],
            **kwargs
        )

    @staticmethod
    def create_task_type_field(**kwargs) -> SelectField:
        """Create a standardized task type SelectField"""
        from app.utils.core.model_introspection import ModelIntrospector
        from app.models.task import Task

        choices = ModelIntrospector.get_field_choices(Task, 'task_type')
        label = kwargs.pop('label', 'Task Type')

        return SelectField(
            label,
            choices=[('', f'Select {label.lower()}')] + choices,
            validators=[OptionalValidator()],
            **kwargs
        )

    @staticmethod
    def create_dependency_type_field(**kwargs) -> SelectField:
        """Create a standardized dependency type SelectField"""
        from app.utils.core.model_introspection import ModelIntrospector
        from app.models.task import Task

        choices = ModelIntrospector.get_field_choices(Task, 'dependency_type')
        label = kwargs.pop('label', 'Dependency Type')

        return SelectField(
            label,
            choices=[('', f'Select {label.lower()}')] + choices,
            validators=[OptionalValidator()],
            **kwargs
        )


class FormConstants:
    """Common constants used across forms - single source of truth"""
    
    # Entity selector configuration
    ENTITY_SELECTOR_PLACEHOLDER = "Select companies, contacts, or opportunities"
    
    # Field length limits
    DESCRIPTION_MAX_LENGTH = 500
    QUICK_TASK_MAX_LENGTH = 200
    NOTE_MAX_LENGTH = 2000
    
    # Default row counts for text areas
    DESCRIPTION_ROWS = 3
    CHILD_TASK_ROWS = 2
    NOTE_ROWS = 4
    
    # Entity type choices for forms
    ENTITY_TYPE_CHOICES = [
        ("", "None"),
        ("company", "Company"),
        ("stakeholder", "Stakeholder"), 
        ("opportunity", "Opportunity")
    ]
    
    # Note type choices
    NOTE_TYPE_CHOICES = [
        ("1", "Internal Note"),
        ("0", "Client-Facing Note")
    ]
    
    # Common validation messages
    VALIDATION_MESSAGES = {
        'required': 'This field is required.',
        'parent_task_required': 'Parent task is required for child tasks.',
        'min_children': 'Multi Tasks must have at least {min} child tasks.',
        'invalid_json': 'Invalid JSON format for linked entities.',
        'invalid_entity': "Each linked entity must have 'type' and 'id' fields."
    }