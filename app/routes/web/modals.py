"""
Generic Modal Routes for HTMX-based Forms - Ultra DRY, Zero Duplication

Follows Python best practices: DRY, KISS, YAGNI, single responsibility.
"""

from functools import wraps
from flask import Blueprint, render_template
from app.models import db, MODEL_REGISTRY
import json

modals_bp = Blueprint("modals", __name__, url_prefix="/modals")


def handle_errors(f):
    """Decorator for consistent error handling."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            return render_template("components/modals/form_error.html", error=str(e))
    return wrapper


def get_model_and_form(model_name):
    """Get model and form class or raise ValueError."""
    model = MODEL_REGISTRY.get(model_name.lower())
    if not model:
        raise ValueError(f"Unknown model: {model_name}")

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
    """Render modal with unified parameters."""
    params = {
        "model_name": model_name,
        "model_class": MODEL_REGISTRY.get(model_name.lower()),
        "form": form,
        "modal_title": f"{mode.title()} {model_name.title()}",
        "mode": mode,
        "is_view": mode == "view",
        "is_edit": mode == "edit"
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
    """Handle stakeholder MEDDPIC roles assignment."""
    try:
        roles_data = form.meddpicc_roles.data
        if not roles_data:
            return

        # Parse the roles data
        roles = json.loads(roles_data) if isinstance(roles_data, str) else roles_data
        if not isinstance(roles, list):
            return

        # For existing entities, clear current roles first
        if not is_new:
            db.session.flush()  # Ensure entity has ID
            # Remove all existing roles
            from app.models.stakeholder import stakeholder_meddpicc_roles
            delete_stmt = stakeholder_meddpicc_roles.delete().where(
                stakeholder_meddpicc_roles.c.stakeholder_id == entity.id
            )
            db.session.execute(delete_stmt)

        # Add new roles
        db.session.flush()  # Ensure entity has ID for new entities
        for role in roles:
            if isinstance(role, dict) and 'id' in role:
                entity.add_meddpicc_role(role['id'])
            elif isinstance(role, str):
                entity.add_meddpicc_role(role)

    except (json.JSONDecodeError, TypeError, AttributeError):
        pass  # Ignore invalid data


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
    """Process form submission with zero duplication."""
    if not form.validate_on_submit():
        return render_modal(model_name, form, "edit" if entity else "create", entity)

    is_new = entity is None
    if is_new:
        entity = model()
        db.session.add(entity)

    # Special handling for stakeholder and opportunity company field
    if model_name.lower() in ["stakeholder", "opportunity"] and hasattr(form, "company"):
        # Store company value before populate_obj
        company_value = form.company.data
        # Remove company from form to avoid populate_obj error
        delattr(form, "company")
        form.populate_obj(entity)
        # Handle company relationship
        if company_value:
            try:
                # Extract company ID from the string (format: "TechCorp Solutions" or ID)
                from app.models import Company
                if company_value.isdigit():
                    entity.company_id = int(company_value)
                else:
                    # Try to find company by name
                    company = Company.query.filter_by(name=company_value).first()
                    if company:
                        entity.company_id = company.id
            except (ValueError, AttributeError):
                pass
    else:
        form.populate_obj(entity)

    # Special handling for stakeholder MEDDPIC roles
    if model_name.lower() == "stakeholder" and hasattr(form, "meddpicc_roles"):
        handle_stakeholder_meddpic_roles(entity, form, is_new)

    # Special handling for tasks
    if model_name.lower() == "task":
        handle_task_relationships(entity, form, "created" if is_new else "updated")

    db.session.commit()

    return render_template(
        "components/modals/form_success.html",
        message=f"{model_name} {'created' if is_new else 'updated'} successfully",
        entity=entity
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
        roles_data = [{"id": role, "name": role.replace("_", " ").title(), "type": "choice"} for role in current_roles]
        form.meddpicc_roles.data = json.dumps(roles_data)
    else:  # view mode
        # For view mode, show as readable text
        role_labels = []
        from app.models.stakeholder import Stakeholder
        choices_dict = dict(Stakeholder.get_field_choices("meddpicc_role"))
        for role in current_roles:
            role_labels.append(choices_dict.get(role, role))
        form.meddpicc_roles.data = ", ".join(role_labels)


def populate_task_form_data(entity, form, mode):
    """Populate task form with linked entities data."""
    if not hasattr(entity, "linked_entities"):
        return

    linked = entity.linked_entities
    if not linked:
        return

    if mode == "edit":
        entities_data = [{"id": e["id"], "name": e["name"], "type": e["type"]} for e in linked]
        form.entity.data = json.dumps(entities_data)
    else:  # view mode
        entity_names = [f"{e['name']} ({e['type']})" for e in linked]
        form.entity.data = ", ".join(entity_names)


# ============= ROUTE HANDLERS - DRY CONSOLIDATED =============

@modals_bp.route("/<model_name>/create")
@handle_errors
def create_modal(model_name):
    """Create modal for any model."""
    model, form_class = get_model_and_form(model_name)
    return render_modal(model_name, form_class(), "create")


@modals_bp.route("/<model_name>/<int:entity_id>/<mode>")
@handle_errors
def entity_modal(model_name, entity_id, mode):
    """View/Edit/Delete modal for any entity - single handler."""
    if mode not in ["view", "edit", "delete"]:
        raise ValueError(f"Invalid mode: {mode}")

    model, form_class = get_model_and_form(model_name)
    entity = model.query.get_or_404(entity_id)

    if mode == "delete":
        return render_template(
            "components/modals/delete_modal.html",
            model_name=model_name,
            entity=entity,
            entity_id=entity_id,
            modal_title=f"Delete {model_name.title()}"
        )

    form = form_class(obj=entity)

    # Handle task relationships
    if model_name.lower() == "task":
        populate_task_form_data(entity, form, mode)

    # Handle stakeholder MEDDPIC roles
    if model_name.lower() == "stakeholder":
        populate_stakeholder_meddpic_roles(entity, form, mode)

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
    return process_form_submission(model_name, model, form_class(obj=entity), entity)


@modals_bp.route("/<model_name>/<int:entity_id>/delete", methods=["POST"])
@handle_errors
def delete_entity(model_name, entity_id):
    """Delete entity with modern safety checks."""
    model, _ = get_model_and_form(model_name)
    entity = model.query.get_or_404(entity_id)

    # Use modern deletion with safety checks
    result = entity.delete_safely()

    if not result["success"]:
        return render_template(
            "components/modals/form_error.html",
            error=result["error"],
            impact=result.get("impact")
        ), 400

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
        refresh_url=refresh_url
    )


@modals_bp.route("/close")
def close_modal():
    """Close modal response."""
    return render_template("components/modals/modal_close.html")