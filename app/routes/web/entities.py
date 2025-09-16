"""
Web routes for CRM entities - Dynamic and DRY.
"""

from flask import Blueprint, render_template, request
from collections import defaultdict
from app.models import db, MODEL_REGISTRY

entities_web_bp = Blueprint("entities", __name__)


def build_dropdowns(model, request_args):
    """Build all dropdown configurations for filters and sorting."""
    metadata = model.get_field_metadata()
    dropdowns = {}

    # Add filter dropdowns for fields with choices
    for field_name, field_info in metadata.items():
        if field_info.get('filterable') and field_info.get('choices'):
            options = [{'value': '', 'label': f'All {field_info["label"]}'}]
            options.extend([
                {'value': choice_val, 'label': choice_data.get('label', choice_val)}
                for choice_val, choice_data in field_info['choices'].items()
            ])

            dropdowns[f'filter_{field_name}'] = {
                'name': field_name,
                'label': f'Filter by {field_info["label"]}',
                'options': options,
                'current_value': request_args.get(field_name, ''),
                'placeholder': f'All {field_info["label"]}',
                'multiple': False,
                'searchable': False
            }

    # Add group-by dropdown if groupable fields exist
    groupable = [
        {'value': name, 'label': info['label']}
        for name, info in metadata.items()
        if info.get('groupable')
    ]

    if groupable:
        dropdowns['group_by'] = {
            'options': groupable,
            'current_value': request_args.get('group_by', ''),
            'placeholder': 'Group by...',
            'multiple': False,
            'searchable': True
        }

    # Add sort dropdown
    sortable = [
        {'value': name, 'label': info['label']}
        for name, info in metadata.items()
        if info.get('sortable')
    ]

    if not any(field['value'] == 'id' for field in sortable):
        sortable.append({'value': 'id', 'label': 'ID'})

    dropdowns['sort_by'] = {
        'options': sortable,
        'current_value': request_args.get('sort_by', model.get_default_sort_field()),
        'placeholder': 'Sort by...',
        'multiple': False,
        'searchable': True
    }

    # Add sort direction dropdown
    dropdowns['sort_direction'] = {
        'options': [
            {'value': 'asc', 'label': 'Ascending'},
            {'value': 'desc', 'label': 'Descending'}
        ],
        'current_value': request_args.get('sort_direction', 'asc'),
        'placeholder': 'Order',
        'multiple': False,
        'searchable': False
    }

    return dropdowns


def get_entity_type(model):
    """Get entity type from MODEL_REGISTRY."""
    for entity_type, model_class in MODEL_REGISTRY.items():
        if model_class == model:
            return entity_type
    return model.__name__.lower()


def entity_index(model):
    """Generic index handler for all entities."""
    dropdown_configs = build_dropdowns(model, request.args)
    entity_type = get_entity_type(model)

    # Get basic stats
    display_name_plural = model.get_display_name_plural()
    total = model.query.count()
    stats = {
        'title': f'{display_name_plural} Overview',
        'stats': [{'value': total, 'label': f'Total {display_name_plural}'}]
    }

    # Add status breakdown if model has status field
    if hasattr(model, 'status'):
        from sqlalchemy import func
        status_counts = db.session.query(
            model.status,
            func.count(model.id)
        ).group_by(model.status).all()

        for status, count in status_counts:
            if status:
                label = status.replace('-', ' ').replace('_', ' ').title()
                stats['stats'].append({'value': count, 'label': label})

    entity_config = {
        'entity_type': entity_type,
        'entity_name': display_name_plural,
        'entity_name_singular': model.get_display_name(),
        'content_endpoint': f'entities.{model.__tablename__}_content',
        'entity_buttons': [{
            'title': f'New {model.get_display_name()}',
            'url': f'/modals/{entity_type}/create'
        }]
    }

    return render_template(
        "base/entity_index.html",
        entity_config=entity_config,
        dropdown_configs=dropdown_configs,
        entity_stats=stats
    )


def entity_content(model):
    """Generic content handler for all entities."""
    # Get params
    group_by = request.args.get('group_by', '')
    sort_by = request.args.get('sort_by', model.get_default_sort_field())
    sort_direction = request.args.get('sort_direction', 'asc')

    # Build query
    query = model.query

    # Handle sorting - simplified logic
    if hasattr(model, sort_by):
        sort_field = getattr(model, sort_by)
    else:
        sort_field = model.id

    # Apply filters from request args
    metadata = model.get_field_metadata()
    for field_name, field_info in metadata.items():
        if field_info.get('filterable'):
            filter_value = request.args.get(field_name)
            if filter_value and hasattr(model, field_name):
                query = query.filter(getattr(model, field_name) == filter_value)

    # Apply sorting
    if sort_direction == 'desc':
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    entities = query.all()

    # Group entities if requested
    if group_by and hasattr(model, group_by):
        grouped = defaultdict(list)
        for entity in entities:
            group_key = getattr(entity, group_by, 'Other') or 'Uncategorized'
            grouped[group_key].append(entity)

        grouped_entities = [
            {
                'key': group_key,
                'label': group_key,
                'count': len(group_items),
                'entities': group_items
            }
            for group_key, group_items in grouped.items()
        ]
    else:
        grouped_entities = [{
            'key': 'all',
            'label': 'All Results',
            'count': len(entities),
            'entities': entities
        }]

    entity_type = get_entity_type(model)

    return render_template(
        "shared/entity_content.html",
        grouped_entities=grouped_entities,
        group_by=group_by,
        total_count=len(entities),
        entity_type=entity_type,
        entity_name=model.get_display_name_plural(),
        entity_name_singular=model.get_display_name(),
        entity_name_plural=model.get_display_name_plural()
    )


# Register routes for all models
for entity_type, model in MODEL_REGISTRY.items():
    if not hasattr(model, 'is_web_enabled') or not model.is_web_enabled():
        continue

    table_name = model.__tablename__

    # Register main routes
    entities_web_bp.add_url_rule(
        f'/{table_name}',
        f'{table_name}_index',
        lambda m=model: entity_index(m)
    )

    entities_web_bp.add_url_rule(
        f'/{table_name}/content',
        f'{table_name}_content',
        lambda m=model: entity_content(m)
    )

    # Add alternate routes for users -> teams
    if entity_type == 'user':
        entities_web_bp.add_url_rule(
            '/teams',
            'teams_index',
            lambda m=model: entity_index(m)
        )
        entities_web_bp.add_url_rule(
            '/teams/content',
            'teams_content',
            lambda m=model: entity_content(m)
        )