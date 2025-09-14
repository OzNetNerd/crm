"""
Form Configuration API

Provides form configurations that replace modal_configs.py.
Returns JSON form schemas for Alpine.js client-side rendering.
"""

from flask import Blueprint, jsonify, request

forms_api = Blueprint('forms_api', __name__, url_prefix='/api/forms')

# Simplified form configs to replace the massive modal_configs.py
FORM_CONFIGS = {
    'company': {
        'title': 'Create Company',
        'edit_title': 'Edit Company',
        'fields': [
            {
                'name': 'name',
                'type': 'text',
                'label': 'Company Name',
                'required': True,
                'validation': {'required': True, 'maxLength': 255}
            },
            {
                'name': 'industry',
                'type': 'select',
                'label': 'Industry',
                'options': [
                    {'value': 'technology', 'label': 'Technology'},
                    {'value': 'healthcare', 'label': 'Healthcare'},
                    {'value': 'finance', 'label': 'Finance'},
                    {'value': 'manufacturing', 'label': 'Manufacturing'},
                    {'value': 'retail', 'label': 'Retail'},
                    {'value': 'education', 'label': 'Education'},
                    {'value': 'consulting', 'label': 'Consulting'},
                    {'value': 'energy', 'label': 'Energy'},
                    {'value': 'other', 'label': 'Other'}
                ]
            },
            {
                'name': 'website',
                'type': 'url',
                'label': 'Website',
                'validation': {'url': True}
            }
        ]
    }
}

@forms_api.route('/<model_name>/config')
def get_form_config(model_name):
    """Get form configuration for a model"""
    form_type = request.args.get('type', 'create')

    config = FORM_CONFIGS.get(model_name.lower())
    if not config:
        return jsonify({'error': f'No form config for {model_name}'}), 404

    # Return appropriate title based on form type
    title = config.get('edit_title') if form_type == 'edit' else config.get('title')

    return jsonify({
        'title': title,
        'fields': config['fields']
    })