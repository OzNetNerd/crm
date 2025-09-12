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
# Models will be imported lazily to avoid circular imports
from app.utils.forms.form_builder import DynamicFormBuilder
from app.utils.core.model_introspection import ModelIntrospector
from .base_forms import BaseForm, FieldFactory, FormConstants


class CompanyForm(BaseForm):
    name = StringField(
        "Company Name", 
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter company name..."}
    )
    
    industry = SelectField(
        "Industry",
        choices=[
            ("", "Select industry"),
            ("technology", "Technology"),
            ("finance", "Finance"),
            ("healthcare", "Healthcare"),
            ("manufacturing", "Manufacturing"),
            ("retail", "Retail"),
            ("education", "Education"),
            ("consulting", "Consulting"),
            ("other", "Other")
        ],
        render_kw={"placeholder": "Select industry..."}
    )
    
    website = StringField(
        "Website",
        validators=[Optional(), URL()],
        render_kw={"placeholder": "https://example.com"}
    )

    size = SelectField(
        "Company Size",
        choices=[
            ("", "Select size"),
            ("startup", "Startup (1-10)"),
            ("small", "Small (11-50)"),
            ("medium", "Medium (51-200)"),
            ("large", "Large (201-1000)"),
            ("enterprise", "Enterprise (1000+)")
        ]
    )

    phone = StringField(
        "Phone",
        validators=[Optional()],
        render_kw={"placeholder": "Company phone number"}
    )

    address = TextAreaField(
        "Address",
        validators=[Optional()],
        render_kw={"placeholder": "Company address", "rows": 2}
    )


class StakeholderForm(BaseForm):
    name = StringField(
        "Full Name",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter stakeholder name..."}
    )

    job_title = StringField(
        "Job Title",
        validators=[Optional()],
        render_kw={"placeholder": "e.g., CEO, VP Sales, CTO..."}
    )

    email = StringField(
        "Email",
        validators=[Optional(), Email()],
        render_kw={"placeholder": "stakeholder@company.com"}
    )

    phone = StringField(
        "Phone",
        validators=[Optional()],
        render_kw={"placeholder": "Phone number"}
    )

    meddpicc_role = SelectField(
        "MEDDPICC Role",
        choices=[
            ("", "Select role"),
            ("economic_buyer", "Economic Buyer"),
            ("decision_maker", "Decision Maker"),
            ("influencer", "Influencer"),
            ("champion", "Champion"),
            ("user", "User"),
            ("other", "Other")
        ],
        validators=[Optional()]
    )


class OpportunityForm(BaseForm):
    name = StringField(
        "Opportunity Name",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter opportunity name..."}
    )

    value = DecimalField(
        "Value ($)",
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "10000"}
    )

    stage = SelectField(
        "Stage",
        choices=[
            ("", "Select stage"),
            ("prospect", "Prospect"),
            ("qualified", "Qualified"),
            ("proposal", "Proposal"),
            ("negotiation", "Negotiation"),
            ("closed_won", "Closed Won"),
            ("closed_lost", "Closed Lost")
        ],
        validators=[Optional()]
    )

    probability = IntegerField(
        "Probability (%)",
        validators=[Optional(), NumberRange(min=0, max=100)],
        render_kw={"placeholder": "25"}
    )

    expected_close_date = DateField(
        "Expected Close Date",
        validators=[Optional()]
    )

    priority = SelectField(
        "Priority",
        choices=[
            ("", "Select priority"),
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High")
        ],
        validators=[Optional()]
    )


class NoteForm(BaseForm):
    content = TextAreaField(
        "Note Content",
        validators=[DataRequired(), Length(min=1, max=FormConstants.NOTE_MAX_LENGTH)],
        render_kw={
            "placeholder": "Enter your note...",
            "rows": 4
        }
    )

    is_internal = SelectField(
        "Note Type",
        choices=[
            ("1", "Internal Note"),
            ("0", "Client-Facing Note")
        ],
        default="1",
        coerce=lambda x: x == "1"
    )