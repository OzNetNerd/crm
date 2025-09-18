"""
Task form - For creating and editing tasks.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, HiddenField, RadioField, ValidationError
from wtforms.validators import DataRequired, Optional, Length
from app.models import Task, User, Company, Opportunity


class TaskForm(FlaskForm):
    """Form for creating/editing tasks."""

    # Task category selector
    task_category = RadioField(
        'Task Category',
        choices=[
            ('opportunity', 'Opportunity'),
            ('internal', 'Internal')
        ],
        default='opportunity',
        validators=[DataRequired()]
    )

    name = StringField(
        'Task Name',
        validators=[DataRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "Enter task name"}
    )

    description = TextAreaField(
        'Description',
        validators=[Optional()],
        render_kw={"placeholder": "Task description", "rows": 4}
    )

    task_type = StringField(
        'Task Type',
        validators=[DataRequired()],
        render_kw={
            "data-search-type": "task_type",
            "placeholder": "Search task types...",
            "autocomplete": "off"
        }
    )

    status = StringField(
        'Status',
        validators=[DataRequired()],
        render_kw={
            "data-search-type": "task_status",
            "placeholder": "Search status...",
            "autocomplete": "off",
            "data-default": "pending"
        }
    )

    priority = StringField(
        'Priority',
        validators=[DataRequired()],
        render_kw={
            "data-search-type": "task_priority",
            "placeholder": "Search priority...",
            "autocomplete": "off",
            "data-default": "medium"
        }
    )

    due_date = DateField(
        'Due Date',
        validators=[Optional()],
        format='%Y-%m-%d'
    )

    # Related entities
    assigned_to_id = StringField(
        'Assigned To',
        validators=[Optional()],
        render_kw={
            "data-search-type": "assignment",
            "placeholder": "Search assignees...",
            "autocomplete": "off"
        }
    )

    company_id = SelectField(
        'Company',
        coerce=int,
        validators=[Optional()]
    )

    opportunity_id = SelectField(
        'Opportunity',
        coerce=int,
        validators=[Optional()]
    )

    parent_task_id = HiddenField('Parent Task ID')

    def __init__(self, *args, **kwargs):
        """Initialize form with dynamic choices."""
        super().__init__(*args, **kwargs)

        # Populate company choices
        companies = Company.query.order_by(Company.name).all()
        self.company_id.choices = [(0, 'No Company')] + [
            (c.id, c.name) for c in companies
        ]

        # Populate opportunity choices
        opportunities = Opportunity.query.order_by(Opportunity.name).all()
        self.opportunity_id.choices = [(0, 'No Opportunity')] + [
            (o.id, o.name) for o in opportunities
        ]

    def validate_company_id(self, field):
        """Validate that Company is required for Opportunity tasks."""
        if self.task_category.data == 'opportunity' and (not field.data or field.data == 0):
            raise ValidationError('Company is required for Opportunity tasks.')

    def get_display_fields(self):
        """Define field order for modal display."""
        return [
            'task_category',        # Radio buttons at top
            'company_id',           # Company (conditional)
            'opportunity_id',       # Opportunity (conditional)
            'name',                 # Task Name
            'description',          # Description
            'task_type',           # Task Type (first in inline group)
            'priority',            # Priority (second in inline group)
            'status',              # Status (third in inline group)
            'due_date',            # Due Date with enhancements
            'assigned_to_id'       # Assigned To
            # Note: parent_task_id is excluded (HiddenField should not display)
        ]