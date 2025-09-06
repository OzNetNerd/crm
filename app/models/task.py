from datetime import datetime
from . import db


class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(10), default='medium')  # high/medium/low
    status = db.Column(db.String(20), default='todo')  # todo/in-progress/complete
    next_step_type = db.Column(db.String(20))  # meeting/demo/call/email
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Polymorphic relationship - can link to any entity
    entity_type = db.Column(db.String(50))  # 'company', 'contact', 'opportunity'
    entity_id = db.Column(db.Integer)
    
    # Parent/child task relationships
    task_type = db.Column(db.String(20), default='standalone')  # standalone/parent/child
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    sequence_order = db.Column(db.Integer)
    dependency_type = db.Column(db.String(20))  # sequential/parallel
    
    # Relationships
    parent_task = db.relationship('Task', remote_side=[id], backref='child_tasks')
    
    @property
    def is_overdue(self):
        if not self.due_date or self.status == 'complete':
            return False
        return self.due_date < datetime.utcnow().date()
    
    @property
    def entity_name(self):
        if not self.entity_type or not self.entity_id:
            return None
        
        if self.entity_type == 'company':
            from .company import Company
            entity = Company.query.get(self.entity_id)
        elif self.entity_type == 'contact':
            from .contact import Contact
            entity = Contact.query.get(self.entity_id)
        elif self.entity_type == 'opportunity':
            from .opportunity import Opportunity
            entity = Opportunity.query.get(self.entity_id)
        else:
            return None
        
        return entity.name if entity else None
    
    @property
    def opportunity_value(self):
        if self.entity_type == 'opportunity' and self.entity_id:
            from .opportunity import Opportunity
            opportunity = Opportunity.query.get(self.entity_id)
            return opportunity.value if opportunity else None
        return None
    
    @property
    def company_name(self):
        """Get company name regardless of entity type"""
        if self.entity_type == 'company' and self.entity_id:
            from .company import Company
            company = Company.query.get(self.entity_id)
            return company.name if company else None
        elif self.entity_type == 'contact' and self.entity_id:
            from .contact import Contact
            contact = Contact.query.get(self.entity_id)
            return contact.company.name if contact and contact.company else None
        elif self.entity_type == 'opportunity' and self.entity_id:
            from .opportunity import Opportunity
            opportunity = Opportunity.query.get(self.entity_id)
            return opportunity.company.name if opportunity and opportunity.company else None
        return None
    
    @property
    def opportunity_name(self):
        """Get opportunity name if task is linked to an opportunity or contact with opportunities"""
        if self.entity_type == 'opportunity' and self.entity_id:
            from .opportunity import Opportunity
            opportunity = Opportunity.query.get(self.entity_id)
            return opportunity.name if opportunity else None
        return None
    
    @property
    def opportunity_stage(self):
        """Get opportunity stage if task is linked to an opportunity"""
        if self.entity_type == 'opportunity' and self.entity_id:
            from .opportunity import Opportunity
            opportunity = Opportunity.query.get(self.entity_id)
            return opportunity.stage if opportunity else None
        return None
    
    def __repr__(self):
        return f'<Task {self.description[:50]}>'