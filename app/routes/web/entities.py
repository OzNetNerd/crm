"""
Generic web routes for all entities - DRY approach eliminating route duplication.
Handles companies, stakeholders, opportunities, teams with single codebase.
"""

from flask import Blueprint
from app.models import Company, Stakeholder, Opportunity, User

# Create blueprint for generic entity routes
entities_web_bp = Blueprint("entities", __name__)

# Entity mapping - same as API but for web routes
WEB_ENTITIES = {
    'companies': {
        'model': Company,
        'filter_fields': ['industry', 'size'],
        'join_map': {}
    },
    'stakeholders': {
        'model': Stakeholder,
        'filter_fields': ['company_id', 'job_title'],
        'join_map': {'company_name': [Company]}
    },
    'opportunities': {
        'model': Opportunity,
        'filter_fields': ['company_id', 'stage', 'priority'],
        'join_map': {'company_name': [Company]}
    },
    'teams': {
        'model': User,
        'filter_fields': ['job_title', 'department'],
        'join_map': {}
    }
}


def create_web_route_handlers():
    """Create web route handlers for all entities - DRY approach"""

    def make_index_handler(entity_name):
        def handler():
            model = WEB_ENTITIES[entity_name]['model']
            return model.render_index()
        return handler

    def make_content_handler(entity_name):
        def handler():
            entity_config = WEB_ENTITIES[entity_name]
            model = entity_config['model']
            return model.render_content(
                filter_fields=entity_config['filter_fields'],
                join_map=entity_config['join_map']
            )
        return handler

    # Register routes for all entities
    for entity_name in WEB_ENTITIES:
        # Main index route
        entities_web_bp.add_url_rule(
            f'/{entity_name}',
            f'{entity_name}_index',
            make_index_handler(entity_name)
        )

        # HTMX content route
        entities_web_bp.add_url_rule(
            f'/{entity_name}/content',
            f'{entity_name}_content',
            make_content_handler(entity_name)
        )


# Register all entity routes
create_web_route_handlers()