"""
Task Modal Form

Explicit form class for Task modals with controlled field ordering and layout.
Layout: Entity (top) -> Description -> Priority/Due Date (side by side) -> Comments
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Optional
from app.models.task import Task
from app.models.company import Company
from app.models.opportunity import Opportunity
from app.models.stakeholder import Stakeholder


class TaskModalForm(FlaskForm):
    """
    Task modal form with explicit field ordering:
    1. Entity (dropdown - Company, Opportunity, or Stakeholder)
    2. Description (required textarea)
    3. Priority (left) and Due Date (right) - side by side
    4. Comments (textarea)
    """

    # Field 1: Entity (dropdown, at top)
    entity = SelectField(
        'Related To',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    # Field 2: Description (required, large text area)
    description = TextAreaField(
        'Description',
        validators=[DataRequired(), Length(max=1000)],
        render_kw={'rows': 3, 'placeholder': 'Describe the task...'}
    )

    # Field 3a: Priority (left side)
    priority = SelectField(
        'Priority',
        validators=[Optional()],
        choices=[]  # Will be populated in __init__
    )

    # Field 3b: Due Date (right side)
    due_date = DateField(
        'Due Date',
        validators=[Optional()],
        render_kw={'type': 'date'}
    )

    # Field 4: Comments (textarea, at bottom)
    comments = TextAreaField(
        'Comments',
        validators=[Optional()],
        render_kw={'rows': 3, 'placeholder': 'Additional notes...'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get priority choices from Task model metadata
        priority_choices = Task.get_field_choices('priority')
        choices = [('', 'Select priority')]
        choices.extend(priority_choices)
        self.priority.choices = choices

        # Build entity choices (companies, opportunities, stakeholders)
        entity_choices = [('', 'Select entity')]

        # Add companies
        try:
            companies = Company.query.order_by(Company.name).all()
            for company in companies:
                entity_choices.append((f'company:{company.id}', f'Company: {company.name}'))
        except:
            pass  # Skip if no companies or DB error

        # Add opportunities
        try:
            opportunities = Opportunity.query.order_by(Opportunity.name).all()
            for opp in opportunities:
                entity_choices.append((f'opportunity:{opp.id}', f'Opportunity: {opp.name}'))
        except:
            pass  # Skip if no opportunities or DB error

        # Add stakeholders
        try:
            stakeholders = Stakeholder.query.order_by(Stakeholder.name).all()
            for stakeholder in stakeholders:
                entity_choices.append((f'stakeholder:{stakeholder.id}', f'Contact: {stakeholder.name}'))
        except:
            pass  # Skip if no stakeholders or DB error

        self.entity.choices = entity_choices