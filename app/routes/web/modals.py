"""
Generic Modal Routes for HTMX-based Forms

Direct, simple modal handling without unnecessary abstraction layers.
"""

from flask import Blueprint, request, render_template, jsonify
from app.models import db, MODEL_REGISTRY
from app.forms.entities.company import CompanyForm
from app.forms.entities.stakeholder import StakeholderForm
from app.forms.entities.opportunity import OpportunityForm
from app.forms.modals.task import TaskModalForm
from app.forms.modals.user import UserModalForm

modals_bp = Blueprint('modals', __name__, url_prefix='/modals')

# Form registry - maps model names to form classes
FORM_REGISTRY = {
    'company': CompanyForm,
    'stakeholder': StakeholderForm,
    'opportunity': OpportunityForm,
    'task': TaskModalForm,
    'user': UserModalForm
}

# Models that require modal_mode parameter
MODAL_MODE_MODELS = {'company', 'stakeholder', 'opportunity'}


@modals_bp.route('/<model_name>/create')
def create_modal(model_name):
    """Render create modal for any model."""
    model_class = MODEL_REGISTRY.get(model_name.lower())
    if not model_class:
        return render_template('components/modals/error_modal.html',
                             error=f"Unknown model: {model_name}")

    form_class = FORM_REGISTRY.get(model_name.lower())
    if not form_class:
        return render_template('components/modals/error_modal.html',
                             error=f"No form available for {model_name}")

    # Create form with modal_mode if needed
    if model_name.lower() in MODAL_MODE_MODELS:
        form = form_class(modal_mode=True)
    else:
        form = form_class()

    return render_template('components/modals/wtforms_modal.html',
                         model_name=model_name,
                         model_class=model_class,
                         form=form,
                         action_url=f'/modals/{model_name}/create',
                         modal_title=f'Create {model_name}',
                         is_edit=False)


@modals_bp.route('/<model_name>/<int:entity_id>/edit')
def edit_modal(model_name, entity_id):
    """Render edit modal for any model and entity."""
    model_class = MODEL_REGISTRY.get(model_name.lower())
    if not model_class:
        return render_template('components/modals/error_modal.html',
                             error=f"Unknown model: {model_name}")

    entity = model_class.query.get_or_404(entity_id)

    form_class = FORM_REGISTRY.get(model_name.lower())
    if not form_class:
        return render_template('components/modals/error_modal.html',
                             error=f"No form available for {model_name}")

    # Create form with entity and modal_mode if needed
    if model_name.lower() in MODAL_MODE_MODELS:
        form = form_class(obj=entity, modal_mode=True)
    else:
        form = form_class(obj=entity)

    return render_template('components/modals/wtforms_modal.html',
                         model_name=model_name,
                         model_class=model_class,
                         entity=entity,
                         entity_id=entity_id,
                         form=form,
                         action_url=f'/modals/{model_name}/{entity_id}/update',
                         modal_title=f'Edit {model_name}',
                         is_edit=True)


@modals_bp.route('/<model_name>/<int:entity_id>/view')
def view_modal(model_name, entity_id):
    """Render read-only view modal for any model and entity."""
    model_class = MODEL_REGISTRY.get(model_name.lower())
    if not model_class:
        return render_template('components/modals/error_modal.html',
                             error=f"Unknown model: {model_name}")

    entity = model_class.query.get_or_404(entity_id)

    form_class = FORM_REGISTRY.get(model_name.lower())
    if not form_class:
        return render_template('components/modals/error_modal.html',
                             error=f"No form available for {model_name}")

    # Create form for viewing
    if model_name.lower() in MODAL_MODE_MODELS:
        form = form_class(obj=entity, modal_mode=True)
    else:
        form = form_class(obj=entity)

    return render_template('components/modals/wtforms_modal.html',
                         model_name=model_name,
                         model_class=model_class,
                         entity=entity,
                         entity_id=entity_id,
                         form=form,
                         modal_title=f'View {model_name}',
                         mode='view',
                         is_edit=False,
                         is_view=True)


@modals_bp.route('/<model_name>/create', methods=['POST'])
def create_entity(model_name):
    """Handle form submission for creating new entity."""
    model_class = MODEL_REGISTRY.get(model_name.lower())
    if not model_class:
        return render_template('components/modals/form_error.html',
                             error=f"Unknown model: {model_name}")

    form_class = FORM_REGISTRY.get(model_name.lower())
    if not form_class:
        return render_template('components/modals/form_error.html',
                             error=f"No form available for {model_name}")

    # Create and validate form
    if model_name.lower() in MODAL_MODE_MODELS:
        form = form_class(modal_mode=True)
    else:
        form = form_class()

    if form.validate_on_submit():
        try:
            # Create new entity from form data
            entity = model_class()
            form.populate_obj(entity)
            db.session.add(entity)
            db.session.commit()

            return render_template('components/modals/form_success.html',
                                 message=f"{model_name} created successfully",
                                 entity=entity)
        except Exception as e:
            db.session.rollback()
            # Re-render form with error
            return render_template('components/modals/wtforms_modal.html',
                                 model_name=model_name,
                                 model_class=model_class,
                                 form=form,
                                 action_url=f'/modals/{model_name}/create',
                                 modal_title=f'Create {model_name}',
                                 is_edit=False,
                                 error=str(e))

    # Form validation failed - re-render with errors
    return render_template('components/modals/wtforms_modal.html',
                         model_name=model_name,
                         model_class=model_class,
                         form=form,
                         action_url=f'/modals/{model_name}/create',
                         modal_title=f'Create {model_name}',
                         is_edit=False)


@modals_bp.route('/<model_name>/<int:entity_id>/update', methods=['POST'])
def update_entity(model_name, entity_id):
    """Handle form submission for updating existing entity."""
    model_class = MODEL_REGISTRY.get(model_name.lower())
    if not model_class:
        return render_template('components/modals/form_error.html',
                             error=f"Unknown model: {model_name}")

    entity = model_class.query.get_or_404(entity_id)

    form_class = FORM_REGISTRY.get(model_name.lower())
    if not form_class:
        return render_template('components/modals/form_error.html',
                             error=f"No form available for {model_name}")

    # Create and validate form
    if model_name.lower() in MODAL_MODE_MODELS:
        form = form_class(obj=entity, modal_mode=True)
    else:
        form = form_class(obj=entity)

    if form.validate_on_submit():
        try:
            # Update entity from form data
            form.populate_obj(entity)
            db.session.commit()

            return render_template('components/modals/form_success.html',
                                 message=f"{model_name} updated successfully",
                                 entity=entity)
        except Exception as e:
            db.session.rollback()
            # Re-render form with error
            return render_template('components/modals/wtforms_modal.html',
                                 model_name=model_name,
                                 model_class=model_class,
                                 entity=entity,
                                 entity_id=entity_id,
                                 form=form,
                                 action_url=f'/modals/{model_name}/{entity_id}/update',
                                 modal_title=f'Edit {model_name}',
                                 is_edit=True,
                                 error=str(e))

    # Form validation failed - re-render with errors
    return render_template('components/modals/wtforms_modal.html',
                         model_name=model_name,
                         model_class=model_class,
                         entity=entity,
                         entity_id=entity_id,
                         form=form,
                         action_url=f'/modals/{model_name}/{entity_id}/update',
                         modal_title=f'Edit {model_name}',
                         is_edit=True)


@modals_bp.route('/close')
def close_modal():
    """Return modal close response."""
    return render_template('components/modals/modal_close.html')