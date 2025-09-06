from . import db

# Many-to-many relationship table for contacts and opportunities
contact_opportunities = db.Table(
    "contact_opportunities",
    db.Column("contact_id", db.Integer, db.ForeignKey("contacts.id"), primary_key=True),
    db.Column(
        "opportunity_id",
        db.Integer,
        db.ForeignKey("opportunities.id"),
        primary_key=True,
    ),
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

    def __repr__(self):
        return f"<Contact {self.name}>"
