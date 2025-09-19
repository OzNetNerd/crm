from datetime import datetime
from . import db
from .base import BaseModel


# Many-to-many table for stakeholder MEDDPICC roles
stakeholder_meddpicc_roles = db.Table(
    "stakeholder_meddpicc_roles",
    db.Column(
        "stakeholder_id", db.Integer, db.ForeignKey("stakeholders.id"), primary_key=True
    ),
    db.Column("meddpicc_role", db.String(50), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow),
)

# Many-to-many table for stakeholder relationship ownership
stakeholder_relationship_owners = db.Table(
    "stakeholder_relationship_owners",
    db.Column(
        "stakeholder_id", db.Integer, db.ForeignKey("stakeholders.id"), primary_key=True
    ),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("created_at", db.DateTime, default=datetime.utcnow),
)

# Pure assignment table for stakeholder-opportunity relationships
stakeholder_opportunities = db.Table(
    "stakeholder_opportunities",
    db.Column(
        "stakeholder_id", db.Integer, db.ForeignKey("stakeholders.id"), primary_key=True
    ),
    db.Column(
        "opportunity_id",
        db.Integer,
        db.ForeignKey("opportunities.id"),
        primary_key=True,
    ),
    db.Column("created_at", db.DateTime, default=datetime.utcnow),
)


class Stakeholder(BaseModel):
    """
    Stakeholder model representing customer-side contacts in the CRM system.

    This model manages stakeholder relationships including MEDDPICC role tracking,
    opportunity associations, and relationship ownership. Stakeholders are
    individuals within customer organizations who influence or participate
    in business opportunities.

    Attributes:
        id: Primary key identifier.
        name: Stakeholder full name (required).
        job_title: Professional title/position.
        email: Primary email address.
        phone: Contact phone number.
        company_id: Associated company foreign key.
        created_at: Stakeholder creation timestamp.
    """

    __tablename__ = "stakeholders"
    __display_name__ = "Stakeholder"
    __search_config__ = {
        "subtitle_fields": ["job_title", "email"],
        "relationships": [("company", "name")],
    }

    # Serialization configuration
    __include_properties__ = [
        "contact_info_status",
        "meddpicc_roles",
        "relationship_owners",
    ]
    __relationship_transforms__ = {
        "meddpicc_roles": lambda self: self.get_meddpicc_role_names(),
        "relationship_owners": lambda self: self.get_relationship_owners(),
        "opportunities": lambda self: [
            {
                "id": opp.id,
                "name": opp.name,
                "stage": opp.stage,
            }
            for opp in self.opportunities
        ],
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(255),
        nullable=False,
        info={"display_label": "Full Name", "required": True, "form_include": True},
    )
    job_title = db.Column(
        db.String(100),
        info={
            "display_label": "Job Title",
            "groupable": True,
            "common_roles": {
                "ceo": {"label": "CEO", "description": "Chief Executive Officer"},
                "cto": {"label": "CTO", "description": "Chief Technology Officer"},
                "vp_sales": {
                    "label": "VP Sales",
                    "description": "Vice President of Sales",
                },
                "director": {
                    "label": "Director",
                    "description": "Director level management",
                },
                "manager": {"label": "Manager", "description": "Manager level role"},
            },
        },
    )  # Their actual job: "VP Sales", "CTO", etc.

    # Virtual field for forms only - MEDDPICC roles are stored in junction table
    meddpicc_role = db.Column(
        db.String(50),
        info={
            "display_label": "MEDDPICC Role",
            "form_exclude": True,  # Don't include in auto-generated forms
            "choices": {
                "economic_buyer": {
                    "label": "Economic Buyer",
                    "description": "Person who controls the budget",
                },
                "decision_maker": {
                    "label": "Decision Maker",
                    "description": "Person who makes the final decision",
                },
                "influencer": {
                    "label": "Influencer",
                    "description": "Person who influences the decision",
                },
                "champion": {
                    "label": "Champion",
                    "description": "Internal advocate for the solution",
                },
                "user": {"label": "User", "description": "End user of the solution"},
                "other": {"label": "Other", "description": "Other role type"},
            },
        },
    )

    email = db.Column(
        db.String(255),
        info={
            "display_label": "Email Address",
            "contact_field": True,
            "icon": "envelope",
            "form_include": True,
            "required": True,
        },
    )
    phone = db.Column(
        db.String(50),
        info={"display_label": "Phone Number", "contact_field": True, "icon": "phone", "sortable": False},
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key to company
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        info={
            "display_label": "Company",
            "groupable": True,
            "filterable": True,
            "relationship_field": "company",
            "relationship_display_field": "name",
            "form_include": True,
            "required": True,
            "choices_source": "companies",  # Dynamically load companies
        },
    )

    comments = db.Column(
        db.Text, info={"display_label": "Comments", "form_include": True, "rows": 3, "sortable": False}
    )

    # Relationships (use back_populates to avoid conflicts)
    company = db.relationship("Company", back_populates="stakeholders")

    # MEDDPICC roles are stored directly in the junction table as strings
    # Access via helper methods rather than SQLAlchemy relationship

    relationship_owners = db.relationship(
        "User",
        secondary=stakeholder_relationship_owners,
        backref="owned_stakeholder_relationships",
    )

    opportunities = db.relationship(
        "Opportunity", secondary=stakeholder_opportunities, backref="stakeholders"
    )

    def get_meddpicc_role_names(self):
        """Get list of MEDDPICC role names for this stakeholder"""
        result = (
            db.session.query(stakeholder_meddpicc_roles.c.meddpicc_role)
            .filter(stakeholder_meddpicc_roles.c.stakeholder_id == self.id)
            .order_by(stakeholder_meddpicc_roles.c.meddpicc_role)
            .all()
        )
        return [row[0] for row in result]

    def add_meddpicc_role(self, role_name):
        """Add a MEDDPICC role to this stakeholder"""
        # Check if already exists using ORM
        existing = (
            db.session.query(stakeholder_meddpicc_roles)
            .filter(stakeholder_meddpicc_roles.c.stakeholder_id == self.id)
            .filter(stakeholder_meddpicc_roles.c.meddpicc_role == role_name)
            .first()
        )

        if not existing:
            # Insert new role using ORM
            insert_stmt = stakeholder_meddpicc_roles.insert().values(
                stakeholder_id=self.id,
                meddpicc_role=role_name,
                created_at=datetime.utcnow(),
            )
            db.session.execute(insert_stmt)
            db.session.commit()

    def remove_meddpicc_role(self, role_name):
        """Remove a MEDDPICC role from this stakeholder"""
        delete_stmt = stakeholder_meddpicc_roles.delete().where(
            (stakeholder_meddpicc_roles.c.stakeholder_id == self.id)
            & (stakeholder_meddpicc_roles.c.meddpicc_role == role_name)
        )
        db.session.execute(delete_stmt)
        db.session.commit()

    def get_relationship_owners(self):
        """Get all users who own relationships with this stakeholder"""
        return [
            {"id": user.id, "name": user.name, "job_title": user.job_title}
            for user in self.relationship_owners
        ]

    def assign_relationship_owner(self, user_id):
        """Assign a user as relationship owner for this stakeholder"""
        from .user import User  # Import here to avoid circular imports

        user = User.query.get(user_id)
        if user and user not in self.relationship_owners:
            self.relationship_owners.append(user)
            db.session.commit()

    def to_dict(self):
        """Convert stakeholder to dictionary for JSON serialization"""
        result = super().to_dict()

        # Add computed company name
        result["company_name"] = self.company.name if self.company else None

        return result

    def to_display_dict(self):
        """Convert stakeholder to dictionary with pre-formatted display fields"""
        # For now, just return the base dictionary
        # Templates will handle formatting using Jinja2 macros
        return self.to_dict()

    @property
    def contact_info_status(self):
        """Calculate contact info completeness"""
        has_email = bool(self.email)
        has_phone = bool(self.phone)

        if has_email and has_phone:
            return "complete"
        elif has_email:
            return "email_only"
        elif has_phone:
            return "phone_only"
        else:
            return "missing"

    def __repr__(self) -> str:
        """Return string representation of the stakeholder."""
        return f"<Stakeholder {self.name} ({self.job_title}) at {self.company.name if self.company else 'Unknown'}>"


# MeddpiccRole class removed - roles are stored as strings in junction table for simplicity
