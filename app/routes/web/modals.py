"""
Generic Modal Routes for HTMX-based Forms

This module provides generic routes for handling modal forms for any model,
leveraging the ModelIntrospector and ModalService systems.
"""

from flask import Blueprint, request, jsonify
from app.utils.ui.modal_service import ModalService
from app.utils.core.model_introspection import get_model_by_name

modals_bp = Blueprint('modals', __name__, url_prefix='/modals')


@modals_bp.route('/<model_name>/create')
def create_modal(model_name):
    """
    Render create modal for any model.
    
    GET /modals/{model_name}/create
    """
    return ModalService.render_create_modal(model_name)


@modals_bp.route('/<model_name>/<int:entity_id>/edit')
def edit_modal(model_name, entity_id):
    """
    Render edit modal for any model and entity.
    
    GET /modals/{model_name}/{entity_id}/edit
    """
    return ModalService.render_edit_modal(model_name, entity_id)


@modals_bp.route('/<model_name>/<int:entity_id>/view')
def view_modal(model_name, entity_id):
    """
    Render read-only view modal for any model and entity.
    
    GET /modals/{model_name}/{entity_id}/view
    """
    return ModalService.render_view_modal(model_name, entity_id)


@modals_bp.route('/<model_name>/create', methods=['POST'])
def create_entity(model_name):
    """
    Handle form submission for creating new entity.
    
    POST /modals/{model_name}/create
    """
    result = ModalService.process_form_submission(model_name)
    
    if result['success']:
        return result['html']
    else:
        return result['html'], 400


@modals_bp.route('/<model_name>/<int:entity_id>/update', methods=['POST'])
def update_entity(model_name, entity_id):
    """
    Handle form submission for updating existing entity.
    
    POST /modals/{model_name}/{entity_id}/update
    """
    result = ModalService.process_form_submission(model_name, entity_id)
    
    if result['success']:
        return result['html']
    else:
        return result['html'], 400


@modals_bp.route('/close')
def close_modal():
    """
    Return modal close response.
    
    GET /modals/close
    """
    return ModalService.render_modal_close()


@modals_bp.route('/<model_name>/fields/<field_name>/choices')
def get_field_choices(model_name, field_name):
    """
    Get field choices as JSON for dynamic form updates.
    
    GET /modals/{model_name}/fields/{field_name}/choices
    """
    result = ModalService.get_field_choices_json(model_name, field_name)
    return jsonify(result)


