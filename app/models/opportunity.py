from datetime import datetime
from . import db


class Opportunity(db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Integer)  # Store monetary value in whole dollars
    probability = db.Column(db.Integer, default=0)  # 0-100 percentage
    expected_close_date = db.Column(db.Date)
    stage = db.Column(
        db.String(50), default="prospect"
    )  # prospect/qualified/proposal/negotiation/closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    @property
    def deal_age(self):
        return (datetime.utcnow() - self.created_at).days

    def to_dict(self):
        """Convert opportunity to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'value': float(self.value) if self.value else None,
            'probability': self.probability,
            'expected_close_date': self.expected_close_date.isoformat() if self.expected_close_date else None,
            'stage': self.stage,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'deal_age': self.deal_age,
            'created_at': self.created_at.isoformat(),
            'contacts': [
                {
                    'id': contact.id,
                    'name': contact.name,
                    'role': contact.role,
                    'email': contact.email,
                }
                for contact in self.contacts
            ]
        }

    def __repr__(self):
        return f"<Opportunity {self.name}>"
