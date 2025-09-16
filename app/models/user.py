from datetime import datetime, date
from typing import Dict, Any
from . import db
from .base import BaseModel


class User(BaseModel):
    """
    User model representing team members in the CRM system.
    
    This model manages internal team members who are assigned to
    manage customer accounts and opportunities. Users serve as the
    single source of truth for job titles and team assignments.
    
    Attributes:
        id: Primary key identifier.
        name: User's full name (required).
        email: Unique email address.
        job_title: Professional title/role (single source of truth).
        created_at: User creation timestamp.
    """

    __tablename__ = "users"
    __display_name__ = "Team Member"
    __display_name_plural__ = "Teams"
    __search_config__ = {
        'subtitle_fields': ['email', 'job_title']
    }
    

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, info={
        'display_label': 'Name'
    })
    email = db.Column(db.String(255), unique=True, info={
        'display_label': 'Email'
    })
    job_title = db.Column(db.String(100), info={
        'display_label': 'Job Title',
        'groupable': True
    })  # Single source of truth for role
    department = db.Column(db.String(100), info={
        'display_label': 'Department',
        'groupable': True,
        'choices': {
            'sales': {
                'label': 'Sales',
                'description': 'Sales and business development'
            },
            'engineering': {
                'label': 'Engineering',
                'description': 'Software development and engineering'
            },
            'marketing': {
                'label': 'Marketing',
                'description': 'Marketing and communications'
            },
            'support': {
                'label': 'Support',
                'description': 'Customer support and success'
            },
            'operations': {
                'label': 'Operations',
                'description': 'Business operations and administration'
            },
            'finance': {
                'label': 'Finance',
                'description': 'Finance and accounting'
            },
            'hr': {
                'label': 'Human Resources',
                'description': 'Human resources and people operations'
            }
        }
    })
    created_at = db.Column(db.DateTime, default=datetime.utcnow, info={'display_label': 'Created At'})


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

    def __repr__(self) -> str:
        """Return string representation of the user."""
        return f"<User {self.name} - {self.job_title}>"


class CompanyAccountTeam(db.Model):
    """Pure assignment table - job_title comes from User model via JOIN"""

    __tablename__ = "company_account_teams"
    __api_enabled__ = False  # Association table - no direct API
    __web_enabled__ = False  # Association table - no web pages

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

        result = {}
        # Serialize all columns
        for column in self.__table__.columns:
            column_name = column.name
            value = getattr(self, column_name, None)
            # Handle datetime/date serialization
            if isinstance(value, (datetime, date)):
                result[column_name] = value.isoformat() if value else None
            else:
                result[column_name] = value

        # Add computed relationship fields
        result["user_name"] = self.user.name if self.user else None
        result["user_job_title"] = self.user.job_title if self.user else None
        result["company_name"] = self.company.name if self.company else None
        
        return result

    def __repr__(self) -> str:
        """Return string representation of the company account team assignment."""
        return f"<CompanyAccountTeam {self.user.name if self.user else 'Unknown'} → {self.company.name if self.company else 'Unknown'}>"


class OpportunityAccountTeam(db.Model):
    """Pure assignment table - job_title comes from User model via JOIN"""

    __tablename__ = "opportunity_account_teams"
    __api_enabled__ = False  # Association table - no direct API
    __web_enabled__ = False  # Association table - no web pages

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
        
        result = {}
        # Serialize all columns
        for column in self.__table__.columns:
            column_name = column.name
            value = getattr(self, column_name, None)
            # Handle datetime/date serialization
            if isinstance(value, (datetime, date)):
                result[column_name] = value.isoformat() if value else None
            else:
                result[column_name] = value

        # Add computed relationship fields
        result["user_name"] = self.user.name if self.user else None
        result["user_job_title"] = self.user.job_title if self.user else None
        result["opportunity_name"] = self.opportunity.name if self.opportunity else None
        
        return result

    def __repr__(self) -> str:
        """Return string representation of the opportunity account team assignment."""
        return f"<OpportunityAccountTeam {self.user.name if self.user else 'Unknown'} → {self.opportunity.name if self.opportunity else 'Unknown'}>"
