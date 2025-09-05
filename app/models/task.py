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
    
    def __repr__(self):
        return f'<Task {self.description[:50]}>'