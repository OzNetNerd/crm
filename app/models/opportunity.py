from datetime import datetime
from typing import Dict, Any
from . import db
from .base import BaseModel
from ..utils.opportunity_utils import (
    calculate_deal_age,
    calculate_priority_by_value,
    get_pipeline_value,
    get_pipeline_breakdown,
    get_closing_soon,
    get_stage_choices,
    get_stakeholders,
    get_full_account_team,
)


class Opportunity(BaseModel):
    """Opportunity model representing sales opportunities."""

    __tablename__ = "opportunities"
    __display_name__ = "Opportunity"
    __search_config__ = {
        "subtitle_fields": ["value", "stage"],
        "relationships": [("company", "name")],
    }

    # Serialization configuration
    __include_properties__ = ["calculated_priority", "deal_age"]
    __relationship_transforms__ = {
        "stakeholders": lambda self: get_stakeholders(self.id)
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(255),
        nullable=False,
        info={
            "display_label": "Opportunity Name",
            "required": True,
            "form_include": True,
        },
    )
    value = db.Column(
        db.Integer,
        info={
            "display_label": "Deal Value",
            "groupable": True,
            "sortable": True,
            "form_include": True,
            "required": True,
            "priority_ranges": [
                (50000, "high", "High Value ($50K+)"),
                (10000, "medium", "Medium Value ($10K-$50K)"),
                (0, "low", "Low Value (<$10K)"),
            ],
        },
    )
    probability = db.Column(
        db.Integer,
        default=0,
        info={
            "display_label": "Win Probability",
            "groupable": True,
            "sortable": True,
            "unit": "%",
            "min_value": 0,
            "max_value": 100,
            "choices": {
                "0-20": {"label": "0-20%", "description": "Very low probability"},
                "21-40": {"label": "21-40%", "description": "Low probability"},
                "41-60": {"label": "41-60%", "description": "Medium probability"},
                "61-80": {"label": "61-80%", "description": "High probability"},
                "81-100": {"label": "81-100%", "description": "Very high probability"},
            },
        },
    )
    priority = db.Column(
        db.String(50),
        info={
            "display_label": "Priority",
            "choices": {
                "low": {"label": "Low", "description": "Low priority opportunity"},
                "medium": {
                    "label": "Medium",
                    "description": "Medium priority opportunity",
                },
                "high": {"label": "High", "description": "High priority opportunity"},
            },
        },
    )
    expected_close_date = db.Column(
        db.Date,
        info={
            "display_label": "Expected Close Date",
            "groupable": True,
            "sortable": True,
            "form_include": True,
        },
    )
    stage = db.Column(
        db.String(50),
        default="prospect",
        info={
            "display_label": "Stage",
            "groupable": True,
            "sortable": True,
            "form_include": True,
            "required": True,
            "choices": get_stage_choices(),
        },
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id", ondelete="CASCADE"),
        info={"display_label": "Company", "form_include": True, "required": True},
    )
    company = db.relationship("Company", back_populates="opportunities")

    comments = db.Column(
        db.Text, info={"display_label": "Comments", "form_include": True, "rows": 3, "sortable": False}
    )

    # Properties using utility functions
    deal_age = property(lambda self: calculate_deal_age(self.created_at))
    calculated_priority = property(lambda self: calculate_priority_by_value(self.value))

    # Class methods using utility functions
    @classmethod
    def calculate_pipeline_value(cls, stage=None):
        """Calculate total pipeline value for stage."""
        return get_pipeline_value(cls, stage)

    @classmethod
    def get_pipeline_breakdown(cls):
        """Get pipeline value breakdown by stage."""
        return get_pipeline_breakdown(cls)

    @classmethod
    def get_closing_soon(cls, days=7, limit=5):
        """Get opportunities closing soon."""
        return get_closing_soon(cls, days, limit)

    @classmethod
    def get_stage_choices(cls):
        """Get available opportunity stages."""
        return get_stage_choices()

    def get_stakeholders(self):
        """Get stakeholders for this opportunity."""
        return get_stakeholders(self.id)

    def get_full_account_team(self):
        """Get full account team for this opportunity."""
        return get_full_account_team(self.id)

    def get_probability_range(self):
        """Get the probability range for grouping and filtering."""
        if self.probability is None:
            return "0-20%"
        elif self.probability <= 20:
            return "0-20%"
        elif self.probability <= 40:
            return "21-40%"
        elif self.probability <= 60:
            return "41-60%"
        elif self.probability <= 80:
            return "61-80%"
        else:
            return "81-100%"

    def to_display_dict(self) -> Dict[str, Any]:
        """Convert opportunity to dictionary with display fields."""
        result = self.to_dict()

        # Add display-friendly versions using comprehension
        display_fields = ["stage", "priority"]
        for field in display_fields:
            value = getattr(self, field, None)
            result[f"{field}_display"] = (
                value.replace("-", " ").replace("_", " ").title() if value else ""
            )

        return result

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Opportunity {self.name}: ${self.value or 0}>"
