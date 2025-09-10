from datetime import datetime
from . import db


# Many-to-many table for stakeholder MEDDPICC roles  
stakeholder_meddpicc_roles = db.Table(
    "stakeholder_meddpicc_roles",
    db.Column("stakeholder_id", db.Integer, db.ForeignKey("stakeholders.id"), primary_key=True),
    db.Column("meddpicc_role", db.String(50), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow)
)

# Many-to-many table for stakeholder relationship ownership
stakeholder_relationship_owners = db.Table(
    "stakeholder_relationship_owners", 
    db.Column("stakeholder_id", db.Integer, db.ForeignKey("stakeholders.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow)
)

# Pure assignment table for stakeholder-opportunity relationships
stakeholder_opportunities = db.Table(
    "stakeholder_opportunities",
    db.Column("stakeholder_id", db.Integer, db.ForeignKey("stakeholders.id"), primary_key=True),
    db.Column("opportunity_id", db.Integer, db.ForeignKey("opportunities.id"), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow)
)


class Stakeholder(db.Model):
    """Stakeholder model (formerly Contact) - customer-side contacts with MEDDPICC roles"""
    __tablename__ = "stakeholders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(100))  # Their actual job: "VP Sales", "CTO", etc.
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key to company
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    # Relationships (use back_populates to avoid conflicts)
    company = db.relationship("Company", back_populates="stakeholders")
    
    # MEDDPICC roles are stored directly in the junction table as strings
    # Access via helper methods rather than SQLAlchemy relationship
    
    relationship_owners = db.relationship(
        "User",
        secondary=stakeholder_relationship_owners,
        backref="owned_stakeholder_relationships"
    )
    
    opportunities = db.relationship(
        "Opportunity",
        secondary=stakeholder_opportunities,
        backref="stakeholders"
    )

    def get_meddpicc_role_names(self):
        """Get list of MEDDPICC role names for this stakeholder"""
        result = db.session.execute(
            db.text("""
                SELECT meddpicc_role FROM stakeholder_meddpicc_roles 
                WHERE stakeholder_id = :stakeholder_id
                ORDER BY meddpicc_role
            """),
            {"stakeholder_id": self.id}
        ).fetchall()
        return [row[0] for row in result]
    
    def add_meddpicc_role(self, role_name):
        """Add a MEDDPICC role to this stakeholder"""
        # Check if already exists
        existing = db.session.execute(
            db.text("""
                SELECT 1 FROM stakeholder_meddpicc_roles 
                WHERE stakeholder_id = :stakeholder_id AND meddpicc_role = :role_name
            """),
            {"stakeholder_id": self.id, "role_name": role_name}
        ).fetchone()
        
        if not existing:
            db.session.execute(
                db.text("""
                    INSERT INTO stakeholder_meddpicc_roles (stakeholder_id, meddpicc_role, created_at)
                    VALUES (:stakeholder_id, :role_name, :created_at)
                """),
                {
                    "stakeholder_id": self.id,
                    "role_name": role_name,
                    "created_at": datetime.utcnow()
                }
            )
            db.session.commit()
    
    def remove_meddpicc_role(self, role_name):
        """Remove a MEDDPICC role from this stakeholder"""
        db.session.execute(
            db.text("""
                DELETE FROM stakeholder_meddpicc_roles 
                WHERE stakeholder_id = :stakeholder_id AND meddpicc_role = :role_name
            """),
            {"stakeholder_id": self.id, "role_name": role_name}
        )
        db.session.commit()
    
    def get_relationship_owners(self):
        """Get all users who own relationships with this stakeholder"""
        return [{
            'id': user.id,
            'name': user.name,
            'job_title': user.job_title
        } for user in self.relationship_owners]
    
    def assign_relationship_owner(self, user_id):
        """Assign a user as relationship owner for this stakeholder"""
        from .user import User  # Import here to avoid circular imports
        user = User.query.get(user_id)
        if user and user not in self.relationship_owners:
            self.relationship_owners.append(user)
            db.session.commit()

    def to_dict(self):
        """Convert stakeholder to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'job_title': self.job_title,
            'email': self.email,
            'phone': self.phone,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'meddpicc_roles': self.get_meddpicc_role_names(),
            'relationship_owners': self.get_relationship_owners(),
            'opportunities': [
                {
                    'id': opp.id,
                    'name': opp.name,
                    'stage': opp.stage,
                }
                for opp in self.opportunities
            ]
        }

    def __repr__(self):
        return f"<Stakeholder {self.name} ({self.job_title}) at {self.company.name if self.company else 'Unknown'}>"


# MeddpiccRole class removed - roles are stored as strings in junction table for simplicity