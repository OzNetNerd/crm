"""
Entity management utilities and configurations.
"""

from .entity_manager import (
    EntityManager,
    StakeholderManager,
    TeamManager,
    TaskEntityManager
)

# Entity icons now use dynamic CSS classes via Jinja: icon-{entity_name}


__all__ = [
    'EntityManager',
    'StakeholderManager',
    'TeamManager',
    'TaskEntityManager'
]