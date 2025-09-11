from datetime import datetime
from . import db


class User(db.Model):
    """User model for account team members - single source of truth for job titles"""

    __tablename__ = "users"
    
    __entity_config__ = {
        'display_name': 'Teams',
        'display_name_singular': 'Team Member',
        'description': 'Manage your team members',
        'icon': 'users',
        'endpoint_name': 'teams',
        'modal_path': '/modals/User'
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    job_title = db.Column(db.String(100))  # Single source of truth for role
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        from app.utils.model_helpers import auto_serialize
        return auto_serialize(self)

    def get_company_assignments(self):
        """Get all companies this user is assigned to"""
        assignments = (
            db.session.query(CompanyAccountTeam).filter_by(user_id=self.id).all()
        )
        return [{"company_id": a.company_id, "company": a.company} for a in assignments]

    def get_opportunity_assignments(self):
        """Get all opportunities this user is assigned to"""
        assignments = (
            db.session.query(OpportunityAccountTeam).filter_by(user_id=self.id).all()
        )
        return [
            {"opportunity_id": a.opportunity_id, "opportunity": a.opportunity}
            for a in assignments
        ]

    def get_owned_stakeholder_relationships(self):
        """Get all stakeholders this user owns relationships with"""
        # Use ORM relationship and sort by name
        sorted_stakeholders = sorted(
            self.owned_stakeholder_relationships, key=lambda s: s.name
        )

        return [
            {
                "stakeholder_id": stakeholder.id,
                "stakeholder_name": stakeholder.name,
                "stakeholder_job_title": stakeholder.job_title,
            }
            for stakeholder in sorted_stakeholders
        ]

    def __repr__(self):
        return f"<User {self.name} - {self.job_title}>"


class CompanyAccountTeam(db.Model):
    """Pure assignment table - job_title comes from User model via JOIN"""

    __tablename__ = "company_account_teams"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="company_assignments")
    company = db.relationship("Company", backref="account_team_assignments")

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        from app.utils.model_helpers import auto_serialize
        
        result = auto_serialize(self)
        
        # Add computed relationship fields
        result["user_name"] = self.user.name if self.user else None
        result["user_job_title"] = self.user.job_title if self.user else None
        result["company_name"] = self.company.name if self.company else None
        
        return result

    def __repr__(self):
        return f"<CompanyAccountTeam {self.user.name if self.user else 'Unknown'} → {self.company.name if self.company else 'Unknown'}>"


class OpportunityAccountTeam(db.Model):
    """Pure assignment table - job_title comes from User model via JOIN"""

    __tablename__ = "opportunity_account_teams"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    opportunity_id = db.Column(
        db.Integer,
        db.ForeignKey("opportunities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="opportunity_assignments")
    opportunity = db.relationship("Opportunity", backref="account_team_assignments")

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        from app.utils.model_helpers import auto_serialize
        
        result = auto_serialize(self)
        
        # Add computed relationship fields
        result["user_name"] = self.user.name if self.user else None
        result["user_job_title"] = self.user.job_title if self.user else None
        result["opportunity_name"] = self.opportunity.name if self.opportunity else None
        
        return result

    def __repr__(self):
        return f"<OpportunityAccountTeam {self.user.name if self.user else 'Unknown'} → {self.opportunity.name if self.opportunity else 'Unknown'}>"
