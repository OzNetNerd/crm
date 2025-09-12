"""
Entity to Icon Mapping Utility - Single Source of Truth for DRY Button System
Centralized mapping system for all CRM entities, their icons, and button generation
"""

from typing import Dict, List, Any, Optional

# Entity semantic categories - colors now defined in CSS custom properties
ENTITY_SEMANTICS = {
    'task': 'work',
    'company': 'growth', 
    'opportunity': 'revenue',
    'stakeholder': 'people',
    'teams': 'management',
    'user': 'management'
}

# Entity to icon name mapping - supports both string icon names and model entity configs  
ENTITY_ICON_MAPPING = {
    # Direct entity class names
    'Company': 'building-office',
    'Stakeholder': 'user', 
    'Opportunity': 'currency-dollar',
    'Task': 'clipboard-list',
    'User': 'user',  # Individual user/team member
    
    # Entity plural names (for routes/endpoints)  
    'companies': 'building-office',
    'stakeholders': 'user',
    'opportunities': 'currency-dollar', 
    'tasks': 'clipboard-list',
    'teams': 'users',  # Teams page uses plural users icon
    
    # Icon string names from model __entity_config__
    'building-office': 'building-office',
    'user': 'user',
    'users': 'users', 
    'currency-dollar': 'currency-dollar',
    'clipboard-list': 'clipboard-list'
}

# Icon to macro function mapping
ICON_FUNCTION_MAPPING = {
    'building-office': 'building_office_icon',
    'user': 'user_icon',
    'users': 'users_icon',  # Note: This needs to exist in icons.html
    'currency-dollar': 'currency_dollar_icon', 
    'clipboard-list': 'clipboard_list_icon',
    'plus': 'plus_icon'
}

# Icon size mapping for different contexts
ICON_SIZE_MAPPING = {
    'button': 'w-4 h-4',
    'metric': 'w-6 h-6', 
    'header': 'w-5 h-5',
    'small': 'w-3 h-3'
}

def get_entity_icon_name(entity_identifier):
    """
    Get icon name for any entity identifier
    
    Args:
        entity_identifier (str): Entity name, plural name, or icon name
    
    Returns:
        str: Standardized icon name
    """
    return ENTITY_ICON_MAPPING.get(entity_identifier, 'plus')

def get_icon_function_name(icon_name):
    """
    Get the macro function name for an icon
    
    Args:
        icon_name (str): Icon name (e.g., 'building-office', 'user')
    
    Returns:  
        str: Macro function name (e.g., 'building_office_icon')
    """
    return ICON_FUNCTION_MAPPING.get(icon_name, 'plus_icon')

def get_entity_icon_html(entity_identifier, size='button'):
    """
    Generate icon HTML for templates using Jinja2 rendering
    
    Args:
        entity_identifier (str): Entity name, plural, or icon name
        size (str): Size context ('button', 'metric', 'header', 'small')
    
    Returns:
        str: Rendered icon HTML
    """
    from flask import render_template_string
    
    icon_name = get_entity_icon_name(entity_identifier)
    function_name = get_icon_function_name(icon_name)
    size_class = ICON_SIZE_MAPPING.get(size, 'w-4 h-4')
    
    # Render the icon using Jinja2
    icon_template = f"""
    {{% from "macros/base/icons.html" import {function_name} %}}
    {{{{ {function_name}('{size_class}') }}}}
    """
    
    try:
        return render_template_string(icon_template.strip())
    except:
        # Fallback to plus icon if specific icon fails
        fallback_template = f"""
        {{% from "macros/base/icons.html" import plus_icon %}}
        {{{{ plus_icon('{size_class}') }}}}
        """
        return render_template_string(fallback_template.strip())

def generate_entity_buttons(entities_config, context='dashboard'):
    """
    Generate standardized buttons for multiple entities
    
    Args:
        entities_config (list): List of entity configurations or entity names
        context (str): Context for button generation ('dashboard', 'page', 'quick_actions')
    
    Returns:
        list: List of standardized button configurations
    """
    buttons = []
    
    for entity_config in entities_config:
        if isinstance(entity_config, str):
            # Simple entity name - need to get model config
            entity_name = entity_config
            # This would need to be enhanced to look up model configs
            button = {
                'label': f'New {entity_name.title()}',
                'hx_get': f'/modals/{entity_name.title()}/create',
                'hx_target': 'body', 
                'hx_swap': 'beforeend',
                'icon': get_entity_icon_html(entity_name),
                'classes': f'btn-entity-{entity_name.lower()}'
            }
        else:
            # Full entity configuration dict
            icon_name = entity_config.get('icon', 'plus')
            button = {
                'label': f"New {entity_config.get('display_name_singular', 'Item')}",
                'hx_get': f"{entity_config.get('modal_path', '/modals/Item')}/create",
                'hx_target': 'body',
                'hx_swap': 'beforeend',
                'icon': get_entity_icon_html(icon_name),
                'classes': f"btn-entity-{entity_config.get('endpoint_name', 'item')}"
            }
        
        buttons.append(button)
    
    return buttons

def get_entity_semantic(entity_identifier):
    """
    Get semantic category for an entity (colors now in CSS)
    
    Args:
        entity_identifier (str): Entity name, plural, or endpoint name
        
    Returns:
        str: Semantic category name
    """
    # Normalize entity identifier to lowercase
    entity_key = entity_identifier.lower()
    
    # Direct lookup
    if entity_key in ENTITY_SEMANTICS:
        return ENTITY_SEMANTICS[entity_key]
    
    # Fallback to default
    return 'default'


def get_dashboard_buttons():
    """
    Generate all dashboard buttons using model configurations with color system integration
    
    Returns:
        list: Complete dashboard button configuration with enhanced styling
    """
    # Import here to avoid circular imports
    from app.models import Task, Company, Stakeholder, Opportunity, User
    
    # Get entity configs from models
    entities = [
        (Task, 'Task'),
        (Company, 'Company'), 
        (Stakeholder, 'Stakeholder'),
        (Opportunity, 'Opportunity'),
        (User, 'User')  # Team Member
    ]
    
    buttons = []
    for model_class, entity_class_name in entities:
        entity_config = getattr(model_class, '__entity_config__', {})
        
        # Use entity config if available, otherwise fall back to class name
        if entity_config:
            icon_name = entity_config.get('icon', entity_class_name)
            label = f"New {entity_config.get('display_name_singular', entity_class_name)}"
            modal_path = entity_config.get('modal_path', f'/modals/{entity_class_name}')
            endpoint_name = entity_config.get('endpoint_name', entity_class_name.lower())
            classes = f"btn-entity-{endpoint_name}"
        else:
            icon_name = entity_class_name
            label = f"New {entity_class_name}"
            modal_path = f'/modals/{entity_class_name}'
            endpoint_name = entity_class_name.lower()
            classes = f'btn-entity-{endpoint_name}'
        
        # Get semantic category for this entity
        semantic = get_entity_semantic(endpoint_name)
        
        button = {
            'label': label,
            'hx_get': f'{modal_path}/create',
            'hx_target': 'body',
            'hx_swap': 'beforeend',
            'icon': get_entity_icon_html(icon_name),
            'classes': classes,
            'entity_type': endpoint_name,  # For debugging/identification
            'semantic': semantic  # Semantic category instead of hex colors
        }
        buttons.append(button)
    
    return buttons