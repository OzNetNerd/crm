from datetime import datetime
from . import db


class Meeting(db.Model):
    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    transcript = db.Column(db.Text, nullable=False)  # Original meeting content
    file_path = db.Column(db.String(500))  # Path to uploaded file if any

    # Analysis status tracking
    analysis_status = db.Column(
        db.String(20), default="pending", nullable=False
    )  # pending, processing, completed, failed

    # Relationships
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    company = db.relationship("Company", backref="meetings")

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyzed_at = db.Column(db.DateTime)  # When LLM analysis completed

    def to_dict(self):
        """Convert meeting to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "transcript": self.transcript,
            "file_path": self.file_path,
            "analysis_status": self.analysis_status,
            "company_id": self.company_id,
            "company_name": self.company.name if self.company else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
        }

    def __repr__(self):
        return f"<Meeting {self.title}>"
