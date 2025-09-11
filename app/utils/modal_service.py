"""
Modal Service for HTMX-based form handling.

This service provides a clean interface for handling modal forms using HTMX,
leveraging the existing ModelIntrospector system for form generation.
"""

from typing import Dict, Any, Optional
from flask import render_template, jsonify, request
from app.models import db
from app.utils.model_introspection import ModelIntrospector, get_model_by_name


class ModalService:
    """
    Service for handling modal forms using HTMX and the existing model system.
    """
    
    @staticmethod
    def render_create_modal(model_name: str, **kwargs) -> str:
        """
        Render a create modal for the specified model.
        
        Args:
            model_name: Name of the model (e.g., 'Task', 'Company')
            **kwargs: Additional template variables
            
        Returns:
            Rendered HTML for the modal
        """
        model_class = get_model_by_name(model_name)
        if not model_class:
            return render_template('components/modals/error_modal.html', 
                                 error=f"Unknown model: {model_name}")
        
        # Get form fields from model introspection
        fields = ModelIntrospector.get_form_fields(model_class)
        
        template_vars = {
            'model_name': model_name,
            'model_class': model_class,
            'fields': fields,
            'action_url': f'/modals/{model_name}/create',
            'modal_title': f'Create {model_name}',
            **kwargs
        }
        
        return render_template('components/modals/generic_create_modal.html', **template_vars)
    
    @staticmethod
    def render_edit_modal(model_name: str, entity_id: int, **kwargs) -> str:
        """
        Render an edit modal for the specified model and entity.
        
        Args:
            model_name: Name of the model (e.g., 'Task', 'Company')
            entity_id: ID of the entity to edit
            **kwargs: Additional template variables
            
        Returns:
            Rendered HTML for the modal
        """
        model_class = get_model_by_name(model_name)
        if not model_class:
            return render_template('components/modals/error_modal.html', 
                                 error=f"Unknown model: {model_name}")
        
        # Get the entity
        entity = model_class.query.get_or_404(entity_id)
        
        # Get form fields from model introspection
        fields = ModelIntrospector.get_form_fields(model_class)
        
        # Pre-populate field values from entity
        for field in fields:
            field['value'] = getattr(entity, field['name'], field.get('default'))
        
        template_vars = {
            'model_name': model_name,
            'model_class': model_class,
            'entity': entity,
            'fields': fields,
            'action_url': f'/modals/{model_name}/{entity_id}/update',
            'modal_title': f'Edit {model_name}',
            **kwargs
        }
        
        return render_template('components/modals/generic_edit_modal.html', **template_vars)
    
    @staticmethod
    def process_form_submission(model_name: str, entity_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process form submission for create or update operations.
        
        Args:
            model_name: Name of the model
            entity_id: ID for update operations (None for create)
            
        Returns:
            Dict with success status and response data
        """
        model_class = get_model_by_name(model_name)
        if not model_class:
            return {
                'success': False,
                'error': f"Unknown model: {model_name}",
                'html': render_template('components/modals/form_error.html', 
                                      error=f"Unknown model: {model_name}")
            }
        
        try:
            # Get form fields to validate against
            fields = ModelIntrospector.get_form_fields(model_class)
            field_names = {field['name'] for field in fields}
            
            if entity_id:
                # Update existing entity
                entity = model_class.query.get_or_404(entity_id)
                operation = 'updated'
            else:
                # Create new entity
                entity = model_class()
                operation = 'created'
            
            # Process form data
            form_data = request.form.to_dict()
            validation_errors = []
            
            for field in fields:
                field_name = field['name']
                if field_name in form_data:
                    value = form_data[field_name]
                    
                    # Basic validation
                    if field.get('required') and not value:
                        validation_errors.append(f"{field['label']} is required")
                        continue
                    
                    # Type conversion
                    if field['type'] == 'number' and value:
                        try:
                            value = int(value)
                        except ValueError:
                            validation_errors.append(f"{field['label']} must be a number")
                            continue
                    elif field['type'] == 'date' and value:
                        # Flask-SQLAlchemy handles date conversion automatically
                        pass
                    
                    # Set the value
                    setattr(entity, field_name, value or None)
            
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors,
                    'html': render_template('components/modals/form_error.html', 
                                          errors=validation_errors)
                }
            
            # Save to database
            if not entity_id:
                db.session.add(entity)
            db.session.commit()
            
            return {
                'success': True,
                'message': f"{model_name} {operation} successfully",
                'entity_id': entity.id,
                'html': render_template('components/modals/form_success.html', 
                                      message=f"{model_name} {operation} successfully",
                                      entity=entity)
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'html': render_template('components/modals/form_error.html', 
                                      error=f"Error {operation}: {str(e)}")
            }
    
    @staticmethod
    def render_modal_close() -> str:
        """
        Render modal close response for HTMX.
        
        Returns:
            HTML that triggers modal close
        """
        return render_template('components/modals/modal_close.html')
    
    @staticmethod
    def get_field_choices_json(model_name: str, field_name: str) -> Dict[str, Any]:
        """
        Get field choices as JSON for dynamic form updates.
        
        Args:
            model_name: Name of the model
            field_name: Name of the field
            
        Returns:
            JSON response with choices
        """
        model_class = get_model_by_name(model_name)
        if not model_class:
            return {'error': f"Unknown model: {model_name}"}
        
        choices = ModelIntrospector.get_field_choices(model_class, field_name)
        return {'choices': choices}