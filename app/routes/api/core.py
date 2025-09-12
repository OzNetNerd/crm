from flask import Blueprint, request, jsonify
from app.utils.forms.form_builder import FormConfigManager

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
        # Import forms inside function to avoid app context issues
        from app.forms import (
            CompanyForm,
            StakeholderForm,
            OpportunityForm,
            NoteForm,
        )
        
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


