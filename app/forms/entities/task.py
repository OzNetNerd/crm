"""
Task form - For creating and editing tasks.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Optional, Length
from app.models import Task, User, Company, Opportunity


class TaskForm(FlaskForm):
    """Form for creating/editing tasks."""

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

    task_type = SelectField(
        'Task Type',
        choices=[
            ('', 'Select Type'),
            ('follow_up', 'Follow Up'),
            ('meeting', 'Meeting'),
            ('call', 'Phone Call'),
            ('email', 'Email'),
            ('proposal', 'Proposal'),
            ('demo', 'Demo'),
            ('review', 'Review'),
            ('other', 'Other')
        ],
        validators=[DataRequired()]
    )

    status = SelectField(
        'Status',
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending',
        validators=[DataRequired()]
    )

    priority = SelectField(
        'Priority',
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        default='medium',
        validators=[DataRequired()]
    )

    due_date = DateField(
        'Due Date',
        validators=[Optional()],
        format='%Y-%m-%d'
    )

    # Related entities
    assigned_to_id = SelectField(
        'Assigned To',
        coerce=int,
        validators=[Optional()]
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

        # Populate user choices
        users = User.query.order_by(User.name).all()
        self.assigned_to_id.choices = [(0, 'Unassigned')] + [
            (u.id, u.name) for u in users
        ]

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