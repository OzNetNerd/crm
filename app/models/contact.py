from . import db

# Enhanced many-to-many relationship table for contacts and opportunities with stakeholder roles
contact_opportunities = db.Table(
    "contact_opportunities",
    db.Column("contact_id", db.Integer, db.ForeignKey("contacts.id"), primary_key=True),
    db.Column(
        "opportunity_id",
        db.Integer,
        db.ForeignKey("opportunities.id"),
        primary_key=True,
    ),
    db.Column("role", db.String(50)),  # 'stakeholder', 'decision_maker', 'influencer', 'champion'
    db.Column("is_primary", db.Boolean, default=False),
)


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))

    # Foreign keys
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    # Many-to-many relationships
    opportunities = db.relationship(
        "Opportunity",
        secondary=contact_opportunities,
        lazy="subquery",
        backref=db.backref("contacts", lazy=True),
    )

    def get_stakeholder_role(self, opportunity_id):
        """Get the stakeholder role for this contact on a specific opportunity"""
        result = db.session.execute(
            db.text("""
                SELECT role FROM contact_opportunities 
                WHERE contact_id = :contact_id AND opportunity_id = :opportunity_id
            """),
            {"contact_id": self.id, "opportunity_id": opportunity_id}
        ).fetchone()
        return result[0] if result else None

    def set_stakeholder_role(self, opportunity_id, role, is_primary=False):
        """Set the stakeholder role for this contact on a specific opportunity"""
        # Check if relationship exists
        existing = db.session.execute(
            db.text("""
                SELECT 1 FROM contact_opportunities 
                WHERE contact_id = :contact_id AND opportunity_id = :opportunity_id
            """),
            {"contact_id": self.id, "opportunity_id": opportunity_id}
        ).fetchone()
        
        if existing:
            # Update existing relationship
            db.session.execute(
                db.text("""
                    UPDATE contact_opportunities 
                    SET role = :role, is_primary = :is_primary
                    WHERE contact_id = :contact_id AND opportunity_id = :opportunity_id
                """),
                {
                    "role": role,
                    "is_primary": is_primary,
                    "contact_id": self.id, 
                    "opportunity_id": opportunity_id
                }
            )
        else:
            # Insert new relationship
            db.session.execute(
                db.text("""
                    INSERT INTO contact_opportunities (contact_id, opportunity_id, role, is_primary)
                    VALUES (:contact_id, :opportunity_id, :role, :is_primary)
                """),
                {
                    "contact_id": self.id,
                    "opportunity_id": opportunity_id,
                    "role": role,
                    "is_primary": is_primary
                }
            )
        db.session.commit()

    def is_primary_stakeholder(self, opportunity_id):
        """Check if this contact is the primary stakeholder for an opportunity"""
        result = db.session.execute(
            db.text("""
                SELECT is_primary FROM contact_opportunities 
                WHERE contact_id = :contact_id AND opportunity_id = :opportunity_id
            """),
            {"contact_id": self.id, "opportunity_id": opportunity_id}
        ).fetchone()
        return bool(result[0]) if result else False

    def to_dict(self):
        """Convert contact to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'email': self.email,
            'phone': self.phone,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'opportunities': [
                {
                    'id': opp.id,
                    'name': opp.name,
                    'value': opp.value,
                    'stage': opp.stage,
                }
                for opp in self.opportunities
            ]
        }

    def __repr__(self):
        return f"<Contact {self.name}>"
