"""
Universal Route Factory - DRY solution for entity route creation.

This module provides a factory pattern to eliminate the verbose duplication
in web route files by leveraging the EntityModel ABC system for automatic
route generation.
"""

from flask import Blueprint, render_template
from app.utils.core.base_handlers import BaseRouteHandler, EntityFilterManager
from app.utils.core.entity_handlers import (
    UniversalEntityManager,
    CompanyHandler,
    OpportunityHandler,
    StakeholderHandler,
    TeamHandler,
    TaskHandler
)
from app.utils.ui.index_helpers import UniversalIndexHelper


class UniversalRouteFactory:
    """Factory for creating standardized entity routes using EntityModel ABC"""

    @staticmethod
    def create_entity_blueprint(model_class):
        """
        Create a complete entity blueprint using EntityModel configuration.

        This replaces 50+ lines of boilerplate per entity with automatic
        route generation based on __entity_config__.

        Args:
            model_class: EntityModel subclass with __entity_config__

        Returns:
            Configured Flask Blueprint with standard routes
        """
        config = model_class.__entity_config__
        endpoint_name = config['endpoint_name']
        entity_name = model_class.__name__.lower()

        # Create blueprint
        blueprint = Blueprint(endpoint_name, __name__)

        # Create universal managers - exactly like the verbose files
        route_handler = BaseRouteHandler(model_class, endpoint_name)
        entity_manager = UniversalEntityManager(model_class, _get_entity_handler(model_class))
        filter_manager = EntityFilterManager(model_class, entity_name)

        # Create wrapper functions - exactly like verbose files
        def custom_filters(query, filters):
            return entity_manager.apply_custom_filters(query, filters)

        def custom_groupers(entities, group_by):
            return entity_manager.apply_custom_grouping(entities, group_by)

        def custom_sorting(query, sort_by, sort_direction):
            return entity_manager.apply_custom_sorting(query, sort_by, sort_direction)

        # Define routes
        @blueprint.route("/content")
        def content():
            """HTMX endpoint for filtered entity content - DRY version"""
            # Determine if we need joins (for entities with company relationships)
            joins = None
            if hasattr(model_class, 'company_id'):  # Has company relationship
                from app.models import Company
                joins = [Company]

            context = filter_manager.get_content_context(
                custom_filters=custom_filters,
                custom_sorting=custom_sorting,
                custom_grouper=custom_groupers,
                joins=joins
            )

            return render_template("shared/entity_content.html", **context)

        # Note: Index routes are left for custom implementation per entity

        return blueprint


def _get_default_group_by(model_class):
    """Get sensible default group_by field for entity"""
    # Map entity types to their logical grouping fields
    defaults = {
        'Company': 'industry',
        'Opportunity': 'stage',
        'Task': 'status',
        'Stakeholder': 'job_title',
        'User': 'job_title'
    }
    return defaults.get(model_class.__name__, 'default')


def _get_entity_handler(model_class):
    """Get the appropriate handler for each model class"""
    handler_map = {
        'Company': CompanyHandler(),
        'Opportunity': OpportunityHandler(),
        'Stakeholder': StakeholderHandler(),
        'Task': TaskHandler(),
        'User': TeamHandler()  # Teams use User model with TeamHandler
    }
    return handler_map.get(model_class.__name__)


def create_entity_blueprint(model_class):
    """
    Public factory function to create entity blueprints.

    Usage in route files:
        from app.utils.routes import create_entity_blueprint
        companies_bp = create_entity_blueprint(Company)
    """
    return UniversalRouteFactory.create_entity_blueprint(model_class)


def add_content_route(blueprint, model_class):
    """
    Add just the /content route to existing blueprint.

    For cases where you want to keep custom index but DRY the content route.

    Usage:
        companies_bp = Blueprint("companies", __name__)
        add_content_route(companies_bp, Company)
    """
    config = model_class.__entity_config__
    entity_name = model_class.__name__.lower()

    # Create managers with shared handler for DRY consistency
    entity_handler = _get_entity_handler(model_class)
    entity_manager = UniversalEntityManager(model_class, entity_handler)
    filter_manager = EntityFilterManager(model_class, entity_name, entity_handler)

    # Create wrapper functions
    def custom_filters(query, filters):
        return entity_manager.apply_custom_filters(query, filters)

    def custom_groupers(entities, group_by):
        return entity_manager.apply_custom_grouping(entities, group_by)

    def custom_sorting(query, sort_by, sort_direction):
        return entity_manager.apply_custom_sorting(query, sort_by, sort_direction)

    @blueprint.route("/content")
    def content():
        """HTMX endpoint for filtered entity content - DRY version"""
        # Determine if we need joins
        joins = None
        if hasattr(model_class, 'company_id'):
            from app.models import Company
            joins = [Company]

        context = filter_manager.get_content_context(
            custom_filters=custom_filters,
            custom_sorting=custom_sorting,
            custom_grouper=custom_groupers,
            joins=joins
        )

        return render_template("shared/entity_content.html", **context)