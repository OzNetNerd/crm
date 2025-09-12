from flask import Blueprint
from app.models import Company, Stakeholder, Opportunity
from app.utils.core.base_handlers import NotesAPIHandler

api_notes_bp = Blueprint("api_notes", __name__, url_prefix="/api")

# Define entity configurations for notes
NOTE_ENTITY_CONFIGS = {
    "companies": {
        "model": Company,
        "entity_name": "company",
        "route_param": "company_id",
    },
    "contacts": {
        "model": Stakeholder, 
        "entity_name": "contact",
        "route_param": "contact_id",
    },
    "opportunities": {
        "model": Opportunity,
        "entity_name": "opportunity", 
        "route_param": "opportunity_id",
    },
}

# Dynamically register GET and POST endpoints for notes
for entity_plural, config in NOTE_ENTITY_CONFIGS.items():
    handler = NotesAPIHandler(config["model"], config["entity_name"])
    route_param = config["route_param"]
    
    # Create GET endpoint function with proper closure
    def make_get_endpoint(handler_func, param_name):
        def endpoint(**kwargs):
            entity_id = kwargs[param_name]
            return handler_func(entity_id)
        return endpoint
    
    get_endpoint_func = make_get_endpoint(handler.get_notes, route_param)
    get_endpoint_func.__name__ = f"get_{config['entity_name']}_notes"
    get_endpoint_func.__doc__ = f"Get all notes for a specific {config['entity_name']}"
    
    api_notes_bp.route(f"/{entity_plural}/<int:{route_param}>/notes", methods=["GET"])(get_endpoint_func)
    
    # Create POST endpoint function with proper closure
    def make_post_endpoint(handler_func, param_name):
        def endpoint(**kwargs):
            entity_id = kwargs[param_name]
            return handler_func(entity_id)
        return endpoint
    
    post_endpoint_func = make_post_endpoint(handler.create_note, route_param)
    post_endpoint_func.__name__ = f"create_{config['entity_name']}_note"
    post_endpoint_func.__doc__ = f"Create a new note for a specific {config['entity_name']}"
    
    api_notes_bp.route(f"/{entity_plural}/<int:{route_param}>/notes", methods=["POST"])(post_endpoint_func)