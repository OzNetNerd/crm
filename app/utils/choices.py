"""
Pure Model-Driven Choice Provider

Uses model introspection exclusively to provide form choices and configuration.
Models are the single source of truth for ALL UI behavior, choices, CSS classes, and grouping.
No hardcoded choices or backward compatibility functions.
"""

from typing import Dict, List, Tuple, Any
from app.utils.model_introspection import ModelIntrospector, get_model_by_name


def parse_field_type(field_type: str) -> Tuple[str, str]:
    """
    Parse field type string to extract model name and field name.
    
    Args:
        field_type: String like 'opportunity_stage', 'task_priority', 'company_industry'
        
    Returns:
        Tuple of (model_name, field_name)
    """
    # Handle special mappings for non-standard naming
    field_mappings = {
        'note_entity_type': ('note', 'entity_type'),  # If we add a Note model
        'meddpicc_role': ('stakeholder', 'meddpicc_role'),  # If we add this field
        'stakeholder_role': ('stakeholder', 'role'),
        'team_role': ('user', 'team_role'),  # If we add this field
        'access_level': ('user', 'access_level'),  # If we add this field
    }
    
    if field_type in field_mappings:
        return field_mappings[field_type]
    
    # Split on underscore: first part is model name, rest is field name
    parts = field_type.split('_')
    if len(parts) >= 2:
        model_name = parts[0]
        field_name = '_'.join(parts[1:])
        return model_name, field_name
    
    return field_type, field_type


def get_choices_for_field(field_type: str) -> List[Tuple[str, str]]:
    """
    Get form choices for any field type using pure model introspection.
    
    Args:
        field_type: The type of field (e.g., 'opportunity_stage', 'task_priority')
        
    Returns:
        List of (value, label) tuples for form choices
    """
    model_name, field_name = parse_field_type(field_type)
    model_class = get_model_by_name(model_name)
    
    if not model_class:
        return []
    
    # Get choices from model introspection
    choices = ModelIntrospector.get_field_choices(model_class, field_name)
    
    # Check if field is marked as optional in metadata
    column = getattr(model_class, field_name, None)
    if column and hasattr(column.property, 'columns'):
        info = column.property.columns[0].info
        if info.get('optional', False):
            empty_label = info.get('empty_label', 'Select option')
            return [("", empty_label)] + choices
    
    return choices


def get_color_for_value(field_type: str, value: str) -> str:
    """
    Get color mapping for a field value using model introspection.
    
    Args:
        field_type: The type of field
        value: The field value
        
    Returns:
        Color name for CSS classes
    """
    model_name, field_name = parse_field_type(field_type)
    model_class = get_model_by_name(model_name)
    
    if not model_class:
        return 'gray'
    
    css_class = ModelIntrospector.get_field_css_class(model_class, field_name, value)
    
    # Extract color from CSS class (e.g., 'status-prospect' -> 'prospect')
    if css_class and '-' in css_class:
        return css_class.split('-')[-1]
    
    return 'gray'


def calculate_opportunity_priority(value: float) -> str:
    """Calculate priority based on opportunity value using model metadata"""
    from app.models import Opportunity
    
    # Get priority ranges from model metadata
    value_column = getattr(Opportunity, 'value', None)
    if not value_column or not hasattr(value_column.property, 'columns'):
        return 'low'
    
    info = value_column.property.columns[0].info
    priority_ranges = info.get('priority_ranges', [])
    
    if not value:
        return 'low'
    
    # priority_ranges is array of [min_value, priority, label, css_class]
    for min_val, priority, label, css_class in priority_ranges:
        if value >= min_val:
            return priority
    
    return 'low'


def get_active_opportunity_stages() -> List[str]:
    """Get stages that represent active opportunities from model metadata"""
    from app.models import Opportunity
    
    choices = ModelIntrospector.get_field_choices_with_metadata(Opportunity, 'stage')
    
    # Find stages that don't include 'closed' in the key or are explicitly marked as active
    active_stages = []
    for key, config in choices.items():
        if config.get('is_active', 'closed' not in key):
            active_stages.append(key)
    
    return active_stages


def get_closed_opportunity_stages() -> List[str]:
    """Get stages that represent closed opportunities from model metadata"""
    from app.models import Opportunity
    
    choices = ModelIntrospector.get_field_choices_with_metadata(Opportunity, 'stage')
    
    # Find stages that include 'closed' in the key or are explicitly marked as closed
    closed_stages = []
    for key, config in choices.items():
        if config.get('is_closed', 'closed' in key):
            closed_stages.append(key)
    
    return closed_stages


def get_active_task_statuses() -> List[str]:
    """Get statuses that represent active tasks from model metadata"""
    from app.models import Task
    
    choices = ModelIntrospector.get_field_choices_with_metadata(Task, 'status')
    
    # Find statuses that don't include 'complete' in the key or are explicitly marked as active
    active_statuses = []
    for key, config in choices.items():
        if config.get('is_active', 'complete' not in key):
            active_statuses.append(key)
    
    return active_statuses