"""
Generic Modal Routes for HTMX-based Forms - Ultra DRY, Zero Duplication

Follows Python best practices: DRY, KISS, YAGNI, single responsibility.
"""

from functools import wraps
from flask import Blueprint, render_template, request
from app.models import db, MODEL_REGISTRY
from app.utils.logging_decorators import log_route, log_form_processing, log_template_render
from app.utils.logging_config import get_crm_logger, log_form_operation, log_database_operation
from app.utils.form_logger import form_logger, meddpicc_logger, template_logger
from app.logging_config import routes_logger, forms_logger, templates_logger
import json
import time

modals_bp = Blueprint("modals", __name__, url_prefix="/modals")

# Initialize logger for this module
logger = get_crm_logger(__name__)


def handle_errors(f):
    """Decorator for consistent error handling with logging."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            # Use both logging systems for comprehensive coverage
            logger.error(
                f"Modal operation failed: {f.__name__}",
                extra={
                    "custom_fields": {
                        "function": f.__name__,
                        "error": str(e),
                        "request_path": request.path,
                        "request_method": request.method,
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }
                },
                exc_info=True
            )
            return render_template("components/modals/form_error.html", error=str(e))

    return wrapper
    return wrapper


def get_model_and_form(model_name):
    """Get model and form class or raise ValueError."""
    model = MODEL_REGISTRY.get(model_name.lower())
    if not model:
        raise ValueError(f"Unknown model: {model_name}")

    # Special handling for User modal - use simplified modal form
    # This provides a streamlined user creation experience with only essential fields
    # (Full Name and Job Title) displayed side-by-side in the modal
    if model_name.lower() == "user":
        try:
            from app.forms.modals.user import UserModalForm
            return model, UserModalForm
        except ImportError:
            pass  # Fall back to regular form lookup if modal form not available

    # Dynamic form import
    form_name = f"{model_name.title()}Form"
    for module in [model_name, f"{model_name}s"]:
        try:
            mod = __import__(f"app.forms.entities.{module}", fromlist=[form_name])
            return model, getattr(mod, form_name)
        except (ImportError, AttributeError):
            continue

    raise ValueError(f"No form available for {model_name}")


def render_modal(model_name, form, mode="create", entity=None):
    """Render modal with unified parameters and logging."""
    # Log modal rendering
    form_fields = list(form._fields.keys()) if hasattr(form, '_fields') else []
    template_logger.log_form_render(
        template_name="wtforms_modal.html",
        entity_type=model_name,
        entity_id=entity.id if entity else None,
        mode=mode,
        form_fields=form_fields
    )

    # Log SelectMultipleField rendering if present
    if hasattr(form, 'meddpicc_roles_select'):
        field = form.meddpicc_roles_select
        choices = getattr(field, 'choices', [])
        selected_values = field.data if field.data else []
        template_logger.log_select_multiple_render(
            field_name='meddpicc_roles_select',
            choices=choices,
            selected_values=selected_values,
            entity_type=model_name
        )

    params = {
        "model_name": model_name,
        "model_class": MODEL_REGISTRY.get(model_name.lower()),
        "form": form,
        "modal_title": f"{mode.title()} {model_name.title()}",
        "mode": mode,
        "is_view": mode == "view",
        "is_edit": mode == "edit",
    }

    if entity:
        params["entity"] = entity
        params["entity_id"] = entity.id

    if mode != "view":
        if entity:
            params["action_url"] = f"/modals/{model_name}/{entity.id}/update"
        else:
            params["action_url"] = f"/modals/{model_name}/create"

    return render_template("components/modals/wtforms_modal.html", **params)


def handle_stakeholder_meddpic_roles(entity, form, is_new):
    """Handle stakeholder MEDDPIC roles assignment with comprehensive logging."""
    operation_start = time.time()

    # Log start of MEDDPICC processing
    meddpicc_logger.log_role_processing_start(
        stakeholder_id=entity.id if not is_new else None,
        form_data=form.meddpicc_roles.data
    )

    try:
        roles_data = form.meddpicc_roles.data
        if not roles_data:
            logger.info(
                "No MEDDPICC roles data provided",
                extra={
                    "custom_fields": {
                        "stakeholder_id": entity.id if not is_new else None,
                        "is_new_entity": is_new
                    },
                    "entity_type": "stakeholder",
                    "form_operation": "meddpicc_roles_empty"
                }
            )
            return

        # Log role data parsing
        original_roles_data = roles_data
        roles = json.loads(roles_data) if isinstance(roles_data, str) else roles_data

        meddpicc_logger.log_role_data_parsing(
            stakeholder_id=entity.id if not is_new else None,
            raw_data=str(original_roles_data),
            parsed_data=roles if isinstance(roles, list) else [],
            success=isinstance(roles, list)
        )

        if not isinstance(roles, list):
            logger.warning(
                "Invalid MEDDPICC roles data format",
                extra={
                    "custom_fields": {
                        "stakeholder_id": entity.id if not is_new else None,
                        "roles_data": str(roles_data),
                        "parsed_type": type(roles).__name__
                    },
                    "entity_type": "stakeholder",
                    "form_operation": "meddpicc_roles_invalid_format"
                }
            )
            return

        # Get previous roles for logging
        previous_roles = []
        if not is_new:
            previous_roles = entity.get_meddpicc_role_names()

        # For existing entities, clear current roles first
        if not is_new:
            db.session.flush()  # Ensure entity has ID
            # Remove all existing roles
            from app.models.stakeholder import stakeholder_meddpicc_roles

            meddpicc_logger.log_role_database_operation(
                stakeholder_id=entity.id,
                operation="delete_existing",
                roles=previous_roles,
                success=True
            )

            delete_stmt = stakeholder_meddpicc_roles.delete().where(
                stakeholder_meddpicc_roles.c.stakeholder_id == entity.id
            )
            db.session.execute(delete_stmt)

        # Add new roles
        db.session.flush()  # Ensure entity has ID for new entities
        added_roles = []
        for role in roles:
            role_id = None
            if isinstance(role, dict) and "id" in role:
                role_id = role["id"]
                entity.add_meddpicc_role(role_id)
            elif isinstance(role, str):
                role_id = role
                entity.add_meddpicc_role(role)

            if role_id:
                added_roles.append(role_id)

        # Log role assignment completion
        meddpicc_logger.log_role_assignment(
            stakeholder_id=entity.id,
            previous_roles=previous_roles,
            new_roles=added_roles,
            success=True
        )

        meddpicc_logger.log_role_database_operation(
            stakeholder_id=entity.id,
            operation="insert_new",
            roles=added_roles,
            success=True
        )

        operation_time = (time.time() - operation_start) * 1000
        logger.info(
            f"MEDDPICC roles processing completed for stakeholder {entity.id}",
            extra={
                "custom_fields": {
                    "stakeholder_id": entity.id,
                    "previous_roles": previous_roles,
                    "new_roles": added_roles,
                    "processing_time_ms": operation_time,
                    "is_new_entity": is_new
                },
                "entity_type": "stakeholder",
                "entity_id": entity.id,
                "form_operation": "meddpicc_roles_completed",
                "response_time_ms": operation_time
            }
        )

    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        error_msg = str(e)
        logger.error(
            f"MEDDPICC roles processing failed for stakeholder",
            extra={
                "custom_fields": {
                    "stakeholder_id": entity.id if not is_new else None,
                    "error": error_msg,
                    "roles_data": str(form.meddpicc_roles.data),
                    "is_new_entity": is_new
                },
                "entity_type": "stakeholder",
                "form_operation": "meddpicc_roles_error"
            },
            exc_info=True
        )

        meddpicc_logger.log_role_assignment(
            stakeholder_id=entity.id if not is_new else 0,
            previous_roles=previous_roles if 'previous_roles' in locals() else [],
            new_roles=[],
            success=False
        )


def handle_task_relationships(entity, form, action):
    """Handle special Task entity relationships."""
    if not (hasattr(entity, "set_linked_entities") and hasattr(form, "entity")):
        return

    try:
        entity_data = form.entity.data
        if not entity_data:
            return

        entities = json.loads(entity_data)
        if action == "created":
            db.session.flush()  # Get ID for new tasks
        entity.set_linked_entities(entities)
    except (json.JSONDecodeError, TypeError):
        pass  # Ignore invalid JSON


def process_form_submission(model_name, model, form, entity=None):
    """Process form submission with zero duplication and comprehensive logging."""
    operation_start = time.time()
    is_new = entity is None
    entity_id = entity.id if entity else None

    # Log form submission
    form_logger.log_form_submission(form, model_name, entity_id)

    # Validate form with logging
    if not form_logger.log_form_validation(form, model_name):
        logger.warning(
            f"Form validation failed for {model_name}",
            extra={
                "custom_fields": {
                    "model_name": model_name,
                    "entity_id": entity_id,
                    "is_new": is_new,
                    "validation_errors": {field.name: field.errors for field in form if field.errors}
                },
                "entity_type": model_name,
                "entity_id": entity_id,
                "form_operation": "validation_failed"
            }
        )
        return render_modal(model_name, form, "edit" if entity else "create", entity)

    # Log successful validation
    logger.info(
        f"Form validation successful for {model_name}",
        extra={
            "custom_fields": {
                "model_name": model_name,
                "entity_id": entity_id,
                "is_new": is_new,
                "form_fields": list(form._fields.keys())
            },
            "entity_type": model_name,
            "entity_id": entity_id,
            "form_operation": "validation_passed"
        }
    )

    if is_new:
        entity = model()
        db.session.add(entity)
        logger.info(
            f"Created new {model_name} entity",
            extra={
                "custom_fields": {
                    "model_name": model_name,
                    "operation": "entity_creation"
                },
                "entity_type": model_name,
                "database_operation": "create"
            }
        )

    # Handle all entity search fields (company, core_rep, core_sc, etc.) in a DRY way
    entity_search_fields = {}

    # Identify and store entity search field values before populate_obj
    for field_name in ["company", "core_rep", "core_sc"]:
        if hasattr(form, field_name):
            entity_search_fields[field_name] = getattr(form, field_name).data
            delattr(form, field_name)

    # Populate the entity with regular form fields
    form.populate_obj(entity)

    # Now handle the entity search fields properly
    for field_name, field_value in entity_search_fields.items():
        if not field_value:
            continue

        # Handle foreign key relationships (company field on stakeholder/opportunity)
        if field_name == "company" and model_name.lower() in ["stakeholder", "opportunity"]:
            if str(field_value).isdigit():
                entity.company_id = int(field_value)
            else:
                from app.models import Company
                company = Company.query.filter_by(name=field_value).first()
                if company:
                    entity.company_id = company.id

        # Handle user reference fields (core_rep, core_sc on company)
        elif field_name in ["core_rep", "core_sc"] and model_name.lower() == "company":
            if str(field_value).isdigit():
                from app.models import User
                user = User.query.get(int(field_value))
                if user:
                    setattr(entity, field_name, user.name)
            else:
                # Use the value as-is (it's already a name)
                setattr(entity, field_name, field_value)

        # Default: just set the value directly
        else:
            setattr(entity, field_name, field_value)

    # Special handling for stakeholder MEDDPIC roles
    if model_name.lower() == "stakeholder" and hasattr(form, "meddpicc_roles"):
        logger.info(
            "Starting MEDDPICC roles processing",
            extra={
                "custom_fields": {
                    "stakeholder_id": entity.id,
                    "has_meddpicc_data": bool(form.meddpicc_roles.data)
                },
                "entity_type": "stakeholder",
                "entity_id": entity.id,
                "form_operation": "meddpicc_start"
            }
        )
        handle_stakeholder_meddpic_roles(entity, form, is_new)

    # Special handling for tasks
    if model_name.lower() == "task":
        handle_task_relationships(entity, form, "created" if is_new else "updated")

    # Commit transaction with logging
    try:
        commit_start = time.time()
        db.session.commit()
        commit_time = (time.time() - commit_start) * 1000

        log_database_operation(
            logger,
            operation="commit",
            entity_type=model_name,
            entity_id=entity.id,
            success=True,
            execution_time_ms=commit_time
        )

        operation_time = (time.time() - operation_start) * 1000
        logger.info(
            f"Form submission completed successfully for {model_name}",
            extra={
                "custom_fields": {
                    "model_name": model_name,
                    "entity_id": entity.id,
                    "is_new": is_new,
                    "total_processing_time_ms": operation_time,
                    "commit_time_ms": commit_time
                },
                "entity_type": model_name,
                "entity_id": entity.id,
                "form_operation": "submission_completed",
                "response_time_ms": operation_time
            }
        )

    except Exception as e:
        db.session.rollback()
        logger.error(
            f"Database commit failed for {model_name}",
            extra={
                "custom_fields": {
                    "model_name": model_name,
                    "entity_id": entity.id if entity else None,
                    "is_new": is_new,
                    "error": str(e)
                },
                "entity_type": model_name,
                "database_operation": "commit_failed"
            },
            exc_info=True
        )
        raise

    return render_template(
        "components/modals/form_success.html",
        message=f"{model_name} {'created' if is_new else 'updated'} successfully",
        entity=entity,
    )


def populate_stakeholder_meddpic_roles(entity, form, mode):
    """Populate stakeholder form with MEDDPIC roles data."""
    if not hasattr(form, "meddpicc_roles"):
        return

    # Get current roles
    current_roles = entity.get_meddpicc_role_names()
    if not current_roles:
        return

    if mode == "edit":
        # Convert role names to the expected entity format
        roles_data = [
            {"id": role, "name": role.replace("_", " ").title(), "type": "choice"}
            for role in current_roles
        ]
        form.meddpicc_roles.data = json.dumps(roles_data)
        # Also set the data for the SelectMultipleField
        if hasattr(form, "meddpicc_roles_select"):
            form.meddpicc_roles_select.data = current_roles
    else:  # view mode
        # For view mode, show as readable text
        role_labels = []
        from app.models.stakeholder import Stakeholder

        choices_dict = dict(Stakeholder.get_field_choices("meddpicc_role"))
        for role in current_roles:
            role_labels.append(choices_dict.get(role, role))
        form.meddpicc_roles.data = ", ".join(role_labels)
        # Also set for the select field in view mode
        if hasattr(form, "meddpicc_roles_select"):
            form.meddpicc_roles_select.data = current_roles


def populate_task_form_data(entity, form, mode):
    """Populate task form with linked entities data."""
    if not hasattr(entity, "linked_entities"):
        return

    linked = entity.linked_entities
    if not linked:
        return

    if mode == "edit":
        entities_data = [
            {"id": e["id"], "name": e["name"], "type": e["type"]} for e in linked
        ]
        form.entity.data = json.dumps(entities_data)
    else:  # view mode
        entity_names = [f"{e['name']} ({e['type']})" for e in linked]
        form.entity.data = ", ".join(entity_names)


def populate_entity_search_fields(entity, form, mode):
    """Universal function to populate all entity search fields for edit mode."""
    if mode != "edit":
        return  # Only handle edit mode, view mode works fine with form_class(obj=entity)

    # Handle user reference fields (core_rep, core_sc)
    user_fields = ['core_rep', 'core_sc']
    for field_name in user_fields:
        if hasattr(form, field_name) and hasattr(entity, field_name):
            field_value = getattr(entity, field_name)
            if field_value:
                from app.models import User
                user = User.query.filter_by(name=field_value).first()
                if user:
                    getattr(form, field_name).data = str(user.id)
                    # Set search display value for template
                    getattr(form, field_name).search_display_value = field_value

    # Handle choice fields (industry, stage, etc.)
    choice_fields = ['industry', 'stage']
    for field_name in choice_fields:
        if hasattr(form, field_name) and hasattr(entity, field_name):
            field_value = getattr(entity, field_name)
            if field_value:
                # For choice fields, set search display value to the human-readable label
                field_obj = getattr(form, field_name)
                if hasattr(field_obj, 'choices'):
                    # Find the label for this choice value
                    choice_label = None
                    for choice_value, choice_text in field_obj.choices:
                        if choice_value == field_value:
                            choice_label = choice_text
                            break
                    if choice_label:
                        field_obj.search_display_value = choice_label
                else:
                    # Fallback: use the value as display
                    field_obj.search_display_value = field_value

    # Handle entity reference fields (company)
    entity_fields = ['company']
    for field_name in entity_fields:
        if hasattr(form, field_name) and hasattr(entity, f"{field_name}_id"):
            entity_id = getattr(entity, f"{field_name}_id")
            if entity_id:
                # Look up the entity name by ID
                if field_name == 'company':
                    from app.models import Company
                    ref_entity = Company.query.get(entity_id)
                    if ref_entity:
                        getattr(form, field_name).data = str(entity_id)
                        getattr(form, field_name).search_display_value = ref_entity.name


# ============= ROUTE HANDLERS - DRY CONSOLIDATED =============


@modals_bp.route("/<model_name>/create")
@handle_errors
@log_route(logger=routes_logger)
@log_template_render()
def create_modal(model_name):
    """Create modal for any model."""
    templates_logger.info(f"Rendering create modal for {model_name}",
                         extra={'extra_fields': {'model_name': model_name, 'mode': 'create'}})
    model, form_class = get_model_and_form(model_name)
    return render_modal(model_name, form_class(), "create")


@modals_bp.route("/<model_name>/<int:entity_id>/<mode>")
@handle_errors
@log_route(logger=routes_logger)
@log_template_render()
def entity_modal(model_name, entity_id, mode):
    """View/Edit/Delete modal for any entity - single handler."""
    if mode not in ["view", "edit", "delete"]:
        raise ValueError(f"Invalid mode: {mode}")

    templates_logger.info(f"Rendering {mode} modal for {model_name} ID {entity_id}",
                         extra={'extra_fields': {'model_name': model_name, 'entity_id': entity_id, 'mode': mode}})

    model, form_class = get_model_and_form(model_name)
    entity = model.query.get_or_404(entity_id)

    if mode == "delete":
        return render_template(
            "components/modals/delete_modal.html",
            model_name=model_name,
            entity=entity,
            entity_id=entity_id,
            modal_title=f"Delete {model_name.title()}",
        )

    form = form_class(obj=entity)

    # Handle task relationships
    if model_name.lower() == "task":
        populate_task_form_data(entity, form, mode)

    # Handle stakeholder MEDDPIC roles
    if model_name.lower() == "stakeholder":
        populate_stakeholder_meddpic_roles(entity, form, mode)

    # Handle entity search fields for all models (universal DRY approach)
    populate_entity_search_fields(entity, form, mode)

    return render_modal(model_name, form, mode, entity)


@modals_bp.route("/<model_name>/create", methods=["POST"])
@handle_errors
def create_entity(model_name):
    """Create new entity - POST handler."""
    model, form_class = get_model_and_form(model_name)
    return process_form_submission(model_name, model, form_class())


@modals_bp.route("/<model_name>/<int:entity_id>/update", methods=["POST"])
@handle_errors
def update_entity(model_name, entity_id):
    """Update existing entity - POST handler."""
    model, form_class = get_model_and_form(model_name)
    entity = model.query.get_or_404(entity_id)
    form = form_class(obj=entity)
    form._obj = entity  # Set _obj for validation to recognize we're editing this entity
    return process_form_submission(model_name, model, form, entity)


@modals_bp.route("/<model_name>/<int:entity_id>/delete", methods=["POST"])
@handle_errors
def delete_entity(model_name, entity_id):
    """Delete entity with modern safety checks."""
    model, _ = get_model_and_form(model_name)
    entity = model.query.get_or_404(entity_id)

    # Use modern deletion with safety checks
    result = entity.delete_safely()

    if not result["success"]:
        return (
            render_template(
                "components/modals/form_error.html",
                error=result["error"],
                impact=result.get("impact"),
            ),
            400,
        )

    # Show impact information on successful deletion
    cascade_info = ""
    if result["impact"]["will_cascade"]:
        cascade_count = sum(item["count"] for item in result["impact"]["will_cascade"])
        cascade_info = f" ({cascade_count} related items also deleted)"

    # Determine the correct refresh URL for this entity type using proper table name
    table_name = model.__tablename__
    refresh_url = f"/{table_name}/content"

    return render_template(
        "components/modals/form_success.html",
        message=f"{model_name.title()} deleted successfully{cascade_info}",
        refresh_url=refresh_url,
        deleted_entity_id=f"entity-{model_name}-{entity_id}",
    )


@modals_bp.route("/close")
def close_modal():
    """Close modal response."""
    return render_template("components/modals/modal_close.html")


@modals_bp.route("/<model_name>/<int:entity_id>/tab/<tab_name>")
@handle_errors
def entity_tab_content(model_name, entity_id, tab_name):
    """Load tab content for entity modals - supports paginated data."""
    model, _ = get_model_and_form(model_name)
    entity = model.query.get_or_404(entity_id)

    # Handle different tabs based on model type
    if model_name.lower() == "company":
        if tab_name == "about":
            # Return the about tab content with company details
            return render_template(
                "components/modals/tabs/company_about.html",
                entity=entity,
                model_name=model_name
            )
        elif tab_name == "team":
            # Return the account team tab content
            return render_template(
                "components/modals/tabs/company_team.html",
                entity=entity,
                model_name=model_name
            )
        elif tab_name == "opportunities":
            # Get paginated opportunities for this company
            from app.models import Opportunity
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 10, type=int)

            opportunities = Opportunity.query.filter_by(company_id=entity.id).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            return render_template(
                "components/modals/tabs/company_opportunities.html",
                entity=entity,
                opportunities=opportunities,
                model_name=model_name
            )
        elif tab_name == "stakeholders":
            # Get paginated stakeholders for this company
            from app.models import Stakeholder
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 10, type=int)

            stakeholders = Stakeholder.query.filter_by(company_id=entity.id).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            return render_template(
                "components/modals/tabs/company_stakeholders.html",
                entity=entity,
                stakeholders=stakeholders,
                model_name=model_name
            )

    # Default: return empty content for unsupported tabs
    return render_template(
        "components/modals/tabs/empty_tab.html",
        message=f"Tab '{tab_name}' is not available for {model_name}"
    )
