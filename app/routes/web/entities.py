"""
Web routes for CRM entities - Fully dynamic, zero hardcoding.
"""

from flask import Blueprint, render_template, request
from collections import defaultdict
from app.models import db, MODEL_REGISTRY

# Create blueprint
entities_web_bp = Blueprint("entities", __name__)



def build_dropdown_configs(model, request_args):
    """Build dropdown configs from model metadata for web UI."""
    dropdowns = {}
    metadata = model.get_field_metadata()

    # Get current values from request
    current_group_by = request_args.get('group_by', '')
    current_sort_by = request_args.get('sort_by', model.get_default_sort_field())
    current_sort_direction = request_args.get('sort_direction', 'asc')

    # Build filter dropdowns for fields with choices
    for field_name, field_info in metadata.items():
        if field_info['filterable'] and field_info['choices']:
            current_value = request_args.get(field_name, '')
            options = [{'value': '', 'label': f'All {field_info["label"]}'}]

            for choice_value, choice_data in field_info['choices'].items():
                options.append({
                    'value': choice_value,
                    'label': choice_data.get('label', choice_value)
                })

            dropdowns[f'filter_{field_name}'] = {
                'name': field_name,
                'label': f'Filter by {field_info["label"]}',
                'options': options,
                'current_value': current_value,
                'placeholder': f'All {field_info["label"]}',
                'multiple': False,
                'searchable': False
            }

    # Build groupable options
    groupable_options = [
        {'value': name, 'label': info['label']}
        for name, info in metadata.items()
        if info['groupable']
    ]

    if groupable_options:
        dropdowns['group_by'] = {
            'options': groupable_options,
            'current_value': current_group_by,
            'placeholder': 'Group by...',
            'multiple': False,
            'searchable': True
        }

    # Build sortable options
    sortable_options = [
        {'value': name, 'label': info['label']}
        for name, info in metadata.items()
        if info['sortable']
    ]

    # Always include id as sortable
    if not any(opt['value'] == 'id' for opt in sortable_options):
        sortable_options.append({'value': 'id', 'label': 'ID'})

    dropdowns['sort_by'] = {
        'options': sortable_options,
        'current_value': current_sort_by,
        'placeholder': 'Sort by...',
        'multiple': False,
        'searchable': True
    }

    dropdowns['sort_direction'] = {
        'options': [
            {'value': 'asc', 'label': 'Ascending'},
            {'value': 'desc', 'label': 'Descending'}
        ],
        'current_value': current_sort_direction,
        'placeholder': 'Order',
        'multiple': False,
        'searchable': False
    }

    return dropdowns




def create_routes():
    """Dynamically create all routes based on MODEL_REGISTRY"""
    for entity_type, model in MODEL_REGISTRY.items():
        # Let models control their own exposure
        if not hasattr(model, 'is_web_enabled') or not model.is_web_enabled():
            continue

        table_name = model.__tablename__
        # Create closures to capture the model
        def make_index(model, table_name):
            def handler():
                return entity_index(model, table_name)
            handler.__name__ = f"{table_name}_index"
            return handler

        def make_content(model, table_name):
            def handler():
                return entity_content(model, table_name)
            handler.__name__ = f"{table_name}_content"
            return handler

        # Register routes
        entities_web_bp.add_url_rule(
            f'/{table_name}',
            f'{table_name}_index',
            make_index(model, table_name)
        )

        entities_web_bp.add_url_rule(
            f'/{table_name}/content',
            f'{table_name}_content',
            make_content(model, table_name)
        )

        # Add alternate routes for users -> teams
        if entity_type == 'user':
            entities_web_bp.add_url_rule('/teams', 'teams_index', make_index(model, 'users'))
            entities_web_bp.add_url_rule('/teams/content', 'teams_content', make_content(model, 'users'))


def entity_index(model, table_name):
    """Generic index handler"""
    dropdown_configs = build_dropdown_configs(model, request.args)

    # Get basic stats
    display_name_plural = model.get_display_name_plural()
    total = model.query.count()
    stats = {
        'title': f'{display_name_plural} Overview',
        'stats': [{'value': total, 'label': f'Total {display_name_plural}'}]
    }

    # Add status breakdown for models with status field
    if hasattr(model, 'status'):
        from sqlalchemy import func
        status_counts = db.session.query(model.status, func.count(model.id)).group_by(model.status).all()
        for status, count in status_counts:
            if status:
                stats['stats'].append({'value': count, 'label': status.replace('-', ' ').replace('_', ' ').title()})

    # Build entity config for template
    from app.models import MODEL_REGISTRY
    entity_type = next((key for key, value in MODEL_REGISTRY.items() if value == model), model.__name__.lower())

    entity_config = {
        'entity_type': entity_type,
        'entity_name': model.get_display_name_plural(),
        'entity_name_singular': model.get_display_name(),
        'content_endpoint': f'entities.{table_name}_content',
        'entity_buttons': [{
            'title': f'New {model.get_display_name()}',
            'url': f'/modals/{entity_type}/create'
        }]
    }

    return render_template("base/entity_index.html",
        entity_config=entity_config,
        dropdown_configs=dropdown_configs,
        entity_stats=stats
    )


def entity_content(model, table_name):
    """Generic content handler"""
    # Get params
    group_by = request.args.get('group_by', '')
    sort_by = request.args.get('sort_by', model.get_default_sort_field())
    sort_direction = request.args.get('sort_direction', 'asc')

    # Build query
    query = model.query

    # Detect and handle joins for _name fields
    if sort_by.endswith('_name'):
        # Try to find the related model
        base_field = sort_by.replace('_name', '')
        if hasattr(model, f'{base_field}_id'):
            # Find the relationship
            for rel in model.__mapper__.relationships:
                if rel.key == base_field:
                    related_model = rel.mapper.class_
                    query = query.join(related_model)
                    sort_field = related_model.name
                    break
            else:
                sort_field = getattr(model, sort_by) if hasattr(model, sort_by) else model.id
        else:
            sort_field = getattr(model, sort_by) if hasattr(model, sort_by) else model.id
    else:
        sort_field = getattr(model, sort_by) if hasattr(model, sort_by) else model.id

    # Apply filters dynamically from request args
    metadata = model.get_field_metadata()
    for field_name, field_info in metadata.items():
        if field_info['filterable']:
            filter_value = request.args.get(field_name)
            if filter_value and hasattr(model, field_name):
                query = query.filter(getattr(model, field_name) == filter_value)

    # Apply sorting
    query = query.order_by(sort_field.desc() if sort_direction == 'desc' else sort_field.asc())

    entities = query.all()

    # Group if needed
    grouped_entities = []
    if group_by and hasattr(model, group_by):
        grouped = defaultdict(list)
        for entity in entities:
            key = getattr(entity, group_by, 'Other') or 'Uncategorized'
            grouped[key].append(entity)

        grouped_entities = [
            {'key': k, 'label': k, 'count': len(v), 'entities': v}
            for k, v in grouped.items()
        ]
    else:
        grouped_entities = [{
            'key': 'all',
            'label': 'All Results',
            'count': len(entities),
            'entities': entities
        }]

    # Build template context
    from app.models import MODEL_REGISTRY
    entity_type = next((key for key, value in MODEL_REGISTRY.items() if value == model), model.__name__.lower())

    return render_template("shared/entity_content.html",
        grouped_entities=grouped_entities,
        group_by=group_by,
        total_count=len(entities),
        entity_type=entity_type,
        entity_name=model.get_display_name_plural(),
        entity_name_singular=model.get_display_name(),
        entity_name_plural=model.get_display_name_plural()
    )


# Create all routes dynamically
create_routes()