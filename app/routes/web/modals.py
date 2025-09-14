"""
Generic Modal Routes for HTMX-based Forms - DRY Refactored

Clean, maintainable modal handling with zero duplication.
"""

from flask import Blueprint, request, render_template
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


# ============= HELPER FUNCTIONS =============

def _validate_model_and_form(model_name):
    """Validate model and form exist, return components or error."""
    model_class = MODEL_REGISTRY.get(model_name.lower())
    if not model_class:
        return None, None, render_template('components/modals/error_modal.html',
                                          error=f"Unknown model: {model_name}")

    form_class = FORM_REGISTRY.get(model_name.lower())
    if not form_class:
        return None, None, render_template('components/modals/error_modal.html',
                                          error=f"No form available for {model_name}")

    return model_class, form_class, None


def _render_modal(model_name, model_class, form, mode='create', entity=None, error=None):
    """Render modal template with appropriate parameters."""
    # Base parameters - always present
    params = {
        'model_name': model_name,
        'model_class': model_class,
        'form': form,
        'modal_title': f'{mode.title()} {model_name}'
    }

    # Mode-specific parameters
    if mode == 'view':
        params.update({
            'mode': 'view',
            'is_view': True,
            'entity': entity,
            'entity_id': entity.id if entity else None
        })
    elif mode == 'edit':
        params.update({
            'entity': entity,
            'entity_id': entity.id,
            'action_url': f'/modals/{model_name}/{entity.id}/update',
            'is_edit': True
        })
    else:  # create
        params.update({
            'action_url': f'/modals/{model_name}/create',
            'is_edit': False
        })

    if error:
        params['error'] = error

    # Use dedicated templates for company and task modals (they have entity search)
    if model_name.lower() == 'company':
        template = 'components/modals/company_modal.html'
    elif model_name.lower() == 'task':
        template = 'components/modals/task_modal.html'
    else:
        template = 'components/modals/wtforms_modal.html'

    return render_template(template, **params)


def _handle_form_submission(model_name, model_class, form, entity=None):
    """Handle form submission for both create and update operations."""
    if form.validate_on_submit():
        try:
            if entity is None:
                # Create new entity
                entity = model_class()
                form.populate_obj(entity)
                db.session.add(entity)
                action = "created"
            else:
                # Update existing entity
                form.populate_obj(entity)
                action = "updated"

            db.session.commit()
            return render_template('components/modals/form_success.html',
                                 message=f"{model_name} {action} successfully",
                                 entity=entity)
        except Exception as e:
            db.session.rollback()
            mode = 'edit' if entity else 'create'
            return _render_modal(model_name, model_class, form,
                               mode=mode, entity=entity, error=str(e))

    # Form validation failed - re-render with errors
    mode = 'edit' if entity else 'create'
    return _render_modal(model_name, model_class, form, mode=mode, entity=entity)


# ============= ROUTE HANDLERS =============

@modals_bp.route('/<model_name>/create')
def create_modal(model_name):
    """Render create modal for any model."""
    model_class, form_class, error = _validate_model_and_form(model_name)
    if error:
        return error

    form = form_class()
    return _render_modal(model_name, model_class, form, mode='create')


@modals_bp.route('/<model_name>/<int:entity_id>/edit')
def edit_modal(model_name, entity_id):
    """Render edit modal for any model and entity."""
    model_class, form_class, error = _validate_model_and_form(model_name)
    if error:
        return error

    entity = model_class.query.get_or_404(entity_id)
    form = form_class(obj=entity)
    return _render_modal(model_name, model_class, form, mode='edit', entity=entity)


@modals_bp.route('/<model_name>/<int:entity_id>/view')
def view_modal(model_name, entity_id):
    """Render read-only view modal for any model and entity."""
    model_class, form_class, error = _validate_model_and_form(model_name)
    if error:
        return error

    entity = model_class.query.get_or_404(entity_id)
    form = form_class(obj=entity)
    return _render_modal(model_name, model_class, form, mode='view', entity=entity)


@modals_bp.route('/<model_name>/create', methods=['POST'])
def create_entity(model_name):
    """Handle form submission for creating new entity."""
    model_class, form_class, error = _validate_model_and_form(model_name)
    if error:
        return render_template('components/modals/form_error.html',
                             error=error.get_data(as_text=True))

    form = form_class()
    return _handle_form_submission(model_name, model_class, form)


@modals_bp.route('/<model_name>/<int:entity_id>/update', methods=['POST'])
def update_entity(model_name, entity_id):
    """Handle form submission for updating existing entity."""
    model_class, form_class, error = _validate_model_and_form(model_name)
    if error:
        return render_template('components/modals/form_error.html',
                             error=error.get_data(as_text=True))

    entity = model_class.query.get_or_404(entity_id)
    form = form_class(obj=entity)
    return _handle_form_submission(model_name, model_class, form, entity=entity)


@modals_bp.route('/close')
def close_modal():
    """Return modal close response."""
    return render_template('components/modals/modal_close.html')