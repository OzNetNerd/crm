import json
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from app.utils.forms.form_builder import DynamicFormBuilder


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


class FieldFactory:
    """Factory methods for common field patterns"""
    
    @staticmethod
    def create_description_field(label="Description", max_length=500, rows=3, placeholder="Enter description..."):
        """Create a standardized description TextAreaField"""
        return TextAreaField(
            label,
            validators=[DataRequired(), Length(min=1, max=max_length)],
            render_kw={"placeholder": placeholder, "rows": rows},
        )
    
    @staticmethod
    def create_linked_entities_field():
        """Create a standardized linked_entities StringField"""
        return StringField(
            "Linked Entities",
            validators=[Optional()],
            render_kw={
                "data-entity-selector": "true",
                "placeholder": "Select companies, contacts, or opportunities",
            },
        )
    
    @staticmethod
    def create_priority_field(model_class):
        """Create a standardized priority SelectField using DynamicFormBuilder"""
        return DynamicFormBuilder.build_select_field(model_class, 'priority')
    
    @staticmethod
    def create_due_date_field(model_class=None, label="Due Date"):
        """Create a standardized due date field"""
        if model_class:
            return DynamicFormBuilder.build_date_field(model_class, 'due_date')
        else:
            return DateField(label, validators=[Optional()], default=None)


class FormConstants:
    """Common constants used across forms"""
    
    ENTITY_SELECTOR_PLACEHOLDER = "Select companies, contacts, or opportunities"
    
    # Common field configurations
    DESCRIPTION_MAX_LENGTH = 500
    QUICK_TASK_MAX_LENGTH = 200
    NOTE_MAX_LENGTH = 2000
    
    # Default row counts for text areas
    DESCRIPTION_ROWS = 3
    CHILD_TASK_ROWS = 2
    NOTE_ROWS = 4