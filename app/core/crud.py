"""Generic CRUD operations - Ultra DRY, zero duplication, modern Python."""

from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Any, Union
from functools import wraps
from flask import request, render_template, redirect, url_for, flash, jsonify, Response
from flask_login import current_user, login_required
from werkzeug.wrappers import Response as WerkzeugResponse
from app.models import db


@dataclass
class RouteConfig:
    """Configuration for a single route.

    Attributes:
        url: The URL pattern for the route.
        endpoint: The endpoint name for the route.
        handler: The callable that handles the route.
        methods: List of HTTP methods allowed for the route.
    """
    url: str
    endpoint: str
    handler: Callable
    methods: List[str] = field(default_factory=lambda: ['GET'])


@dataclass
class Templates:
    """Template paths for CRUD operations.

    Attributes:
        list: Template path for list view.
        add: Template path for add form.
        edit: Template path for edit form.
        view: Template path for view details.
    """
    list: str
    add: str
    edit: str
    view: str

    @classmethod
    def for_model(cls, model_name: str) -> "Templates":
        """Create default templates for a model.

        Args:
            model_name: The lowercase name of the model.

        Returns:
            Templates instance with default paths for the model.
        """
        return cls(
            list=f'crm/{model_name}_list.html',
            add=f'crm/add_{model_name}.html',
            edit=f'crm/edit_{model_name}.html',
            view=f'crm/view_{model_name}.html'
        )


def handle_form_errors(form: Any) -> None:
    """Extract and flash form validation errors.

    Args:
        form: WTForms form instance with validation errors.
    """
    for field_name, errors in form.errors.items():
        for error in errors:
            flash(f'{field_name}: {error}', 'error')


def crud_response(
    success: bool = True,
    message: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    redirect_url: Optional[str] = None
) -> Union[Response, WerkzeugResponse]:
    """Generate standardized response for CRUD operations.

    Args:
        success: Whether the operation was successful.
        message: Optional message to display/return.
        data: Optional data for JSON responses.
        redirect_url: Optional URL to redirect to.

    Returns:
        JSON response for API calls or redirect for web requests.
    """
    if request.is_json:
        return jsonify({'success': success, 'message': message, 'data': data})

    if message:
        flash(message, 'success' if success else 'error')

    return redirect(redirect_url) if redirect_url else redirect(request.url)


def error_handler(f: Callable) -> Callable:
    """Decorator for consistent error handling.

    Args:
        f: The function to wrap with error handling.

    Returns:
        Wrapped function with error handling.
    """
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return crud_response(False, str(e), redirect_url=request.url)
        except Exception:
            db.session.rollback()
            return crud_response(False, 'An error occurred', redirect_url=url_for('main.index'))
    return wrapper


class CRUDHandler:
    """Generic CRUD handler eliminating all duplication.

    Attributes:
        model: SQLAlchemy model class.
        form_class: WTForms form class.
        name: Lowercase name of the model.
        templates: Template configuration for views.
    """

    def __init__(
        self,
        model_class: type,
        form_class: type,
        templates: Optional[Templates] = None
    ) -> None:
        """Initialize CRUD handler.

        Args:
            model_class: SQLAlchemy model class to handle.
            form_class: WTForms form class for the model.
            templates: Optional template configuration.
        """
        self.model = model_class
        self.form_class = form_class
        self.name = model_class.__name__.lower()
        self.templates = templates or Templates.for_model(self.name)

    @login_required
    @error_handler
    def create(self) -> Union[str, Response, WerkzeugResponse]:
        """Handle entity creation.

        Returns:
            Template render for GET, redirect for successful POST,
            or template with errors for failed POST.
        """
        if request.method != 'POST':
            return render_template(self.templates.add, form=self.form_class())

        form = self.form_class()
        if not form.validate_on_submit():
            handle_form_errors(form)
            return render_template(self.templates.add, form=form)

        entity = self.model(**form.data, user_id=current_user.id)
        db.session.add(entity)
        db.session.commit()

        return crud_response(
            success=True,
            message=f'{self.model.__name__} created successfully!',
            redirect_url=url_for(f'crm.{self.name}_list')
        )

    @login_required
    @error_handler
    def update(self, entity_id: int) -> Union[str, Response, WerkzeugResponse]:
        """Handle entity update.

        Args:
            entity_id: ID of the entity to update.

        Returns:
            Template render for GET, redirect for successful POST,
            or template with errors for failed POST.
        """
        entity = self.model.query.filter_by(
            id=entity_id,
            user_id=current_user.id
        ).first_or_404()

        if request.method != 'POST':
            form = self.form_class(obj=entity)
            return render_template(self.templates.edit, form=form, entity=entity)

        form = self.form_class()
        if not form.validate_on_submit():
            handle_form_errors(form)
            return render_template(self.templates.edit, form=form, entity=entity)

        form.populate_obj(entity)
        db.session.commit()

        return crud_response(
            success=True,
            message=f'{self.model.__name__} updated successfully!',
            redirect_url=url_for(f'crm.{self.name}_list')
        )

    @login_required
    @error_handler
    def delete(self, entity_id: int) -> Union[Response, WerkzeugResponse]:
        """Handle entity deletion.

        Args:
            entity_id: ID of the entity to delete.

        Returns:
            Redirect to list view after successful deletion.
        """
        entity = self.model.query.filter_by(
            id=entity_id,
            user_id=current_user.id
        ).first_or_404()

        db.session.delete(entity)
        db.session.commit()

        return crud_response(
            success=True,
            message=f'{self.model.__name__} deleted successfully!',
            redirect_url=url_for(f'crm.{self.name}_list')
        )

    @login_required
    def list(self) -> str:
        """Handle entity listing with pagination.

        Returns:
            Rendered template with paginated entity list.
        """
        page = request.args.get('page', 1, type=int)
        query = self.model.query.filter_by(user_id=current_user.id)

        # Apply filters from request args
        for key, value in request.args.items():
            if hasattr(self.model, key) and value:
                query = query.filter(getattr(self.model, key) == value)

        entities = query.paginate(page=page, per_page=10)
        return render_template(self.templates.list, entities=entities)

    @login_required
    def view(self, entity_id: int) -> str:
        """Handle entity detail view.

        Args:
            entity_id: ID of the entity to view.

        Returns:
            Rendered template with entity details.
        """
        entity = self.model.query.filter_by(
            id=entity_id,
            user_id=current_user.id
        ).first_or_404()

        return render_template(self.templates.view, entity=entity)

    def get_routes(self, url_prefix: str = '') -> List[RouteConfig]:
        """Generate route configurations for this handler.

        Args:
            url_prefix: Optional URL prefix for all routes.

        Returns:
            List of RouteConfig instances for registration.
        """
        name = self.name
        prefix = f'{url_prefix}/{name}' if url_prefix else name

        return [
            RouteConfig(f'{prefix}/add', f'add_{name}', self.create, ['GET', 'POST']),
            RouteConfig(f'{prefix}/<int:entity_id>/edit', f'edit_{name}', self.update, ['GET', 'POST']),
            RouteConfig(f'{prefix}/<int:entity_id>/delete', f'delete_{name}', self.delete, ['POST']),
            RouteConfig(f'{prefix}', f'{name}_list', self.list, ['GET']),
            RouteConfig(f'{prefix}/<int:entity_id>', f'view_{name}', self.view, ['GET']),
        ]


def register_crud_routes(
    blueprint: Any,
    model_class: type,
    form_class: type,
    url_prefix: str = '',
    templates: Optional[Templates] = None
) -> None:
    """Register all CRUD routes for a model.

    Args:
        blueprint: Flask blueprint to register routes on.
        model_class: SQLAlchemy model class.
        form_class: WTForms form class.
        url_prefix: Optional URL prefix for all routes.
        templates: Optional custom template configuration.
    """
    handler = CRUDHandler(model_class, form_class, templates)

    for route in handler.get_routes(url_prefix):
        blueprint.add_url_rule(
            route.url,
            route.endpoint,
            route.handler,
            methods=route.methods
        )