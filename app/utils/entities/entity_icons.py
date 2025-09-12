"""
Entity Configuration - Clean Python approach
Python only passes entity names, Jinja handles CSS class generation
"""

def get_dashboard_buttons():
    """
    Generate dashboard buttons - Python just passes entity names
    Jinja handles icon names and CSS class concatenation
    
    Returns:
        list: Simple button configurations with just entity names
    """
    # Import here to avoid circular imports
    from app.models import Task, Company, Stakeholder, Opportunity, User
    
    # Get entity configs from models
    entities = [
        (Task, 'Task'),
        (Company, 'Company'), 
        (Stakeholder, 'Stakeholder'),
        (Opportunity, 'Opportunity'),
        (User, 'User')
    ]
    
    buttons = []
    for model_class, entity_class_name in entities:
        entity_config = getattr(model_class, '__entity_config__', {})
        
        # Use entity config if available, otherwise fall back to class name
        if entity_config:
            label = f"New {entity_config.get('display_name_singular', entity_class_name)}"
            modal_path = entity_config.get('modal_path', f'/modals/{entity_class_name}')
            endpoint_name = entity_config.get('endpoint_name', entity_class_name.lower())
        else:
            label = f"New {entity_class_name}"
            modal_path = f'/modals/{entity_class_name}'
            endpoint_name = entity_class_name.lower()
        
        button = {
            'label': label,
            'hx_get': f'{modal_path}/create',
            'hx_target': 'body',
            'hx_swap': 'beforeend',
            'entity_type': endpoint_name  # Just the entity name - Jinja handles the rest
        }
        buttons.append(button)
    
    return buttons

# Keep get_dashboard_entities as alias for backwards compatibility
def get_dashboard_entities():
    return get_dashboard_buttons()