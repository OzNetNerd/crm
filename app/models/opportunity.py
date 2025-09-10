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
        result = db.session.execute(
            db.text("""
                SELECT s.id, s.name, s.job_title, s.email, s.phone
                FROM stakeholders s
                JOIN stakeholder_opportunities so ON s.id = so.stakeholder_id
                WHERE so.opportunity_id = :opportunity_id
                ORDER BY s.name
            """),
            {"opportunity_id": self.id}
        ).fetchall()
        
        stakeholders = []
        for row in result:
            # Get MEDDPICC roles for this stakeholder
            roles_result = db.session.execute(
                db.text("""
                    SELECT meddpicc_role 
                    FROM stakeholder_meddpicc_roles 
                    WHERE stakeholder_id = :stakeholder_id
                    ORDER BY meddpicc_role
                """),
                {"stakeholder_id": row[0]}
            ).fetchall()
            
            stakeholders.append({
                'id': row[0],
                'name': row[1], 
                'job_title': row[2],
                'email': row[3],
                'phone': row[4],
                'meddpicc_roles': [r[0] for r in roles_result]
            })
        
        return stakeholders

    def get_full_account_team(self):
        """Get full account team including inherited company team and opportunity-specific assignments"""
        # Get company account team members
        company_team = db.session.execute(
            db.text("""
                SELECT u.id, u.name, u.email, u.job_title, 'company' as source
                FROM users u
                JOIN company_account_teams cat ON u.id = cat.user_id
                WHERE cat.company_id = :company_id
                ORDER BY u.job_title, u.name
            """),
            {"company_id": self.company_id}
        ).fetchall()
        
        # Get opportunity-specific account team members
        opp_team = db.session.execute(
            db.text("""
                SELECT u.id, u.name, u.email, u.job_title, 'opportunity' as source
                FROM users u
                JOIN opportunity_account_teams oat ON u.id = oat.user_id
                WHERE oat.opportunity_id = :opportunity_id
                ORDER BY u.job_title, u.name
            """),
            {"opportunity_id": self.id}
        ).fetchall()
        
        # Combine teams and deduplicate (user might be on both company and opportunity teams)
        all_team = {}
        for row in list(company_team) + list(opp_team):
            user_id = row[0]
            if user_id not in all_team:
                all_team[user_id] = {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'job_title': row[3],
                    'source': row[4]
                }
            elif all_team[user_id]['source'] == 'company' and row[4] == 'opportunity':
                # Upgrade source to opportunity if they're on both
                all_team[user_id]['source'] = 'both'
        
        return list(all_team.values())

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
