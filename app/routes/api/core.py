"""
Core API routes for the CRM application.

This module provides core API endpoints including dynamic form configuration
that serves as a single source of truth for all entity forms, eliminating
duplication between backend forms and frontend configurations.
"""

from typing import Dict, Any, Tuple
from flask import Blueprint, request, jsonify
from app.forms.base.builders import FormConfigManager

api_core_bp = Blueprint("api_core", __name__, url_prefix="/api")


# ==============================================================================
# DYNAMIC FORM CONFIGURATION ENDPOINTS - DRY APPROACH
# Single source of truth for all form configurations
# ==============================================================================


@api_core_bp.route("/form-config/<entity_type>")
def get_form_config(entity_type: str) -> Tuple[Dict[str, Any], int]:
    """
    Get dynamic form configuration for any entity type.
    
    This endpoint eliminates duplication between backend forms and frontend
    template configs by generating configurations directly from WTForms.
    Supports context-aware field choices based on query parameters.
    
    Args:
        entity_type: Type of entity to get form config for 
                    (company, stakeholder, opportunity, note).
    
    Returns:
        Tuple of (JSON response, HTTP status code).
        JSON contains form field configurations or error message.
        
    Example:
        GET /api/form-config/company?company_id=1
        Returns form configuration for company forms with dynamic choices.
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


