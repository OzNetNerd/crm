"""
Entity management utilities and configurations.
"""

from .entity_manager import (
    EntityManager,
    StakeholderManager,
    TeamManager,
    TaskEntityManager,
    get_entities_for_forms,
    assign_stakeholder_role,
    get_entity_tasks
)

from .entity_icons import (
    get_entity_icon_name,
    get_icon_function_name,
    get_entity_icon_html,
    get_entity_semantic,
    get_dashboard_entities,
    generate_entity_buttons
)

from .entity_config import (
    EntityConfigGenerator
)

__all__ = [
    'EntityManager',
    'StakeholderManager',
    'TeamManager',
    'TaskEntityManager',
    'get_entities_for_forms',
    'assign_stakeholder_role',
    'get_entity_tasks',
    'get_entity_icon_name',
    'get_icon_function_name', 
    'get_entity_icon_html',
    'get_entity_semantic',
    'get_dashboard_entities',
    'generate_entity_buttons',
    'EntityConfigGenerator'
]