"""
Route utilities package.

Contains helpers for route generation using DRY principles.
"""

from .helpers import build_dropdown_configs, calculate_entity_stats, build_entity_buttons

__all__ = [
    'build_dropdown_configs',
    'calculate_entity_stats',
    'build_entity_buttons'
]