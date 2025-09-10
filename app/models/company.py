from . import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(255))

    # Relationships
    stakeholders = db.relationship("Stakeholder", back_populates="company", lazy=True)
    opportunities = db.relationship("Opportunity", backref="company", lazy=True)

    def get_account_team(self):
        """Get account team members assigned to this company"""
        # Use the ORM relationship and sort by job_title, name
        team_assignments = sorted(self.account_team_assignments, 
                                key=lambda x: (x.user.job_title or '', x.user.name))
        return [{
            'id': assignment.user.id,
            'name': assignment.user.name,
            'email': assignment.user.email,
            'job_title': assignment.user.job_title
        } for assignment in team_assignments]

    def to_dict(self):
        """Convert company to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'website': self.website,
            'stakeholders': [
                {
                    'id': stakeholder.id,
                    'name': stakeholder.name,
                    'job_title': stakeholder.job_title,
                    'email': stakeholder.email,
                }
                for stakeholder in self.stakeholders
            ],
            'account_team': self.get_account_team(),
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
