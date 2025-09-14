"""
Generic web routes for all entities - DRY approach eliminating route duplication.
Handles companies, stakeholders, opportunities, teams with single codebase.
"""

from flask import Blueprint
from app.models import Company, Stakeholder, Opportunity, User

# Create blueprint for generic entity routes
entities_web_bp = Blueprint("entities", __name__)

# Dynamic entity mapping - DRY approach using model configuration
def get_web_entities():
    """Build WEB_ENTITIES dynamically from model configurations"""
    entities = {}
    models = [Company, Stakeholder, Opportunity, User]

    for model in models:
        config = model.get_entity_config()
        if config.get('show_dashboard_button', True):
            endpoint = config['entity_endpoint']
            entities[endpoint] = {
                'model': model,
                'filter_fields': config.get('filter_fields', []),
                'join_map': config.get('join_map', {})
            }

    return entities

# Get entities dynamically from model configurations
WEB_ENTITIES = get_web_entities()


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