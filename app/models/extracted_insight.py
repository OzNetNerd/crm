from datetime import datetime
from . import db


class ExtractedInsight(db.Model):
    __tablename__ = "extracted_insights"

    id = db.Column(db.Integer, primary_key=True)
    
    # Link to the meeting this insight was extracted from
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id"), nullable=False)
    meeting = db.relationship("Meeting", backref="extracted_insights")
    
    # Type of insight (attendees, technologies, action_items, etc.)
    insight_type = db.Column(db.String(50), nullable=False)
    
    # Extracted data stored as JSON
    extracted_data = db.Column(db.JSON, nullable=False)
    
    # Extraction metadata
    extraction_metadata = db.Column(db.JSON)  # Model used, confidence scores, etc.
    
    # Confidence score (0.0 to 1.0)
    confidence_score = db.Column(db.Float, default=0.0)
    
    # Manual review status
    review_status = db.Column(
        db.String(20), 
        default="pending", 
        nullable=False
    )  # pending, approved, rejected, needs_review
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)

    def to_dict(self):
        """Convert insight to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'meeting_id': self.meeting_id,
            'insight_type': self.insight_type,
            'extracted_data': self.extracted_data,
            'extraction_metadata': self.extraction_metadata,
            'confidence_score': self.confidence_score,
            'review_status': self.review_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
        }

    def __repr__(self):
        return f"<ExtractedInsight {self.insight_type} for Meeting {self.meeting_id}>"