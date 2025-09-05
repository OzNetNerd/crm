from . import db


class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(255))
    
    # Relationships
    contacts = db.relationship('Contact', backref='company', lazy=True)
    opportunities = db.relationship('Opportunity', backref='company', lazy=True)
    
    def __repr__(self):
        return f'<Company {self.name}>'