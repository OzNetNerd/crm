from app.models import db
from sqlalchemy import distinct


def get_distinct_values(model_class, field_name, label_transform=None):
    """
    Get distinct values from a model field for filter options.
    
    Args:
        model_class: SQLAlchemy model class
        field_name: Name of the field to get distinct values from
        label_transform: Optional function to transform field value to display label
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    field = getattr(model_class, field_name)
    distinct_values = db.session.query(distinct(field)).filter(field.isnot(None)).all()
    
    options = []
    for (value,) in distinct_values:
        if value:  # Skip empty/null values
            label = label_transform(value) if label_transform else value.title()
            options.append({'value': value, 'label': label})
    
    return sorted(options, key=lambda x: x['label'])


def get_model_columns(model_class, exclude_fields=None, custom_fields=None):
    """
    Get sortable column names from a model.
    
    Args:
        model_class: SQLAlchemy model class
        exclude_fields: List of field names to exclude
        custom_fields: Dict of custom computed fields to add {'value': 'label'}
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    exclude_fields = exclude_fields or ['id', 'created_at', 'updated_at']
    custom_fields = custom_fields or {}
    
    columns = []
    
    # Add database columns
    for column in model_class.__table__.columns:
        if column.name not in exclude_fields:
            label = column.name.replace('_', ' ').title()
            columns.append({'value': column.name, 'label': label})
    
    # Add custom computed fields
    for value, label in custom_fields.items():
        columns.append({'value': value, 'label': label})
    
    return sorted(columns, key=lambda x: x['label'])


def get_filter_options(model_name, field_name, **kwargs):
    """
    Generic function to get filter options for any model field.
    
    Args:
        model_name: String name of the model ('Company', 'Task', etc.)
        field_name: Name of the field to get options for
        **kwargs: Additional arguments passed to specific functions
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    from app.models import Company, Contact, Task, Opportunity
    
    model_map = {
        'Company': Company,
        'Contact': Contact, 
        'Task': Task,
        'Opportunity': Opportunity
    }
    
    model_class = model_map.get(model_name)
    if not model_class:
        return []
    
    # Special handling for Task entity_type field
    if model_name == 'Task' and field_name == 'entity_type':
        return get_task_entity_types()
    
    return get_distinct_values(model_class, field_name, kwargs.get('label_transform'))


def get_task_entity_types():
    """
    Get available entity types for tasks with proper labels.
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    from app.models import Task
    
    # Get distinct entity types from database
    distinct_types = db.session.query(distinct(Task.entity_type)).filter(Task.entity_type.isnot(None)).all()
    
    # Map to proper labels
    type_labels = {
        'company': 'Company',
        'contact': 'Contact', 
        'opportunity': 'Opportunity'
    }
    
    options = []
    for (entity_type,) in distinct_types:
        if entity_type:
            label = type_labels.get(entity_type, entity_type.title())
            options.append({'value': entity_type, 'label': label})
    
    # Add 'General' for tasks with no entity relationship
    # Check if there are tasks with null entity_type
    null_count = db.session.query(Task).filter(Task.entity_type.is_(None)).count()
    if null_count > 0:
        options.append({'value': 'unrelated', 'label': 'General'})
    
    return sorted(options, key=lambda x: x['label'])


def get_sort_options(model_name, exclude_fields=None, custom_fields=None):
    """
    Generic function to get sort options for any model.
    
    Args:
        model_name: String name of the model
        exclude_fields: List of field names to exclude
        custom_fields: Dict of custom computed fields to add
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    from app.models import Company, Contact, Task, Opportunity
    
    model_map = {
        'Company': Company,
        'Contact': Contact,
        'Task': Task, 
        'Opportunity': Opportunity
    }
    
    # Default custom fields for each model
    default_custom_fields = {
        'Company': {
            'contacts_count': 'Contact Count',
            'opportunities_count': 'Opportunity Count'
        },
        'Task': {
            'entity_name': 'Related To'
        },
        'Opportunity': {
            'deal_age': 'Deal Age'
        }
    }
    
    model_class = model_map.get(model_name)
    if not model_class:
        return []
    
    # Merge default custom fields with any provided
    final_custom_fields = default_custom_fields.get(model_name, {})
    if custom_fields:
        final_custom_fields.update(custom_fields)
    
    return get_model_columns(model_class, exclude_fields, final_custom_fields)