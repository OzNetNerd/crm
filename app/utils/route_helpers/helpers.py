"""
Route Helper Functions

Helpers to generate dropdown configs and entity stats using existing model metadata.
"""

from flask import request
from typing import Dict, List, Any


def build_dropdown_configs(model_class) -> Dict[str, Any]:
    """
    Build dropdown configurations using existing model column info metadata.

    Uses column info={'groupable': True, 'choices': {...}} to generate
    dropdowns with proper validation structure.

    Args:
        model_class: SQLAlchemy model class with column info metadata

    Returns:
        Dict with dropdown configs including required validation fields
    """
    dropdown_configs = {}

    # Get current request parameters
    current_group_by = request.args.get('group_by', '')
    current_sort_by = request.args.get('sort_by', '')
    current_sort_direction = request.args.get('sort_direction', 'asc')

    # Build group_by dropdown from groupable fields
    groupable_options = []
    sortable_options = []

    # Iterate through model columns to find groupable/sortable fields
    for column in model_class.__table__.columns:
        column_info = getattr(column, 'info', {})

        if column_info.get('groupable'):
            label = column_info.get('display_label', column.name.replace('_', ' ').title())
            groupable_options.append({'value': column.name, 'label': label})

        if column_info.get('sortable') or column.name in ['created_at', 'name', 'id']:
            label = column_info.get('display_label', column.name.replace('_', ' ').title())
            sortable_options.append({'value': column.name, 'label': label})

    # Add name/title as sortable by default if exists
    if hasattr(model_class, 'name') and not any(opt['value'] == 'name' for opt in sortable_options):
        sortable_options.append({'value': 'name', 'label': 'Name'})

    # Group by dropdown
    if groupable_options:
        dropdown_configs['group_by'] = {
            'options': groupable_options,
            'current_value': current_group_by,
            'placeholder': 'Group by...',
            'multiple': False,
            'searchable': True
        }

    # Sort by dropdown
    if sortable_options:
        dropdown_configs['sort_by'] = {
            'options': sortable_options,
            'current_value': current_sort_by,
            'placeholder': 'Sort by...',
            'multiple': False,
            'searchable': True
        }

    # Sort direction dropdown
    dropdown_configs['sort_direction'] = {
        'options': [
            {'value': 'asc', 'label': 'Ascending'},
            {'value': 'desc', 'label': 'Descending'}
        ],
        'current_value': current_sort_direction,
        'placeholder': 'Order',
        'multiple': False,
        'searchable': True
    }

    return dropdown_configs


def build_entity_buttons(model_class) -> List[Dict[str, str]]:
    """
    Build entity buttons using model configuration.

    Creates properly formatted button dictionaries for validation compliance.

    Args:
        model_class: SQLAlchemy model class with __entity_config__

    Returns:
        List of button dictionaries with title and url
    """
    config = getattr(model_class, '__entity_config__', {})
    display_name_singular = config.get('display_name_singular', model_class.__name__)
    modal_path = config.get('modal_path', f'/modals/{model_class.__name__}')

    return [
        {
            'title': f'New {display_name_singular}',
            'url': f'{modal_path}/create'
        }
    ]


def calculate_entity_stats(model_class) -> Dict[str, Any]:
    """
    Calculate entity stats using existing model methods and data.

    Uses model.query.all() and existing model methods like calculate_sum,
    get_recent, etc. to generate stats.

    Args:
        model_class: SQLAlchemy model class

    Returns:
        Dict with title and stats array for entity overview
    """
    # Get all entities
    entities = model_class.query.all()
    total_count = len(entities)

    # Get entity config for display names
    config = getattr(model_class, '__entity_config__', {})
    display_name = config.get('display_name', f'{model_class.__name__}s')

    # Base stats - always include total count
    stats = [
        {
            'value': total_count,
            'label': f'Total {display_name}'
        }
    ]

    # Entity-specific stats based on common patterns
    if hasattr(model_class, 'status'):
        # Count by status if status field exists
        status_counts = {}
        for entity in entities:
            status = getattr(entity, 'status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        for status, count in status_counts.items():
            stats.append({
                'value': count,
                'label': status.replace('-', ' ').replace('_', ' ').title()
            })

    elif hasattr(model_class, 'stage'):
        # Count by stage if stage field exists (opportunities)
        stage_counts = {}
        for entity in entities:
            stage = getattr(entity, 'stage', 'unknown')
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

        # Show won/closed stats for opportunities
        stats.append({
            'value': stage_counts.get('closed-won', 0),
            'label': 'Closed Won'
        })

    # Add contact info stats for stakeholders
    if hasattr(model_class, 'email') and hasattr(model_class, 'phone'):
        with_email = len([e for e in entities if getattr(e, 'email')])
        with_phone = len([e for e in entities if getattr(e, 'phone')])

        stats.extend([
            {'value': with_email, 'label': 'With Email'},
            {'value': with_phone, 'label': 'With Phone'}
        ])

    # Add relationship stats if company_id exists
    if hasattr(model_class, 'company_id'):
        unique_companies = len(set(getattr(e, 'company_id') for e in entities if getattr(e, 'company_id')))
        stats.append({
            'value': unique_companies,
            'label': 'Companies Represented'
        })

    return {
        'title': f'{display_name} Overview',
        'stats': stats
    }