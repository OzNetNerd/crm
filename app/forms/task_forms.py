from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import date


class TaskForm(FlaskForm):
    description = TextAreaField(
        'Description',
        validators=[DataRequired(), Length(min=1, max=500)],
        render_kw={'placeholder': 'What needs to be done?', 'rows': 3}
    )
    
    due_date = DateField(
        'Due Date',
        validators=[Optional()],
        default=None
    )
    
    priority = SelectField(
        'Priority',
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium',
        validators=[DataRequired()]
    )
    
    status = SelectField(
        'Status',
        choices=[('todo', 'To Do'), ('in-progress', 'In Progress'), ('complete', 'Complete')],
        default='todo',
        validators=[DataRequired()]
    )
    
    next_step_type = SelectField(
        'Next Step Type',
        choices=[('', 'None'), ('call', 'Call'), ('email', 'Email'), 
                ('meeting', 'Meeting'), ('demo', 'Demo')],
        default='',
        validators=[Optional()]
    )
    
    entity_type = SelectField(
        'Related To',
        choices=[('', 'None'), ('company', 'Company'), 
                ('contact', 'Contact'), ('opportunity', 'Opportunity')],
        default='',
        validators=[Optional()]
    )
    
    entity_id = IntegerField(
        'Entity ID',
        validators=[Optional(), NumberRange(min=1)]
    )
    
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        
        # If entity_type is specified, entity_id must be provided
        if self.entity_type.data and not self.entity_id.data:
            self.entity_id.errors.append('Entity ID is required when entity type is specified')
            return False
        
        # Due date cannot be in the past for new tasks
        if self.due_date.data and self.due_date.data < date.today():
            # Allow past dates for existing tasks being updated
            pass
        
        return True


class QuickTaskForm(FlaskForm):
    """Simplified form for quick task creation"""
    description = StringField(
        'Task',
        validators=[DataRequired(), Length(min=1, max=200)],
        render_kw={'placeholder': 'Add a quick task...', 'class': 'form-control'}
    )
    
    priority = SelectField(
        'Priority',
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )