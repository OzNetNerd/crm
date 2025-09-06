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


class CompanyForm(FlaskForm):
    name = StringField(
        "Company Name",
        validators=[DataRequired(), Length(min=1, max=255)],
        render_kw={"placeholder": "Enter company name..."},
    )

    industry = StringField(
        "Industry",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g., Technology, Healthcare, Finance..."},
    )

    website = StringField(
        "Website",
        validators=[
            Optional(),
            URL(message="Please enter a valid URL"),
            Length(max=255),
        ],
        render_kw={"placeholder": "https://example.com"},
    )


class ContactForm(FlaskForm):
    name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=1, max=255)],
        render_kw={"placeholder": "Enter contact name..."},
    )

    role = StringField(
        "Role/Title",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g., CEO, Sales Manager, Developer..."},
    )

    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email(message="Please enter a valid email address"),
            Length(max=255),
        ],
        render_kw={"placeholder": "contact@company.com"},
    )

    phone = StringField(
        "Phone",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "+1 (555) 123-4567"},
    )

    company_id = IntegerField(
        "Company",
        validators=[DataRequired(), NumberRange(min=1)],
        render_kw={"class": "form-select"},
    )


class OpportunityForm(FlaskForm):
    name = StringField(
        "Opportunity Name",
        validators=[DataRequired(), Length(min=1, max=255)],
        render_kw={"placeholder": "Enter opportunity name..."},
    )

    company_id = IntegerField(
        "Company", validators=[DataRequired(), NumberRange(min=1)]
    )

    value = DecimalField(
        "Value ($)",
        validators=[Optional(), NumberRange(min=0)],
        places=2,
        render_kw={"placeholder": "0.00", "step": "0.01"},
    )

    probability = IntegerField(
        "Probability (%)",
        validators=[Optional(), NumberRange(min=0, max=100)],
        default=0,
        render_kw={"placeholder": "0", "min": "0", "max": "100"},
    )

    expected_close_date = DateField("Expected Close Date", validators=[Optional()])

    stage = SelectField(
        "Stage",
        choices=[
            ("prospect", "Prospect"),
            ("qualified", "Qualified"),
            ("proposal", "Proposal"),
            ("negotiation", "Negotiation"),
            ("closed", "Closed"),
        ],
        default="prospect",
        validators=[DataRequired()],
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
            ("contact", "Contact"),
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
