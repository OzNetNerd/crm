from flask import Blueprint, request, jsonify, render_template_string
from app.utils.form_configs import FormConfigManager, DynamicChoiceProvider
from app.utils.model_introspection import ModelIntrospector, get_model_by_name, get_all_model_configs
from app.utils.dynamic_form_builder import DynamicFormBuilder
from app.forms.entity_forms import (
    CompanyForm,
    StakeholderForm,
    OpportunityForm,
    NoteForm,
)

api_core_bp = Blueprint("api_core", __name__, url_prefix="/api")


# ==============================================================================
# DYNAMIC FORM CONFIGURATION ENDPOINTS - DRY APPROACH
# Single source of truth for all form configurations
# ==============================================================================


@api_core_bp.route("/form-config/<entity_type>")
def get_form_config(entity_type):
    """
    Get dynamic form configuration for any entity type.

    This endpoint eliminates duplication between backend forms and frontend
    template configs by generating configurations directly from WTForms.
    """
    try:
        # Map entity types to form classes
        form_classes = {
            "company": CompanyForm,
            "stakeholder": StakeholderForm,
            "opportunity": OpportunityForm,
            "note": NoteForm,
        }

        form_class = form_classes.get(entity_type)
        if not form_class:
            return jsonify({"error": f"Unknown entity type: {entity_type}"}), 400

        # Get context from query parameters for dynamic choices
        context = {
            "company_id": request.args.get("company_id"),
            "user_id": request.args.get("user_id"),
        }

        # Generate configuration using DRY approach
        config = FormConfigManager.get_form_config(form_class, context)

        return jsonify(config)

    except Exception as e:
        return jsonify({"error": f"Failed to generate form config: {str(e)}"}), 500


@api_core_bp.route("/choices/<choice_type>")
def get_dynamic_choices(choice_type):
    """
    Get dynamic choices for select fields.

    Supports real-time choice population and filtering based on context.
    """
    try:
        # Get filter parameters
        company_id = request.args.get("company_id", type=int)

        # Route to appropriate choice provider
        choice_methods = {
            "companies": DynamicChoiceProvider.get_company_choices,
            "users": DynamicChoiceProvider.get_user_choices,
            "stakeholders": lambda: DynamicChoiceProvider.get_stakeholder_choices(
                company_id
            ),
            "meddpicc_roles": DynamicChoiceProvider.get_meddpicc_role_choices,
            "industries": DynamicChoiceProvider.get_industry_choices,
            "opportunity_stages": DynamicChoiceProvider.get_opportunity_stage_choices,
            "company_sizes": DynamicChoiceProvider.get_company_size_choices,
        }

        choice_method = choice_methods.get(choice_type)
        if not choice_method:
            return jsonify({"error": f"Unknown choice type: {choice_type}"}), 400

        choices = choice_method()
        return jsonify({"choices": choices})

    except Exception as e:
        return jsonify({"error": f"Failed to get choices: {str(e)}"}), 500


# ==============================================================================
# MODEL INTROSPECTION API ENDPOINTS - SELF-DESCRIBING MODELS
# Single source of truth for all model configurations
# ==============================================================================


@api_core_bp.route("/model-config")
def get_all_model_configurations():
    """
    Get configuration for all models.
    
    Returns complete model configurations including choices, groupable fields,
    sortable fields, and all metadata directly from the models themselves.
    """
    try:
        configs = get_all_model_configs()
        return jsonify(configs)
    except Exception as e:
        return jsonify({"error": f"Failed to get model configs: {str(e)}"}), 500


@api_core_bp.route("/model-config/<model_name>")
def get_model_configuration(model_name):
    """
    Get complete configuration for a specific model.
    
    Args:
        model_name: Name of the model (e.g., 'Opportunity', 'Task', 'Company')
        
    Returns:
        Complete model configuration including all field metadata
    """
    try:
        model_class = get_model_by_name(model_name)
        if not model_class:
            return jsonify({"error": f"Unknown model: {model_name}"}), 404
        
        config = ModelIntrospector.get_model_config(model_class)
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": f"Failed to get model config: {str(e)}"}), 500


@api_core_bp.route("/model-config/<model_name>/<field_name>")
def get_field_configuration(model_name, field_name):
    """
    Get configuration for a specific model field.
    
    Args:
        model_name: Name of the model
        field_name: Name of the field
        
    Returns:
        Field configuration including choices, CSS classes, icons, etc.
    """
    try:
        model_class = get_model_by_name(model_name)
        if not model_class:
            return jsonify({"error": f"Unknown model: {model_name}"}), 404
        
        choices = ModelIntrospector.get_field_choices_with_metadata(model_class, field_name)
        if not choices:
            return jsonify({"error": f"Field {field_name} not found or has no choices"}), 404
        
        return jsonify({
            "field_name": field_name,
            "model_name": model_name,
            "choices": choices,
            "form_choices": ModelIntrospector.get_field_choices(model_class, field_name),
            "ordered_choices": ModelIntrospector.get_ordered_choices(model_class, field_name)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get field config: {str(e)}"}), 500


@api_core_bp.route("/model-choices/<model_name>")
def get_model_form_choices(model_name):
    """
    Get all form choices for a model in API-friendly format.
    
    Args:
        model_name: Name of the model
        
    Returns:
        All field choices formatted for frontend consumption
    """
    try:
        model_class = get_model_by_name(model_name)
        if not model_class:
            return jsonify({"error": f"Unknown model: {model_name}"}), 404
        
        choices_data = DynamicFormBuilder.get_form_choices_api_data(model_class)
        return jsonify({
            "model_name": model_name,
            "choices": choices_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get model choices: {str(e)}"}), 500


@api_core_bp.route("/field-choices/<model_name>/<field_name>")
def get_field_choices_api(model_name, field_name):
    """
    Get choices for a specific field in API format.
    
    Args:
        model_name: Name of the model
        field_name: Name of the field
        
    Returns:
        Field choices with complete metadata for frontend use
    """
    try:
        model_class = get_model_by_name(model_name)
        if not model_class:
            return jsonify({"error": f"Unknown model: {model_name}"}), 404
        
        choices_metadata = ModelIntrospector.get_field_choices_with_metadata(model_class, field_name)
        if not choices_metadata:
            return jsonify({"error": f"No choices found for {model_name}.{field_name}"}), 404
        
        # Format for API consumption
        api_choices = [
            {
                'value': value,
                'label': config['label'],
                'css_class': config.get('css_class', ''),
                'icon': config.get('icon', ''),
                'description': config.get('description', ''),
                'order': config.get('order', 999),
                'groupable': config.get('groupable', False),
                'sortable': config.get('sortable', True)
            }
            for value, config in choices_metadata.items()
        ]
        
        # Sort by order
        api_choices.sort(key=lambda x: x['order'])
        
        return jsonify({
            "field_name": field_name,
            "model_name": model_name,
            "choices": api_choices
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get field choices: {str(e)}"}), 500


@api_core_bp.route("/icon", methods=["POST"])
def get_icon():
    """Get icon HTML from Jinja2 macro"""
    try:
        data = request.get_json()
        macro_name = data.get("macro_name")
        css_class = data.get("class", "w-5 h-5")

        if not macro_name:
            return jsonify({"error": "macro_name is required"}), 400

        # Template to call the macro
        template_str = f"""
        {{% from 'components/icons.html' import {macro_name} %}}
        {{{{ {macro_name}(class='{css_class}') }}}}
        """

        # Render the macro
        icon_html = render_template_string(template_str.strip())

        return icon_html, 200, {"Content-Type": "text/html"}

    except Exception as e:
        return jsonify({"error": f"Failed to render icon: {str(e)}"}), 500