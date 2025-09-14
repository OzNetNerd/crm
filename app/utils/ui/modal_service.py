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
from app.forms.entities.company import CompanyForm
from app.forms.entities.stakeholder import StakeholderForm
from app.forms.entities.opportunity import OpportunityForm
from app.forms.modals.task import TaskModalForm
from app.forms.modals.user import UserModalForm
from app.forms.base.base_forms import BaseForm
# No icon functions needed - templates handle CSS class generation



class ModalService:
    """
    Service for handling modal forms using HTMX and explicit form classes.
    """

    # Models that require modal_mode parameter
    MODAL_MODE_MODELS = {'company', 'stakeholder', 'opportunity'}

    # Allowed fields for each model during creation
    ALLOWED_FIELDS_MAP = {
        'Company': ['name', 'industry', 'website', 'employee_count'],
        'Stakeholder': ['name', 'job_title', 'email', 'company_id'],
        'Opportunity': ['description', 'value', 'stage', 'close_date', 'company_id', 'priority'],
        'Task': ['description', 'due_date', 'priority', 'status', 'next_step_type', 'task_type']
    }

    @staticmethod
    def _render_error(error_message: str) -> str:
        """Render error modal with consistent formatting."""
        return render_template('components/modals/error_modal.html', error=error_message)

    @staticmethod
    def _create_form(model_name: str, form_class, entity=None):
        """Create form instance with appropriate parameters."""
        if model_name.lower() in ModalService.MODAL_MODE_MODELS:
            return form_class(obj=entity, modal_mode=True) if entity else form_class(modal_mode=True)
        return form_class(obj=entity) if entity else form_class()

    @staticmethod
    def _build_template_vars(model_name: str, model_class, form,
                            entity=None, entity_id=None, mode='create', **kwargs) -> dict:
        """Build template variables for modal rendering."""
        if mode == 'view':
            return {
                'model_name': model_name,
                'model_class': model_class,
                'entity': entity,
                'entity_id': entity_id,
                'form': form,
                'modal_title': f'View {model_name}',
                'mode': 'view',
                'is_edit': False,
                'is_view': True,
                **kwargs
            }

        is_edit = mode == 'edit'
        action_url = f'/modals/{model_name}/{entity_id}/update' if is_edit else f'/modals/{model_name}/create'
        modal_title = f'Edit {model_name}' if is_edit else f'Create {model_name}'

        vars = {
            'model_name': model_name,
            'model_class': model_class,
            'form': form,
            'action_url': action_url,
            'modal_title': modal_title,
            'is_edit': is_edit,
            **kwargs
        }

        if entity:
            vars['entity'] = entity

        return vars

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
            'Company': CompanyForm,
            'company': CompanyForm,  # Support both cases
            'Task': TaskModalForm,
            'task': TaskModalForm,
            'Stakeholder': StakeholderForm,
            'stakeholder': StakeholderForm,
            'Opportunity': OpportunityForm,
            'opportunity': OpportunityForm,
            'User': UserModalForm,
            'user': UserModalForm,
        }
        # Try exact match first, then title case
        return form_classes.get(model_name) or form_classes.get(model_name.title())

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
            return ModalService._render_error(f"Unknown model: {model_name}")

        form_class = ModalService._get_form_class(model_name)
        if not form_class:
            return ModalService._render_error(f"No modal form available for {model_name}")

        form = ModalService._create_form(model_name, form_class)
        template_vars = ModalService._build_template_vars(
            model_name, model_class, form, mode='create', **kwargs
        )

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
            return ModalService._render_error(f"Unknown model: {model_name}")

        entity = model_class.query.get_or_404(entity_id)

        form_class = ModalService._get_form_class(model_name)
        if not form_class:
            return ModalService._render_error(f"No modal form available for {model_name}")

        form = ModalService._create_form(model_name, form_class, entity)
        template_vars = ModalService._build_template_vars(
            model_name, model_class, form, entity=entity, entity_id=entity_id, mode='edit', **kwargs
        )

        return render_template('components/modals/wtforms_modal.html', **template_vars)
    
    @staticmethod
    def render_view_modal(model_name: str, entity_id: int, **kwargs) -> str:
        """
        Render a read-only view modal for the specified model and entity.
        Uses the same unified template as edit/create for DRY principles.

        Args:
            model_name: Name of the model (e.g., 'Task', 'Company')
            entity_id: ID of the entity to view
            **kwargs: Additional template variables

        Returns:
            Rendered HTML for the read-only modal
        """
        model_class = get_model_by_name(model_name)
        if not model_class:
            return ModalService._render_error(f"Unknown model: {model_name}")

        entity = model_class.query.get_or_404(entity_id)

        form_class = ModalService._get_form_class(model_name)
        if not form_class:
            return ModalService._render_error(f"No modal form available for {model_name}")

        form = ModalService._create_form(model_name, form_class, entity)
        template_vars = ModalService._build_template_vars(
            model_name, model_class, form, entity=entity, entity_id=entity_id, mode='view', **kwargs
        )

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

            # Create form with modal_mode for unified forms
            if model_name.lower() in ['company', 'stakeholder', 'opportunity']:
                form = form_class(obj=entity, modal_mode=True)
            else:
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
            return ModalService._render_form_error(f"Error {operation}: {str(e)}")
    
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