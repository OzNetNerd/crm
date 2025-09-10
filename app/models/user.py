from datetime import datetime
from . import db


class User(db.Model):
    """User model for team management"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    role = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.name}>"


class TeamMemberMixin:
    """Reusable mixin for team member functionality following DRY principles"""
    
    # Common team member fields (to be added to team models)
    role = db.Column(db.String(50), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    access_level = db.Column(db.String(20), default='read')
    assigned_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def role_badge_class(self):
        """Get CSS class for role badge"""
        role_classes = {
            'account_manager': 'badge-primary',
            'sales_rep': 'badge-success',
            'engineer': 'badge-info',
            'support': 'badge-warning',
            'manager': 'badge-dark'
        }
        return role_classes.get(self.role, 'badge-secondary')
    
    @property
    def access_level_icon(self):
        """Get icon for access level"""
        icons = {
            'read': 'eye',
            'write': 'edit',
            'admin': 'shield'
        }
        return icons.get(self.access_level, 'user')


class CompanyTeam(db.Model, TeamMemberMixin):
    """Company team members"""
    __tablename__ = "company_teams"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationship fields from mixin
    role = db.Column(db.String(50), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    access_level = db.Column(db.String(20), default='read')
    assigned_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="company_assignments")
    company = db.relationship("Company", backref="team_members")

    # Unique constraint
    __table_args__ = (db.UniqueConstraint('company_id', 'user_id', 'role', name='unique_company_user_role'),)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'role': self.role,
            'is_primary': self.is_primary,
            'access_level': self.access_level,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.user.name if self.user else None,
            'company_name': self.company.name if self.company else None,
            'role_badge_class': self.role_badge_class,
            'access_level_icon': self.access_level_icon,
        }

    def __repr__(self):
        return f"<CompanyTeam {self.user.name if self.user else 'Unknown'} - {self.role}>"


class OpportunityTeam(db.Model, TeamMemberMixin):
    """Opportunity team members"""
    __tablename__ = "opportunity_teams"

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationship fields from mixin
    role = db.Column(db.String(50), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    access_level = db.Column(db.String(20), default='read')
    assigned_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="opportunity_assignments")
    opportunity = db.relationship("Opportunity", backref="team_members")

    # Unique constraint
    __table_args__ = (db.UniqueConstraint('opportunity_id', 'user_id', 'role', name='unique_opportunity_user_role'),)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'opportunity_id': self.opportunity_id,
            'user_id': self.user_id,
            'role': self.role,
            'is_primary': self.is_primary,
            'access_level': self.access_level,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.user.name if self.user else None,
            'opportunity_name': self.opportunity.name if self.opportunity else None,
            'role_badge_class': self.role_badge_class,
            'access_level_icon': self.access_level_icon,
        }

    def __repr__(self):
        return f"<OpportunityTeam {self.user.name if self.user else 'Unknown'} - {self.role}>"


class TaskTeam(db.Model, TeamMemberMixin):
    """Task team members"""
    __tablename__ = "task_teams"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationship fields from mixin
    role = db.Column(db.String(50), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    access_level = db.Column(db.String(20), default='read')
    assigned_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="task_assignments")
    task = db.relationship("Task", backref="team_members")

    # Unique constraint
    __table_args__ = (db.UniqueConstraint('task_id', 'user_id', 'role', name='unique_task_user_role'),)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'role': self.role,
            'is_primary': self.is_primary,
            'access_level': self.access_level,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.user.name if self.user else None,
            'task_description': self.task.description if self.task else None,
            'role_badge_class': self.role_badge_class,
            'access_level_icon': self.access_level_icon,
        }

    def __repr__(self):
        return f"<TaskTeam {self.user.name if self.user else 'Unknown'} - {self.role}>"