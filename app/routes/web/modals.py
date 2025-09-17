"""
Generic Modal Routes for HTMX-based Forms - DRY Refactored

Clean, maintainable modal handling with zero duplication.
"""

from flask import Blueprint, request, render_template
from app.models import db, MODEL_REGISTRY

modals_bp = Blueprint('modals', __name__, url_prefix='/modals')


# ============= HELPER FUNCTIONS =============

def _get_form_class(model_name):
    """Dynamically import and return form class for model."""
    form_class_name = f'{model_name.title()}Form'
    module_names = [model_name, f'{model_name}s']  # Try singular and plural

    for module_name in module_names:
        try:
            module = __import__(f'app.forms.entities.{module_name}', fromlist=[form_class_name])
            return getattr(module, form_class_name)
        except (ImportError, AttributeError):
            continue

    # Let it fail with proper error if not found
    raise ImportError(f"Form class {form_class_name} not found for model {model_name}")

def _validate_model_and_form(model_name):
    """Validate model and form exist, return components or raise error template."""
    model_class = MODEL_REGISTRY.get(model_name.lower())
    if not model_class:
        return None, None, render_template('components/modals/error_modal.html',
                                          error=f"Unknown model: {model_name}")

    try:
        form_class = _get_form_class(model_name.lower())
        return model_class, form_class, None
    except ImportError:
        return None, None, render_template('components/modals/error_modal.html',
                                          error=f"No form available for {model_name}")


def _render_modal(model_name, model_class, form, mode='create', entity=None, error=None):
    """Render modal template with appropriate parameters."""
    context = {
        'model_name': model_name,
        'model_class': model_class,
        'form': form,
        'modal_title': f"{'View' if mode == 'view' else mode.title()} {model_name.title()}",
        'error': error
    }

    mode_configs = {
        'view': {
            'mode': 'view',
            'is_view': True,
            'entity': entity,
            'entity_id': entity.id if entity else None
        },
        'edit': {
            'entity': entity,
            'entity_id': entity.id,
            'action_url': f'/modals/{model_name}/{entity.id}/update',
            'is_edit': True
        },
        'create': {
            'action_url': f'/modals/{model_name}/create',
            'is_edit': False
        }
    }

    context.update(mode_configs.get(mode, mode_configs['create']))
    return render_template('components/modals/wtforms_modal.html', **context)


def _save_new_entity(model_class, form):
    """Create and save a new entity."""
    entity = model_class()
    form.populate_obj(entity)
    db.session.add(entity)
    return entity


def _save_existing_entity(entity, form):
    """Update an existing entity."""
    form.populate_obj(entity)
    return entity


def _handle_task_relationships(entity, form_data, is_new=False):
    """Handle task entity relationships if applicable."""
    if not form_data or not hasattr(entity, 'set_linked_entities'):
        return

    import json
    try:
        entities_list = json.loads(form_data)
        if is_new:
            db.session.flush()  # Get ID for new tasks
        entity.set_linked_entities(entities_list)
    except (json.JSONDecodeError, TypeError):
        pass  # Invalid JSON, skip silently


def _handle_form_submission(model_name, model_class, form, entity=None):
    """Handle form submission for create or update."""
    if not form.validate_on_submit():
        mode = 'edit' if entity else 'create'
        return _render_modal(model_name, model_class, form, mode=mode, entity=entity)

    try:
        is_new = entity is None
        entity = _save_new_entity(model_class, form) if is_new else _save_existing_entity(entity, form)

        # Handle task relationships if needed
        if model_name.lower() == 'task' and hasattr(form, 'entity'):
            _handle_task_relationships(entity, form.entity.data, is_new)

        db.session.commit()
        action = "created" if is_new else "updated"
        return render_template('components/modals/form_success.html',
                             message=f"{model_name} {action} successfully",
                             entity=entity)
    except Exception as e:
        db.session.rollback()
        mode = 'edit' if entity else 'create'
        return _render_modal(model_name, model_class, form,
                           mode=mode, entity=entity, error=str(e))


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

    # For tasks, populate the entity field with linked entities as JSON
    if model_name.lower() == 'task' and hasattr(entity, 'linked_entities') and entity.linked_entities:
        import json
        entities_data = [{'id': item['id'], 'name': item['name'], 'type': item['type']}
                       for item in entity.linked_entities]
        form.entity.data = json.dumps(entities_data)

    return _render_modal(model_name, model_class, form, mode='edit', entity=entity)


@modals_bp.route('/<model_name>/<int:entity_id>/view')
def view_modal(model_name, entity_id):
    """Render read-only view modal for any model and entity."""
    model_class, form_class, error = _validate_model_and_form(model_name)
    if error:
        return error

    entity = model_class.query.get_or_404(entity_id)
    form = form_class(obj=entity)

    # For tasks, format the linked entities for display
    if model_name.lower() == 'task' and hasattr(entity, 'linked_entities') and entity.linked_entities:
        entity_names = [f"{item['name']} ({item['type']})" for item in entity.linked_entities]
        form.entity.data = ', '.join(entity_names)

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


@modals_bp.route('/<model_name>/<int:entity_id>/delete')
def delete_modal(model_name, entity_id):
    """Render delete confirmation modal for any model and entity."""
    model_class, form_class, error = _validate_model_and_form(model_name)
    if error:
        return error

    entity = model_class.query.get_or_404(entity_id)
    return render_template('components/modals/delete_modal.html',
                         model_name=model_name,
                         entity=entity,
                         entity_id=entity_id,
                         modal_title=f"Delete {model_name.title()}")


@modals_bp.route('/<model_name>/<int:entity_id>/delete', methods=['POST'])
def delete_entity(model_name, entity_id):
    """Handle entity deletion."""
    model_class, form_class, error = _validate_model_and_form(model_name)
    if error:
        return render_template('components/modals/form_error.html',
                             error=error.get_data(as_text=True))

    entity = model_class.query.get_or_404(entity_id)
    try:
        db.session.delete(entity)
        db.session.commit()
        return render_template('components/modals/form_success.html',
                             message=f"{model_name.title()} deleted successfully")
    except Exception as e:
        db.session.rollback()
        return render_template('components/modals/form_error.html',
                             error=str(e))


@modals_bp.route('/close')
def close_modal():
    """Return modal close response."""
    return render_template('components/modals/modal_close.html')