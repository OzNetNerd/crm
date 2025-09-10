"""
Dynamic Form Configuration System - Single Source of Truth

This module provides a DRY approach to form configuration by automatically 
generating JSON configurations from WTForms definitions. No more duplication
between backend forms and frontend template configs.
"""

from typing import Dict, List, Any, Optional
from flask_wtf import FlaskForm
from wtforms import Field
from wtforms.fields import (
    StringField,
    TextAreaField,
    SelectField,
    IntegerField,
    DecimalField,
    DateField,
    BooleanField,
    SelectMultipleField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    NumberRange,
    URL,
)


class FormConfigManager:
    """
    DRY Form Configuration Manager

    Generates dynamic form configurations from WTForms definitions,
    eliminating duplication between backend and frontend.
    """

    # Field type mapping - single source of truth
    FIELD_TYPE_MAP = {
        StringField: "text",
        TextAreaField: "textarea",
        SelectField: "select",
        SelectMultipleField: "multiselect",
        IntegerField: "number",
        DecimalField: "number",
        DateField: "date",
        BooleanField: "checkbox",
    }

    # Validator type mapping - DRY validation rules
    VALIDATOR_TYPE_MAP = {
        DataRequired: "required",
        Length: "length",
        Email: "email",
        NumberRange: "number_range",
        URL: "url",
    }

    @classmethod
    def get_form_config(
        cls, form_class: FlaskForm, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate complete form configuration from WTForms class.

        Args:
            form_class: The FlaskForm class to analyze
            context: Optional context for dynamic choices (user_id, company_id, etc.)

        Returns:
            Complete form configuration dictionary
        """
        config = {
            "entity_type": cls._get_entity_type(form_class.__name__),
            "title": cls._get_form_title(form_class.__name__),
            "fields": [],
            "validation_rules": {},
            "choices": {},
        }

        # Process each field in the form
        for field_name, field in form_class._formfields.items():
            field_config = cls._get_field_config(field_name, field, context)
            config["fields"].append(field_config)

            # Extract validation rules
            if field.validators:
                config["validation_rules"][field_name] = cls._get_validation_rules(
                    field.validators
                )

            # Extract choices for select fields
            if hasattr(field, "choices") and field.choices:
                config["choices"][field_name] = cls._get_field_choices(field, context)

        return config

    @classmethod
    def _get_field_config(
        cls, field_name: str, field: Field, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Extract configuration for a single field - DRY approach"""
        field_type = type(field)

        config = {
            "name": field_name,
            "type": cls.FIELD_TYPE_MAP.get(field_type, "text"),
            "label": (
                field.label.text
                if field.label
                else field_name.replace("_", " ").title()
            ),
            "required": cls._is_required(field.validators),
            "placeholder": cls._get_placeholder(field),
        }

        # Add type-specific attributes
        if field_type == TextAreaField:
            config["rows"] = getattr(field, "render_kw", {}).get("rows", 3)

        elif field_type in [IntegerField, DecimalField]:
            render_kw = getattr(field, "render_kw", {})
            if "min" in render_kw:
                config["min"] = render_kw["min"]
            if "max" in render_kw:
                config["max"] = render_kw["max"]
            if "step" in render_kw:
                config["step"] = render_kw["step"]

        elif field_type in [SelectField, SelectMultipleField]:
            config["choices"] = cls._get_field_choices(field, context)

        return config

    @classmethod
    def _get_validation_rules(cls, validators: List) -> Dict[str, Any]:
        """Extract validation rules from WTForms validators - DRY validation"""
        rules = {}

        for validator in validators:
            validator_type = type(validator)

            if validator_type == DataRequired:
                rules["required"] = True

            elif validator_type == Length:
                if hasattr(validator, "min") and validator.min is not None:
                    rules["min_length"] = validator.min
                if hasattr(validator, "max") and validator.max is not None:
                    rules["max_length"] = validator.max

            elif validator_type == NumberRange:
                if hasattr(validator, "min") and validator.min is not None:
                    rules["min_value"] = validator.min
                if hasattr(validator, "max") and validator.max is not None:
                    rules["max_value"] = validator.max

            elif validator_type == Email:
                rules["email"] = True

            elif validator_type == URL:
                rules["url"] = True

        return rules

    @classmethod
    def _get_field_choices(
        cls, field: Field, context: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """Get choices for select fields - supports dynamic choices"""
        if not hasattr(field, "choices"):
            return []

        choices = []
        for choice in field.choices:
            if isinstance(choice, (tuple, list)) and len(choice) == 2:
                choices.append({"value": str(choice[0]), "label": str(choice[1])})
            else:
                # Simple string choice
                choices.append({"value": str(choice), "label": str(choice)})

        return choices

    @classmethod
    def _is_required(cls, validators: List) -> bool:
        """Check if field is required"""
        return (
            any(isinstance(v, DataRequired) for v in validators)
            if validators
            else False
        )

    @classmethod
    def _get_placeholder(cls, field: Field) -> str:
        """Extract placeholder from field render_kw"""
        if hasattr(field, "render_kw") and field.render_kw:
            return field.render_kw.get("placeholder", "")
        return ""

    @classmethod
    def _get_entity_type(cls, form_name: str) -> str:
        """Extract entity type from form class name"""
        return form_name.replace("Form", "").lower()

    @classmethod
    def _get_form_title(cls, form_name: str) -> str:
        """Generate form title from class name"""
        entity_type = cls._get_entity_type(form_name)
        return f"{entity_type.replace('_', ' ').title()} Details"


class DynamicChoiceProvider:
    """
    Provides dynamic choices for form fields based on database state.
    Eliminates hardcoded choices and enables real-time data.
    """

    @staticmethod
    def get_company_choices() -> List[Dict[str, str]]:
        """Get all companies for select fields"""
        from app.models import Company

        companies = Company.query.order_by(Company.name).all()
        return [{"value": str(c.id), "label": c.name} for c in companies]

    @staticmethod
    def get_user_choices() -> List[Dict[str, str]]:
        """Get all users for select fields"""
        from app.models import User

        users = User.query.order_by(User.name).all()
        return [
            {"value": str(u.id), "label": f"{u.name} ({u.job_title})"} for u in users
        ]

    @staticmethod
    def get_stakeholder_choices(
        company_id: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """Get stakeholders, optionally filtered by company"""
        from app.models import Stakeholder

        query = Stakeholder.query
        if company_id:
            query = query.filter_by(company_id=company_id)
        stakeholders = query.order_by(Stakeholder.name).all()
        return [
            {"value": str(s.id), "label": f"{s.name} ({s.job_title})"}
            for s in stakeholders
        ]

    @staticmethod
    def get_meddpicc_role_choices() -> List[Dict[str, str]]:
        """Get MEDDPICC role options - centralized definition"""
        return [
            {"value": "metrics", "label": "Metrics - Quantifiable business value"},
            {"value": "economic_buyer", "label": "Economic Buyer - Budget authority"},
            {
                "value": "decision_criteria",
                "label": "Decision Criteria - Evaluation standards",
            },
            {
                "value": "decision_process",
                "label": "Decision Process - How decisions are made",
            },
            {
                "value": "paper_process",
                "label": "Paper Process - Procurement/legal process",
            },
            {
                "value": "implicate_pain",
                "label": "Implicate Pain - Problem identification",
            },
            {"value": "champion", "label": "Champion - Internal advocate"},
            {"value": "competition", "label": "Competition - Competitive landscape"},
        ]

    @staticmethod
    def get_industry_choices() -> List[Dict[str, str]]:
        """Get industry options - centralized and extensible"""
        return [
            {"value": "", "label": "Select industry"},
            {"value": "technology", "label": "Technology"},
            {"value": "finance", "label": "Finance & Banking"},
            {"value": "healthcare", "label": "Healthcare & Life Sciences"},
            {"value": "manufacturing", "label": "Manufacturing"},
            {"value": "retail", "label": "Retail & E-commerce"},
            {"value": "education", "label": "Education"},
            {"value": "consulting", "label": "Consulting & Professional Services"},
            {"value": "energy", "label": "Energy & Utilities"},
            {"value": "government", "label": "Government & Public Sector"},
            {"value": "other", "label": "Other"},
        ]

    @staticmethod
    def get_opportunity_stage_choices() -> List[Dict[str, str]]:
        """Get opportunity stage options - single source of truth"""
        return [
            {"value": "", "label": "Select stage"},
            {"value": "lead", "label": "Lead - Initial contact"},
            {"value": "qualified", "label": "Qualified - Meets criteria"},
            {"value": "proposal", "label": "Proposal - Formal proposal submitted"},
            {"value": "negotiation", "label": "Negotiation - Terms discussion"},
            {"value": "closed_won", "label": "Closed Won - Deal successful"},
            {"value": "closed_lost", "label": "Closed Lost - Deal unsuccessful"},
        ]

    @staticmethod
    def get_company_size_choices() -> List[Dict[str, str]]:
        """Get company size options"""
        return [
            {"value": "", "label": "Select size"},
            {"value": "startup", "label": "Startup (1-10 employees)"},
            {"value": "small", "label": "Small (11-50 employees)"},
            {"value": "medium", "label": "Medium (51-200 employees)"},
            {"value": "large", "label": "Large (201-1000 employees)"},
            {"value": "enterprise", "label": "Enterprise (1000+ employees)"},
        ]
