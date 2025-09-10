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


def get_model_columns(model_class, exclude_fields=None):
    """
    Get sortable column names from a model.
    
    Args:
        model_class: SQLAlchemy model class
        exclude_fields: List of field names to exclude
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    exclude_fields = exclude_fields or ['id', 'created_at', 'updated_at']
    
    columns = []
    for column in model_class.__table__.columns:
        if column.name not in exclude_fields:
            label = column.name.replace('_', ' ').title()
            columns.append({'value': column.name, 'label': label})
    
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
    
    return get_distinct_values(model_class, field_name, kwargs.get('label_transform'))


def get_sort_options(model_name, exclude_fields=None):
    """
    Generic function to get sort options for any model.
    
    Args:
        model_name: String name of the model
        exclude_fields: List of field names to exclude
    
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
    
    return get_model_columns(model_class, exclude_fields)