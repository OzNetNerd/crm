"""
Modal Service for HTMX-based form handling.

This service provides a clean interface for handling modal forms using HTMX,
leveraging WTForms with specific form classes for generation and validation.
"""

from typing import Dict, Any, Optional
import logging
from flask import render_template, jsonify, request
from app.models import db
from app.utils.core.model_introspection import ModelIntrospector, get_model_by_name
from app.forms.modals.company import CompanyModalForm
from app.forms.modals.task import TaskModalForm
from app.forms.base.base_forms import BaseForm
# No icon functions needed - templates handle CSS class generation



class ModalService:
    """
    Service for handling modal forms using HTMX and explicit form classes.
    """

    @staticmethod
    def _get_form_class(model_name: str):
        """
        Get the appropriate form class for a model.

        Args:
            model_name: Name of the model (e.g., 'Company', 'Task')

        Returns:
            Form class or None if not supported
        """
        form_classes = {
            'Company': CompanyModalForm,
            'Task': TaskModalForm,
        }
        return form_classes.get(model_name)

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

        # Get explicit form class
        form_class = ModalService._get_form_class(model_name)
        if not form_class:
            return render_template('components/modals/error_modal.html',
                                 error=f"No modal form available for {model_name}")

        form = form_class()
        
        template_vars = {
            'model_name': model_name,
            'model_class': model_class,
            'form': form,
            'action_url': f'/modals/{model_name}/create',
            'modal_title': f'Create {model_name}',
            'is_edit': False,
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

        # Get explicit form class and populate with entity data
        form_class = ModalService._get_form_class(model_name)
        if not form_class:
            return render_template('components/modals/error_modal.html',
                                 error=f"No modal form available for {model_name}")

        form = form_class(obj=entity)
        
        template_vars = {
            'model_name': model_name,
            'model_class': model_class,
            'entity': entity,
            'form': form,
            'action_url': f'/modals/{model_name}/{entity_id}/update',
            'modal_title': f'Edit {model_name}',
            'is_edit': True,
            **kwargs
        }
        
        return render_template('components/modals/wtforms_modal.html', **template_vars)
    
    @staticmethod
    def render_view_modal(model_name: str, entity_id: int, **kwargs) -> str:
        """
        Render a read-only view modal for the specified model and entity.
        
        Args:
            model_name: Name of the model (e.g., 'Task', 'Company')  
            entity_id: ID of the entity to view
            **kwargs: Additional template variables
            
        Returns:
            Rendered HTML for the read-only modal
        """
        model_class = get_model_by_name(model_name)
        if not model_class:
            return render_template('components/modals/error_modal.html', 
                                 error=f"Unknown model: {model_name}")
        
        # Get the entity
        entity = model_class.query.get_or_404(entity_id)
        
        # Use model metadata for configuration
        from app.utils.model_registry import ModelRegistry

        # Get metadata for this entity type
        entity_type = model_name.lower()
        try:
            metadata = ModelRegistry.get_model_metadata(entity_type)
        except ValueError:
            return render_template('components/modals/error_modal.html',
                                 error=f"No metadata found for {model_name}")

        # Render the view modal template
        template_vars = {
            'model_name': entity_type,
            'entity': entity,
            'metadata': metadata,
            'modal_title': f'View {metadata.display_name}',
            **kwargs
        }
        
        return render_template('components/modals/view_modal.html', **template_vars)
    
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
            
            # Get existing entity for updates
            if entity_id:
                entity = model_class.query.get_or_404(entity_id)
                operation = 'updated'
            else:
                entity = None
                operation = 'created'

            # Get explicit form class and populate with request data
            form_class = ModalService._get_form_class(model_name)
            if not form_class:
                return {
                    'success': False,
                    'error': f"No modal form available for {model_name}",
                    'html': render_template('components/modals/form_error.html',
                                          error=f"No modal form available for {model_name}")
                }

            form = form_class(obj=entity)
            
            
            # Validate form using WTForms
            if form.validate_on_submit():
                # For create operations, use GenericAPIHandler for duplicate checking
                if not entity_id:
                    from app.utils.core.base_handlers import GenericAPIHandler

                    # Get form data as dict
                    form_data = {}
                    for field in form:
                        if field.name != 'csrf_token':
                            form_data[field.name] = field.data

                    # Determine allowed fields based on model
                    allowed_fields_map = {
                        'Company': ['name', 'industry', 'website', 'employee_count'],
                        'Stakeholder': ['name', 'job_title', 'email', 'company_id'],
                        'Opportunity': ['description', 'value', 'stage', 'close_date', 'company_id', 'priority'],
                        'Task': ['description', 'due_date', 'priority', 'status', 'next_step_type', 'task_type']
                    }
                    allowed_fields = allowed_fields_map.get(model_name, [])

                    # Use GenericAPIHandler for creation with duplicate checking
                    handler = GenericAPIHandler(model_class, model_name.lower())
                    result = handler.create_entity_from_data(form_data, allowed_fields)

                    if result['success']:
                        entity = result['entity']
                        return {
                            'success': True,
                            'message': f"{model_name} {operation} successfully",
                            'entity_id': entity.id,
                            'html': render_template('components/modals/form_success.html',
                                                  message=f"{model_name} {operation} successfully",
                                                  entity=entity)
                        }
                    else:
                        # Handle duplicate error by adding to form errors
                        if result.get('type') == 'duplicate' and result.get('field'):
                            field = getattr(form, result['field'], None)
                            if field:
                                field.errors.append(result['error'])
                        else:
                            # General error - add to form
                            form.errors['general'] = [result.get('error', 'Unknown error')]

                        # Re-render form with errors
                        action_url = f'/modals/{model_name}/create'
                        modal_title = f'Create {model_name}'

                        template_vars = {
                            'model_name': model_name,
                            'model_class': model_class,
                            'form': form,
                            'action_url': action_url,
                            'modal_title': modal_title,
                            'is_edit': False,
                        }

                        return {
                            'success': False,
                            'errors': form.errors,
                            'html': render_template('components/modals/wtforms_modal.html', **template_vars)
                        }

                else:
                    # For update operations, use existing logic
                    # Populate entity with form data using WTForms
                    form.populate_obj(entity)
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