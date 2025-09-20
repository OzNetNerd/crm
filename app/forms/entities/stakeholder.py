"""
Stakeholder Forms

Simple stakeholder form using WTForms with model introspection.
"""

from wtforms import StringField, TextAreaField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, Length
from ..base.base_forms import BaseForm
from app.utils.logging_config import get_crm_logger
from app.utils.form_logger import form_logger


class StakeholderForm(BaseForm):
    """Form for creating and editing stakeholders in modals with comprehensive logging"""

    def __init__(self, *args, **kwargs):
        self.logger = get_crm_logger(__name__)
        super().__init__(*args, **kwargs)

        # Populate MEDDPICC role choices with logging
        from app.models.enums import MeddpiccRole

        choices = [
            (role.value, role.value.replace("_", " ").title())
            for role in MeddpiccRole
        ]
        self.meddpicc_roles_select.choices = choices

        self.logger.info(
            "Stakeholder form initialized",
            extra={
                "custom_fields": {
                    "meddpicc_choices_count": len(choices),
                    "form_fields": list(self._fields.keys())
                },
                "entity_type": "stakeholder",
                "form_operation": "initialization"
            }
        )

    name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(max=255)],
        render_kw={"placeholder": "Enter stakeholder name..."},
    )

    job_title = StringField(
        "Job Title",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Enter job title..."},
    )

    company = StringField("Company", validators=[DataRequired()])

    meddpicc_roles = HiddenField("MEDDPICC Roles")  # Keep for backward compatibility

    meddpicc_roles_select = SelectMultipleField(
        "MEDDPICC Roles",
        choices=[],  # Will be populated in __init__
        validators=[Optional()],
        render_kw={"class": "form-select", "size": "8"}
    )

    relationship_owners = HiddenField("Relationship Owners")

    comments = TextAreaField(
        "Comments",
        validators=[Optional()],
        render_kw={
            "placeholder": "Additional notes about this stakeholder...",
            "rows": 3,
        },
    )

    def validate(self, extra_validators=None):
        """Enhanced validation with logging for MEDDPICC processing."""
        # Log SelectMultipleField processing
        if hasattr(self, 'meddpicc_roles_select'):
            form_logger.log_select_multiple_field(
                field=self.meddpicc_roles_select,
                field_name='meddpicc_roles_select',
                entity_type='stakeholder'
            )

        # Perform standard validation
        is_valid = super().validate(extra_validators)

        # Log validation result with detailed field information
        self.logger.info(
            f"Stakeholder form validation {'passed' if is_valid else 'failed'}",
            extra={
                "custom_fields": {
                    "validation_passed": is_valid,
                    "field_errors": {field.name: field.errors for field in self if field.errors},
                    "meddpicc_data": self.meddpicc_roles_select.data,
                    "meddpicc_raw_data": self.meddpicc_roles_select.raw_data,
                    "has_company": bool(self.company.data),
                    "has_name": bool(self.name.data)
                },
                "entity_type": "stakeholder",
                "form_operation": "validation"
            }
        )

        return is_valid

    def get_display_fields(self):
        """Return field names to display in modal, in this exact order"""
        return ["name", "company", "job_title", "meddpicc_roles_select", "relationship_owners", "comments"]

    def get_field_layout(self):
        """
        Define field layout for consistent rendering in view and edit modes.
        Company and Job Title side by side for better space utilization.
        """
        return [
            {'type': 'single', 'field': 'name'},
            {'type': 'inline-2col', 'fields': ['company', 'job_title']},
            {'type': 'single', 'field': 'meddpicc_roles_select'},
            {'type': 'single', 'field': 'relationship_owners'},
            {'type': 'single', 'field': 'comments'}
        ]
