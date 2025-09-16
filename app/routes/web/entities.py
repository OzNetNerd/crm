"""
Web routes for CRM entities - Clean and DRY.
"""

from flask import Blueprint, render_template, request
from collections import defaultdict
from sqlalchemy import func
from app.models import db, MODEL_REGISTRY

entities_web_bp = Blueprint("entities", __name__)


def make_dropdown(name, options, current_value='', placeholder='', searchable=False):
    """Create a dropdown configuration."""
    return {
        'name': name,
        'options': options,
        'current_value': current_value,
        'placeholder': placeholder,
        'multiple': False,
        'searchable': searchable
    }


def get_filter_options(field_info):
    """Convert field choices to dropdown options."""
    options = [{'value': '', 'label': f'All {field_info["label"]}'}]

    if not field_info.get('choices'):
        return options

    for val, data in field_info['choices'].items():
        options.append({'value': val, 'label': data.get('label', val)})

    return options


def get_field_options(metadata, filter_func):
    """Get field options based on filter function."""
    return [
        {'value': name, 'label': info['label']}
        for name, info in metadata.items()
        if filter_func(info)
    ]


def build_dropdowns(model, request_args):
    """Build dropdown configurations."""
    metadata = model.get_field_metadata()
    dropdowns = {}

    # Filter dropdowns
    for name, info in metadata.items():
        if not (info.get('filterable') and info.get('choices')):
            continue

        options = get_filter_options(info)
        dropdowns[f'filter_{name}'] = make_dropdown(
            name,
            options,
            request_args.get(name, ''),
            f'All {info["label"]}'
        )

    # Group dropdown
    groupable = get_field_options(metadata, lambda x: x.get('groupable'))
    if groupable:
        dropdowns['group_by'] = make_dropdown(
            'group_by',
            groupable,
            request_args.get('group_by', ''),
            'Group by...',
            searchable=True
        )

    # Sort dropdown
    sortable = get_field_options(metadata, lambda x: x.get('sortable'))
    if not any(f['value'] == 'id' for f in sortable):
        sortable.append({'value': 'id', 'label': 'ID'})

    dropdowns['sort_by'] = make_dropdown(
        'sort_by',
        sortable,
        request_args.get('sort_by', model.get_default_sort_field()),
        'Sort by...',
        searchable=True
    )

    # Direction dropdown
    dropdowns['sort_direction'] = make_dropdown(
        'sort_direction',
        [
            {'value': 'asc', 'label': 'Ascending'},
            {'value': 'desc', 'label': 'Descending'}
        ],
        request_args.get('sort_direction', 'asc'),
        'Order'
    )

    return dropdowns


def get_entity_type(model):
    """Get entity type from registry."""
    for entity_type, model_class in MODEL_REGISTRY.items():
        if model_class == model:
            return entity_type
    return model.__name__.lower()


def get_status_stats(model):
    """Get status breakdown stats."""
    if not hasattr(model, 'status'):
        return []

    counts = db.session.query(
        model.status,
        func.count(model.id)
    ).group_by(model.status).all()

    stats = []
    for status, count in counts:
        if status:
            label = status.replace('-', ' ').replace('_', ' ').title()
            stats.append({'value': count, 'label': label})

    return stats


def build_entity_config(model, entity_type):
    """Build entity configuration."""
    # Use __route_name__ if defined, otherwise use display_name_plural
    route_name = getattr(model, '__route_name__', model.get_display_name_plural().lower())
    return {
        'entity_type': entity_type,
        'entity_name': model.get_display_name_plural(),
        'entity_name_singular': model.get_display_name(),
        'route_path': f'/{route_name}',
        'content_endpoint': f'entities.{route_name}_content',
        'entity_buttons': [{
            'title': f'New {model.get_display_name()}',
            'url': f'/modals/{entity_type}/create'
        }]
    }


def entity_index(model):
    """Render entity index page."""
    entity_type = get_entity_type(model)

    # Build stats
    total = model.query.count()
    stats = {
        'title': f'{model.get_display_name_plural()} Overview',
        'stats': [{'value': total, 'label': f'Total {model.get_display_name_plural()}'}]
    }
    stats['stats'].extend(get_status_stats(model))

    return render_template(
        "base/entity_index.html",
        entity_config=build_entity_config(model, entity_type),
        dropdown_configs=build_dropdowns(model, request.args),
        entity_stats=stats
    )


def apply_filters(query, model, metadata):
    """Apply filters to query."""
    for name, info in metadata.items():
        if not info.get('filterable'):
            continue

        value = request.args.get(name)
        if value and hasattr(model, name):
            query = query.filter(getattr(model, name) == value)

    return query


def apply_sort(query, model):
    """Apply sorting to query."""
    sort_by = request.args.get('sort_by', model.get_default_sort_field())
    sort_dir = request.args.get('sort_direction', 'asc')

    sort_field = getattr(model, sort_by, model.id)

    if sort_dir == 'desc':
        return query.order_by(sort_field.desc())
    return query.order_by(sort_field.asc())


def group_entities(entities, model, group_by):
    """Group entities by field."""
    if not (group_by and hasattr(model, group_by)):
        return [{
            'key': 'all',
            'label': 'All Results',
            'count': len(entities),
            'entities': entities
        }]

    grouped = defaultdict(list)
    for entity in entities:
        key = getattr(entity, group_by, 'Other') or 'Uncategorized'
        grouped[key].append(entity)

    return [
        {'key': k, 'label': k, 'count': len(v), 'entities': v}
        for k, v in grouped.items()
    ]


def entity_content(model):
    """Render entity content."""
    # Get entities
    query = model.query
    query = apply_filters(query, model, model.get_field_metadata())
    query = apply_sort(query, model)
    entities = query.all()

    # Group if requested
    group_by = request.args.get('group_by', '')
    grouped_entities = group_entities(entities, model, group_by)

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


# Register routes
for entity_type, model in MODEL_REGISTRY.items():
    if not getattr(model, 'is_web_enabled', lambda: True)():
        continue

    config = build_entity_config(model, entity_type)
    route_path = config['route_path']

    # Use route name for endpoint (e.g., 'companies_index' not 'company_index')
    route_name = route_path[1:]  # Remove leading slash

    entities_web_bp.add_url_rule(
        route_path,
        f'{route_name}_index',
        lambda model=model: entity_index(model)
    )

    entities_web_bp.add_url_rule(
        f'{route_path}/content',
        f'{route_name}_content',
        lambda model=model: entity_content(model)
    )