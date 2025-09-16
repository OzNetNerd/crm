"""
Web routes for CRM entities - Fully dynamic, zero hardcoding.
"""

from flask import Blueprint, render_template, request
from collections import defaultdict
from app.models import db

# Create blueprint
entities_web_bp = Blueprint("entities", __name__)

# Dynamic model discovery from the database models
def get_entity_models():
    """Get all entity models dynamically from SQLAlchemy"""
    models = {}
    for mapper in db.Model.registry.mappers:
        model = mapper.class_
        if hasattr(model, '__tablename__') and not model.__name__.startswith('_'):
            # Skip association tables and internal models
            if 'Team' in model.__name__ or model.__name__ in ['Note', 'ChatHistory', 'Embedding']:
                continue
            models[model.__tablename__] = model
    return models


def get_filterable_columns(model):
    """Extract filterable columns from model metadata"""
    filters = []
    for column in model.__table__.columns:
        column_info = getattr(column, 'info', {})
        # Consider columns with choices or foreign keys as filterable
        if column_info.get('choices') or column.name.endswith('_id'):
            filters.append(column.name)
    return filters


def get_default_sort(model):
    """Determine default sort field for a model"""
    # Priority: due_date, name, created_at, id
    for field in ['due_date', 'name', 'created_at', 'id']:
        if hasattr(model, field):
            return field
    return 'id'


def get_dropdowns_from_columns(model_class):
    """Build dropdown configs from model columns with groupable/sortable info."""
    dropdowns = {}
    current_group_by = request.args.get('group_by', '')
    current_sort_by = request.args.get('sort_by', '')
    current_sort_direction = request.args.get('sort_direction', 'asc')

    groupable_options = []
    sortable_options = []

    for column in model_class.__table__.columns:
        column_info = getattr(column, 'info', {})
        label = column_info.get('display_label', column.name.replace('_', ' ').title())

        if column_info.get('groupable'):
            groupable_options.append({'value': column.name, 'label': label})

        if column_info.get('sortable') or column.name in ['created_at', 'name', 'id']:
            sortable_options.append({'value': column.name, 'label': label})

        # Add filter dropdowns for fields with choices
        if column_info.get('choices'):
            current_filter_value = request.args.get(column.name, '')
            choice_options = [{'value': '', 'label': f'All {label}'}]  # "All" option

            for choice_value, choice_data in column_info['choices'].items():
                choice_options.append({
                    'value': choice_value,
                    'label': choice_data.get('label', choice_value)
                })

            dropdowns[f'filter_{column.name}'] = {
                'name': column.name,  # For form field name
                'label': f'Filter by {label}',
                'options': choice_options,
                'current_value': current_filter_value,
                'placeholder': f'All {label}',
                'multiple': False,
                'searchable': False  # Most filter dropdowns don't need search
            }

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
    """Dynamically create all routes based on discovered models"""
    models = get_entity_models()

    for table_name, model in models.items():
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
        if table_name == 'users':
            entities_web_bp.add_url_rule('/teams', 'teams_index', make_index(model, table_name))
            entities_web_bp.add_url_rule('/teams/content', 'teams_content', make_content(model, table_name))


def entity_index(model, table_name):
    """Generic index handler"""
    dropdown_configs = get_dropdowns_from_columns(model)

    # Get basic stats using model metadata
    metadata = model.get_metadata()
    total = model.query.count()
    stats = {'title': f'{metadata["entity_name"]} Overview', 'stats': [{'value': total, 'label': f'Total {metadata["entity_name"]}'}]}

    # Add status breakdown for models with status field
    if hasattr(model, 'status'):
        from sqlalchemy import func
        status_counts = db.session.query(model.status, func.count(model.id)).group_by(model.status).all()
        for status, count in status_counts:
            if status:
                stats['stats'].append({'value': count, 'label': status.replace('-', ' ').replace('_', ' ').title()})

    entity_config = {
        'entity_type': metadata['entity_type'],
        'entity_name': metadata['entity_name'],
        'entity_name_singular': metadata['entity_name_singular'],
        'content_endpoint': f'entities.{table_name}_content',
        'entity_buttons': [{
            'title': f'New {metadata["entity_name_singular"]}',
            'url': f'/modals/{model.__name__}/create'
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
    sort_by = request.args.get('sort_by', get_default_sort(model))
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
    for column in model.__table__.columns:
        filter_value = request.args.get(column.name)
        if filter_value:
            query = query.filter(getattr(model, column.name) == filter_value)

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

    return render_template("shared/entity_content.html",
        grouped_entities=grouped_entities,
        group_by=group_by,
        total_count=len(entities),
        **model.get_metadata()
    )


# Create all routes dynamically
create_routes()