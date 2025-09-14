"""
Simple helper functions - no abstraction, just utilities.
"""

from flask import request


def get_dropdowns_from_columns(model_class):
    """
    Build dropdown configs from model columns with groupable/sortable info.

    Args:
        model_class: SQLAlchemy model class

    Returns:
        Dict with dropdown configurations
    """
    dropdowns = {}

    # Get current request params
    current_group_by = request.args.get('group_by', '')
    current_sort_by = request.args.get('sort_by', '')
    current_sort_direction = request.args.get('sort_direction', 'asc')

    # Build options from column info metadata
    groupable_options = []
    sortable_options = []

    for column in model_class.__table__.columns:
        column_info = getattr(column, 'info', {})
        label = column_info.get('display_label', column.name.replace('_', ' ').title())

        if column_info.get('groupable'):
            groupable_options.append({'value': column.name, 'label': label})

        if column_info.get('sortable') or column.name in ['created_at', 'name', 'id']:
            sortable_options.append({'value': column.name, 'label': label})

    # Add dropdowns if we have options
    if groupable_options:
        dropdowns['group_by'] = {
            'options': groupable_options,
            'current_value': current_group_by,
            'placeholder': 'Group by...',
            'multiple': False,
            'searchable': True
        }

    if sortable_options:
        dropdowns['sort_by'] = {
            'options': sortable_options,
            'current_value': current_sort_by,
            'placeholder': 'Sort by...',
            'multiple': False,
            'searchable': True
        }

    # Always add sort direction
    dropdowns['sort_direction'] = {
        'options': [
            {'value': 'asc', 'label': 'Ascending'},
            {'value': 'desc', 'label': 'Descending'}
        ],
        'current_value': current_sort_direction,
        'placeholder': 'Order',
        'multiple': False,
        'searchable': True
    }

    return dropdowns