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
        """Get all stakeholders for this opportunity with their roles"""
        result = db.session.execute(
            db.text("""
                SELECT c.id, c.name, c.role as job_role, c.email, 
                       co.role as stakeholder_role, co.is_primary
                FROM contacts c
                JOIN contact_opportunities co ON c.id = co.contact_id
                WHERE co.opportunity_id = :opportunity_id
                ORDER BY co.is_primary DESC, co.role ASC
            """),
            {"opportunity_id": self.id}
        ).fetchall()
        
        return [{
            'id': row[0],
            'name': row[1], 
            'job_role': row[2],
            'email': row[3],
            'stakeholder_role': row[4],
            'is_primary': bool(row[5])
        } for row in result]

    def get_primary_stakeholder(self):
        """Get the primary stakeholder for this opportunity"""
        result = db.session.execute(
            db.text("""
                SELECT c.id, c.name, c.email, co.role as stakeholder_role
                FROM contacts c
                JOIN contact_opportunities co ON c.id = co.contact_id
                WHERE co.opportunity_id = :opportunity_id AND co.is_primary = 1
                LIMIT 1
            """),
            {"opportunity_id": self.id}
        ).fetchone()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'stakeholder_role': result[3]
            }
        return None

    def get_full_team(self):
        """Get full team including company team and opportunity-specific team"""
        # Get company team members
        company_team = db.session.execute(
            db.text("""
                SELECT u.id, u.name, u.email, ct.role, ct.is_primary, ct.access_level, 'company' as source
                FROM users u
                JOIN company_teams ct ON u.id = ct.user_id
                WHERE ct.company_id = :company_id
                ORDER BY ct.is_primary DESC, ct.role ASC
            """),
            {"company_id": self.company_id}
        ).fetchall()
        
        # Get opportunity-specific team members
        opp_team = db.session.execute(
            db.text("""
                SELECT u.id, u.name, u.email, ot.role, ot.is_primary, ot.access_level, 'opportunity' as source
                FROM users u
                JOIN opportunity_teams ot ON u.id = ot.user_id
                WHERE ot.opportunity_id = :opportunity_id
                ORDER BY ot.is_primary DESC, ot.role ASC
            """),
            {"opportunity_id": self.id}
        ).fetchall()
        
        # Combine teams
        all_team = []
        for row in list(company_team) + list(opp_team):
            all_team.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'role': row[3],
                'is_primary': bool(row[4]),
                'access_level': row[5],
                'source': row[6]
            })
        
        return all_team

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
