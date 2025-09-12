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

# Entity icons now use dynamic CSS classes via Jinja: icon-{entity_name}


__all__ = [
    'EntityManager',
    'StakeholderManager',
    'TeamManager',
    'TaskEntityManager',
    'get_entities_for_forms',
    'assign_stakeholder_role',
    'get_entity_tasks',
]