from datetime import datetime
from decimal import Decimal
from . import db


class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Numeric(10, 2))  # Store monetary value in dollars
    probability = db.Column(db.Integer, default=0)  # 0-100 percentage
    expected_close_date = db.Column(db.Date)
    stage = db.Column(db.String(50), default='prospect')  # prospect/qualified/proposal/negotiation/closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    
    @property
    def deal_age(self):
        return (datetime.utcnow() - self.created_at).days
    
    def __repr__(self):
        return f'<Opportunity {self.name}>'