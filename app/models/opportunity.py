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

    def get_stakeholders(self):
        """Get all stakeholders for this opportunity with their MEDDPICC roles"""
        # Use the ORM relationship and sort by name
        sorted_stakeholders = sorted(self.stakeholders, key=lambda s: s.name)
        
        return [{
            'id': stakeholder.id,
            'name': stakeholder.name,
            'job_title': stakeholder.job_title,
            'email': stakeholder.email,
            'phone': stakeholder.phone,
            'meddpicc_roles': stakeholder.get_meddpicc_role_names()  # Use existing method
        } for stakeholder in sorted_stakeholders]

    def get_full_account_team(self):
        """Get full account team including inherited company team and opportunity-specific assignments"""
        # Get company account team members using ORM
        company_team = []
        if self.company:
            for assignment in self.company.account_team_assignments:
                company_team.append({
                    'id': assignment.user.id,
                    'name': assignment.user.name,
                    'email': assignment.user.email,
                    'job_title': assignment.user.job_title,
                    'source': 'company'
                })
        
        # Get opportunity-specific account team members using ORM
        opp_team = []
        for assignment in self.account_team_assignments:
            opp_team.append({
                'id': assignment.user.id,
                'name': assignment.user.name,
                'email': assignment.user.email,
                'job_title': assignment.user.job_title,
                'source': 'opportunity'
            })
        
        # Combine teams and deduplicate (user might be on both company and opportunity teams)
        all_team = {}
        for member in company_team + opp_team:
            user_id = member['id']
            if user_id not in all_team:
                all_team[user_id] = member
            elif all_team[user_id]['source'] == 'company' and member['source'] == 'opportunity':
                # Upgrade source to opportunity if they're on both
                all_team[user_id]['source'] = 'both'
        
        # Sort by job_title, name and return
        return sorted(all_team.values(), key=lambda x: (x['job_title'] or '', x['name']))

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
            'stakeholders': [
                {
                    'id': stakeholder['id'],
                    'name': stakeholder['name'],
                    'job_title': stakeholder['job_title'],
                    'email': stakeholder['email'],
                    'meddpicc_roles': stakeholder['meddpicc_roles']
                }
                for stakeholder in self.get_stakeholders()
            ]
        }

    def __repr__(self):
        return f"<Opportunity {self.name}>"
