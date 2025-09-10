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
    from app.models import Company, Stakeholder, Task, Opportunity
    
    model_map = {
        'Company': Company,
        'Stakeholder': Stakeholder, 
        'Task': Task,
        'Opportunity': Opportunity
    }
    
    model_class = model_map.get(model_name)
    if not model_class:
        return []
    
    # Special handling for specific model-field combinations
    if model_name == 'Task' and field_name == 'entity_type':
        return get_task_entity_types()
    elif model_name == 'Contact' and field_name == 'industry':
        return get_contact_industries()
    
    return get_distinct_values(model_class, field_name, kwargs.get('label_transform'))


def get_task_entity_types():
    """
    Get available entity types for tasks from task_entities table.
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    from app.models import db
    
    # Get distinct entity types from task_entities junction table
    distinct_types = db.session.execute(
        db.text("SELECT DISTINCT entity_type FROM task_entities ORDER BY entity_type")
    ).fetchall()
    
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
    
    # Always include the basic entity types for new tasks
    for entity_type, label in type_labels.items():
        if not any(opt['value'] == entity_type for opt in options):
            options.append({'value': entity_type, 'label': label})
    
    return sorted(options, key=lambda x: x['label'])


def get_contact_industries():
    """
    Get available industries for contacts (from their companies).
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    from app.models import Company
    
    # Get distinct industries from companies that have contacts
    companies_with_contacts = db.session.query(distinct(Company.industry))\
        .join(Company.contacts)\
        .filter(Company.industry.isnot(None))\
        .all()
    
    options = []
    for (industry,) in companies_with_contacts:
        if industry:
            options.append({'value': industry, 'label': industry.title()})
    
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
    from app.models import Company, Stakeholder, Task, Opportunity
    
    model_map = {
        'Company': Company,
        'Contact': Stakeholder,
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


def get_group_options(model_name, exclude_fields=None, custom_fields=None):
    """
    Get grouping options for any model (same as sort options since grouping uses same fields).
    
    Args:
        model_name: String name of the model
        exclude_fields: List of field names to exclude
        custom_fields: Dict of custom computed fields to add
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    return get_sort_options(model_name, exclude_fields, custom_fields)


def get_grouping_options(model_name):
    """
    Get semantic grouping options for different models.
    These are business-logic based groupings, not just database fields.
    
    Args:
        model_name: String name of the model
        
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    grouping_configs = {
        'Opportunity': [
            {'value': 'stage', 'label': 'Pipeline Stage'},
            {'value': 'close_date', 'label': 'Close Date'},
            {'value': 'value', 'label': 'Deal Value'},
            {'value': 'company', 'label': 'Company'}
        ],
        'Contact': [
            {'value': 'company', 'label': 'Company'},
            {'value': 'industry', 'label': 'Industry'},
            {'value': 'role', 'label': 'Role'},
            {'value': 'contact_info', 'label': 'Contact Info'}
        ],
        'Company': [
            {'value': 'industry', 'label': 'Industry'},
            {'value': 'size', 'label': 'Company Size'},
            {'value': 'contacts', 'label': 'Contact Count'},
            {'value': 'opportunities', 'label': 'Opportunities'}
        ],
        'Task': [
            {'value': 'status', 'label': 'Status'},
            {'value': 'due_date', 'label': 'Due Date'},
            {'value': 'priority', 'label': 'Priority'},
            {'value': 'entity', 'label': 'Related To'}
        ]
    }
    
    return grouping_configs.get(model_name, [])


def get_priority_options(model_name):
    """
    Get priority/quality filter options for different models.
    
    Args:
        model_name: String name of the model
        
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    priority_configs = {
        'Opportunity': [
            {'value': 'high', 'label': 'High ($50K+)'},
            {'value': 'medium', 'label': 'Medium ($10K-$50K)'},
            {'value': 'low', 'label': 'Low (<$10K)'}
        ],
        'Contact': [
            {'value': 'complete', 'label': 'Complete Info'},
            {'value': 'email_only', 'label': 'Email Only'},
            {'value': 'phone_only', 'label': 'Phone Only'},
            {'value': 'missing', 'label': 'Missing Info'}
        ],
        'Company': [
            {'value': 'has_industry', 'label': 'Has Industry'},
            {'value': 'has_website', 'label': 'Has Website'},
            {'value': 'has_contacts', 'label': 'Has Contacts'},
            {'value': 'missing_info', 'label': 'Missing Info'}
        ],
        'Task': []  # Tasks use get_filter_options('Task', 'priority') instead
    }
    
    return priority_configs.get(model_name, [])


def get_size_options():
    """
    Get company size filter options.
    
    Returns:
        List of {'value': str, 'label': str} dictionaries
    """
    return [
        {'value': 'small', 'label': 'Small (1-50)'},
        {'value': 'medium', 'label': 'Medium (51-500)'},
        {'value': 'large', 'label': 'Large (500+)'},
        {'value': 'unknown', 'label': 'Unknown Size'}
    ]