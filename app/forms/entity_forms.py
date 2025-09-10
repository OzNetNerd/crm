from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    DecimalField,
    DateField,
    IntegerField,
)
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange, URL
from wtforms.widgets import TextArea
from app.models import Company, Stakeholder, Opportunity
from app.utils.dynamic_form_builder import DynamicFormBuilder
from app.utils.model_introspection import ModelIntrospector


class CompanyForm(FlaskForm):
    # Dynamic fields from model metadata
    name = DynamicFormBuilder.build_string_field(
        Company, 'name',
        render_kw={"placeholder": "Enter company name..."}
    )
    
    industry = DynamicFormBuilder.build_select_field(
        Company, 'industry',
        render_kw={"placeholder": "Select industry..."}
    )
    
    website = DynamicFormBuilder.build_string_field(
        Company, 'website',
        render_kw={"placeholder": "https://example.com"}
    )


class StakeholderForm(FlaskForm):
    # Dynamic fields from model metadata
    name = DynamicFormBuilder.build_string_field(
        Stakeholder, 'name',
        render_kw={"placeholder": "Enter stakeholder name..."}
    )

    job_title = DynamicFormBuilder.build_string_field(
        Stakeholder, 'job_title',
        render_kw={"placeholder": "e.g., CEO, VP Sales, CTO..."}
    )

    email = DynamicFormBuilder.build_string_field(
        Stakeholder, 'email',
        render_kw={"placeholder": "stakeholder@company.com"}
    )

    phone = DynamicFormBuilder.build_string_field(
        Stakeholder, 'phone',
        render_kw={"placeholder": "+1 (555) 123-4567"}
    )

    company_id = IntegerField(
        "Company",
        validators=[DataRequired(), NumberRange(min=1)],
        render_kw={"class": "form-select"},
    )


class OpportunityForm(FlaskForm):
    # Dynamic fields from model metadata
    name = StringField(
        "Opportunity Name",
        validators=[DataRequired(), Length(min=1, max=255)],
        render_kw={"placeholder": "Enter opportunity name..."},
    )

    company_id = IntegerField(
        "Company", validators=[DataRequired(), NumberRange(min=1)]
    )
    
    value = DynamicFormBuilder.build_integer_field(
        Opportunity, 'value',
        render_kw={"placeholder": "Enter deal value...", "step": "1000"}
    )

    probability = DynamicFormBuilder.build_integer_field(
        Opportunity, 'probability',
        render_kw={"placeholder": "Enter probability %"}
    )

    expected_close_date = DynamicFormBuilder.build_date_field(
        Opportunity, 'expected_close_date'
    )

    stage = DynamicFormBuilder.build_select_field(
        Opportunity, 'stage'
    )


class NoteForm(FlaskForm):
    content = TextAreaField(
        "Note Content",
        validators=[DataRequired(), Length(min=1, max=2000)],
        widget=TextArea(),
        render_kw={"placeholder": "Enter your note here...", "rows": 4},
    )

    is_internal = SelectField(
        "Note Type",
        choices=[("1", "Internal Note"), ("0", "External Note")],
        default="1",
        validators=[DataRequired()],
    )

    entity_type = SelectField(
        "Attach To",
        choices=[
            ("company", "Company"),
            ("stakeholder", "Stakeholder"),
            ("opportunity", "Opportunity"),
            ("task", "Task"),
        ],
        validators=[DataRequired()],
    )

    entity_id = IntegerField(
        "Entity ID", validators=[DataRequired(), NumberRange(min=1)]
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        # Convert is_internal string to boolean
        self.is_internal.data = self.is_internal.data == "1"

        return True
