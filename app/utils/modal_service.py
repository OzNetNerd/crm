"""
Modal Service for HTMX-based form handling.

This service provides a clean interface for handling modal forms using HTMX,
leveraging WTForms with DynamicFormBuilder for form generation and validation.
"""

from typing import Dict, Any, Optional
from flask import render_template, jsonify, request
from app.models import db
from app.utils.model_introspection import ModelIntrospector, get_model_by_name
from app.utils.dynamic_form_builder import DynamicFormBuilder
from app.forms.base_forms import BaseForm
from app.utils.entity_icons import get_entity_icon_html


class ModalService:
    """
    Service for handling modal forms using HTMX and the existing model system.
    """
    
    @staticmethod
    def render_create_modal(model_name: str, **kwargs) -> str:
        """
        Render a create modal for the specified model using WTForms.
        
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
        
        # Generate dynamic WTForms form class
        form_class = DynamicFormBuilder.build_dynamic_form(model_class, BaseForm)
        form = form_class()
        
        template_vars = {
            'model_name': model_name,
            'model_class': model_class,
            'form': form,
            'action_url': f'/modals/{model_name}/create',
            'modal_title': f'Create {model_name}',
            'is_edit': False,
            'get_entity_icon_html': get_entity_icon_html,
            **kwargs
        }
        
        return render_template('components/modals/wtforms_modal.html', **template_vars)
    
    @staticmethod
    def render_edit_modal(model_name: str, entity_id: int, **kwargs) -> str:
        """
        Render an edit modal for the specified model and entity using WTForms.
        
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
        
        # Generate dynamic WTForms form class and populate with entity data
        form_class = DynamicFormBuilder.build_dynamic_form(model_class, BaseForm)
        form = form_class(obj=entity)
        
        template_vars = {
            'model_name': model_name,
            'model_class': model_class,
            'entity': entity,
            'form': form,
            'action_url': f'/modals/{model_name}/{entity_id}/update',
            'modal_title': f'Edit {model_name}',
            'is_edit': True,
            'get_entity_icon_html': get_entity_icon_html,
            **kwargs
        }
        
        return render_template('components/modals/wtforms_modal.html', **template_vars)
    
    @staticmethod
    def process_form_submission(model_name: str, entity_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process form submission for create or update operations using WTForms validation.
        
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
            print(f"DEBUG: Processing form for model {model_name}, entity_id: {entity_id}")
            print(f"DEBUG: Form data: {request.form}")
            
            # Get existing entity for updates
            if entity_id:
                entity = model_class.query.get_or_404(entity_id)
                operation = 'updated'
            else:
                entity = None
                operation = 'created'
            
            # Generate dynamic WTForms form class and populate with request data
            form_class = DynamicFormBuilder.build_dynamic_form(model_class, BaseForm)
            form = form_class(obj=entity)
            
            print(f"DEBUG: Form class: {form_class}")
            print(f"DEBUG: Form fields: {[field.name for field in form]}")
            print(f"DEBUG: Form validation result: {form.validate_on_submit()}")
            if form.errors:
                print(f"DEBUG: Form errors: {form.errors}")
            
            # Validate form using WTForms
            if form.validate_on_submit():
                # Create or update entity
                if not entity:
                    entity = model_class()
                
                # Populate entity with form data using WTForms
                form.populate_obj(entity)
                
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
            else:
                # Form validation failed - re-render form with errors
                action_url = f'/modals/{model_name}/create' if not entity_id else f'/modals/{model_name}/{entity_id}/update'
                modal_title = f'Create {model_name}' if not entity_id else f'Edit {model_name}'
                
                template_vars = {
                    'model_name': model_name,
                    'model_class': model_class,
                    'form': form,
                    'action_url': action_url,
                    'modal_title': modal_title,
                    'is_edit': bool(entity_id),
                    'get_entity_icon_html': get_entity_icon_html,
                }
                
                if entity_id:
                    template_vars['entity'] = entity
                
                return {
                    'success': False,
                    'errors': form.errors,
                    'html': render_template('components/modals/wtforms_modal.html', **template_vars)
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