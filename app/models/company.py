from . import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(255))

    # Relationships
    contacts = db.relationship("Contact", backref="company", lazy=True)
    opportunities = db.relationship("Opportunity", backref="company", lazy=True)

    def to_dict(self):
        """Convert company to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'website': self.website,
            'contacts': [
                {
                    'id': contact.id,
                    'name': contact.name,
                    'role': contact.role,
                    'email': contact.email,
                }
                for contact in self.contacts
            ],
            'opportunities': [
                {
                    'id': opp.id,
                    'name': opp.name,
                    'value': opp.value,
                    'stage': opp.stage,
                    'probability': opp.probability,
                }
                for opp in self.opportunities
            ]
        }

    def __repr__(self):
        return f"<Company {self.name}>"
