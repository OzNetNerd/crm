"""
Form Configuration API

Provides form configurations that replace modal_configs.py.
Returns JSON form schemas for Alpine.js client-side rendering.
"""

from flask import Blueprint, jsonify, request
from app.utils.core.model_introspection import get_model_by_name

forms_api = Blueprint('forms_api', __name__, url_prefix='/api/forms')


# Simplified form configs to replace the massive modal_configs.py
FORM_CONFIGS = {
    'company': {
        'title': 'Create Company',
        'edit_title': 'Edit Company',
        'fields': [
            {
                'type': 'text',
                'name': 'name',
                'label': 'Company Name',
                'placeholder': 'Enter company name',
                'required': True
            },
            {
                'type': 'grid',
                'columns': 2,
                'fields': [
                    {
                        'type': 'select',
                        'name': 'industry',
                        'label': 'Industry',
                        'options': [
                            {'value': '', 'label': 'Select industry'},
                            {'value': 'technology', 'label': 'Technology'},
                            {'value': 'finance', 'label': 'Finance'},
                            {'value': 'healthcare', 'label': 'Healthcare'},
                            {'value': 'manufacturing', 'label': 'Manufacturing'},
                            {'value': 'retail', 'label': 'Retail'},
                            {'value': 'other', 'label': 'Other'}
                        ]
                    },
                    {
                        'type': 'select',
                        'name': 'size',
                        'label': 'Company Size',
                        'options': [
                            {'value': '', 'label': 'Select size'},
                            {'value': 'startup', 'label': 'Startup (1-10)'},
                            {'value': 'small', 'label': 'Small (11-50)'},
                            {'value': 'medium', 'label': 'Medium (51-200)'},
                            {'value': 'large', 'label': 'Large (201-1000)'},
                            {'value': 'enterprise', 'label': 'Enterprise (1000+)'}
                        ]
                    }
                ]
            },
            {
                'type': 'grid',
                'columns': 2,
                'fields': [
                    {
                        'type': 'url',
                        'name': 'website',
                        'label': 'Website',
                        'placeholder': 'https://example.com'
                    },
                    {
                        'type': 'tel',
                        'name': 'phone',
                        'label': 'Phone',
                        'placeholder': '+1 (555) 123-4567'
                    }
                ]
            },
            {
                'type': 'textarea',
                'name': 'address',
                'label': 'Address',
                'placeholder': 'Enter company address',
                'rows': 3
            }
        ]
    },
    'contact': {
        'title': 'Create Contact',
        'edit_title': 'Edit Contact',
        'fields': [
            {
                'type': 'grid',
                'columns': 2,
                'fields': [
                    {
                        'type': 'text',
                        'name': 'first_name',
                        'label': 'First Name',
                        'placeholder': 'Enter first name',
                        'required': True
                    },
                    {
                        'type': 'text',
                        'name': 'last_name',
                        'label': 'Last Name',
                        'placeholder': 'Enter last name',
                        'required': True
                    }
                ]
            },
            {
                'type': 'text',
                'name': 'title',
                'label': 'Job Title',
                'placeholder': 'Enter job title'
            },
            {
                'type': 'grid',
                'columns': 2,
                'fields': [
                    {
                        'type': 'email',
                        'name': 'email',
                        'label': 'Email',
                        'placeholder': 'email@example.com',
                        'required': True
                    },
                    {
                        'type': 'tel',
                        'name': 'phone',
                        'label': 'Phone',
                        'placeholder': '+1 (555) 123-4567'
                    }
                ]
            },
            {
                'type': 'select',
                'name': 'company_id',
                'label': 'Company',
                'options': []  # Will be populated dynamically
            }
        ]
    },
    'opportunity': {
        'title': 'Create Opportunity',
        'edit_title': 'Edit Opportunity',
        'fields': [
            {
                'type': 'text',
                'name': 'name',
                'label': 'Opportunity Name',
                'placeholder': 'Enter opportunity name',
                'required': True
            },
            {
                'type': 'grid',
                'columns': 2,
                'fields': [
                    {
                        'type': 'select',
                        'name': 'stage',
                        'label': 'Stage',
                        'required': True,
                        'options': [
                            {'value': '', 'label': 'Select stage'},
                            {'value': 'prospecting', 'label': 'Prospecting'},
                            {'value': 'qualification', 'label': 'Qualification'},
                            {'value': 'proposal', 'label': 'Proposal'},
                            {'value': 'negotiation', 'label': 'Negotiation'},
                            {'value': 'closed_won', 'label': 'Closed Won'},
                            {'value': 'closed_lost', 'label': 'Closed Lost'}
                        ]
                    },
                    {
                        'type': 'text',
                        'name': 'value',
                        'label': 'Value ($)',
                        'placeholder': '0.00'
                    }
                ]
            },
            {
                'type': 'select',
                'name': 'company_id',
                'label': 'Company',
                'required': True,
                'options': []  # Will be populated dynamically
            },
            {
                'type': 'textarea',
                'name': 'description',
                'label': 'Description',
                'placeholder': 'Enter opportunity description',
                'rows': 3
            }
        ]
    },
    'task': {
        'title': 'Create Task',
        'edit_title': 'Edit Task',
        'fields': [
            {
                'type': 'text',
                'name': 'title',
                'label': 'Task Title',
                'placeholder': 'Enter task title',
                'required': True
            },
            {
                'type': 'grid',
                'columns': 2,
                'fields': [
                    {
                        'type': 'select',
                        'name': 'priority',
                        'label': 'Priority',
                        'options': [
                            {'value': 'low', 'label': 'Low'},
                            {'value': 'medium', 'label': 'Medium'},
                            {'value': 'high', 'label': 'High'},
                            {'value': 'urgent', 'label': 'Urgent'}
                        ]
                    },
                    {
                        'type': 'select',
                        'name': 'status',
                        'label': 'Status',
                        'options': [
                            {'value': 'pending', 'label': 'Pending'},
                            {'value': 'in_progress', 'label': 'In Progress'},
                            {'value': 'completed', 'label': 'Completed'},
                            {'value': 'cancelled', 'label': 'Cancelled'}
                        ]
                    }
                ]
            },
            {
                'type': 'date',
                'name': 'due_date',
                'label': 'Due Date'
            },
            {
                'type': 'textarea',
                'name': 'description',
                'label': 'Description',
                'placeholder': 'Enter task description',
                'rows': 4
            }
        ]
    }
}


@forms_api.route('/<model_name>/config')
def get_form_config(model_name):
    """
    Get form configuration for a model.

    Replaces the server-side form generation from modal_configs.py
    with a lightweight JSON API.
    """
    form_type = request.args.get('type', 'create')

    # Get base config
    config = FORM_CONFIGS.get(model_name.lower())
    if not config:
        return jsonify({'error': f'No form config found for {model_name}'}), 404

    # Create a copy to avoid modifying the original
    form_config = {
        'title': config.get('edit_title' if form_type == 'edit' else 'title', f'{form_type.title()} {model_name.title()}'),
        'fields': config['fields'].copy()
    }

    # Populate dynamic options (e.g., company dropdown)
    _populate_dynamic_options(form_config, model_name)

    return jsonify(form_config)


def _populate_dynamic_options(form_config, model_name):
    """
    Populate dynamic dropdown options (e.g., companies for contact/opportunity forms).

    This replaces the complex relationship logic from modal_configs.py
    with simple dynamic population.
    """
    # Find fields that need dynamic options
    for field in form_config['fields']:
        if field.get('type') == 'grid':
            for sub_field in field.get('fields', []):
                _populate_field_options(sub_field)
        else:
            _populate_field_options(field)


def _populate_field_options(field):
    """Populate options for a single field."""
    if field.get('name') == 'company_id' and not field.get('options'):
        # Load companies for dropdown
        try:
            from app.models import Company
            companies = Company.query.order_by(Company.name).all()
            field['options'] = [{'value': '', 'label': 'Select company'}] + [
                {'value': str(company.id), 'label': company.name}
                for company in companies
            ]
        except Exception as e:
            print(f"Error loading companies: {e}")
            field['options'] = [{'value': '', 'label': 'Select company'}]


@forms_api.route('/<model_name>/validate', methods=['POST'])
def validate_form(model_name):
    """
    Validate form data server-side.

    Optional endpoint for additional server-side validation
    beyond what Alpine.js provides client-side.
    """
    from flask import request

    data = request.get_json()
    errors = {}

    # Basic validation - can be extended
    config = FORM_CONFIGS.get(model_name.lower())
    if config:
        for field in config['fields']:
            if field.get('type') == 'grid':
                for sub_field in field.get('fields', []):
                    _validate_field(sub_field, data, errors)
            else:
                _validate_field(field, data, errors)

    return jsonify({
        'valid': len(errors) == 0,
        'errors': errors
    })


def _validate_field(field, data, errors):
    """Validate a single field."""
    field_name = field.get('name')
    if not field_name:
        return

    value = data.get(field_name)

    # Required validation
    if field.get('required') and not value:
        errors[field_name] = f"{field.get('label', field_name)} is required"

    # Email validation
    if field.get('type') == 'email' and value:
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value):
            errors[field_name] = "Please enter a valid email address"