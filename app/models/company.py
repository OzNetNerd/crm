from typing import Dict, Any, List
from datetime import datetime
from . import db
from .base import BaseModel


class Company(BaseModel):
    """
    Company model representing business organizations in the CRM system.

    This model stores comprehensive information about companies including
    their basic details, industry classification, contact information,
    and relationships with stakeholders and opportunities. Companies serve
    as the primary organizational entity in the CRM system.

    Attributes:
        id: Primary key identifier.
        name: Company name (required).
        industry: Industry classification from predefined choices.
        website: Company website URL.
        size: Company size category (startup, small, medium, large, enterprise).
        phone: Primary contact phone number.
        address: Physical business address.
        stakeholders: Related stakeholder contacts.
        opportunities: Related business opportunities.
    """

    __tablename__ = "companies"
    __display_name__ = "Company"
    __search_config__ = {
        "subtitle_fields": [
            "industry",
            "size",
        ]  # Auto-detection works well, but be explicit
    }

    # Serialization configuration
    __include_properties__ = ["size_category", "account_team"]
    __relationship_transforms__ = {
        "stakeholders": lambda self: [
            {
                "id": stakeholder.id,
                "name": stakeholder.name,
                "job_title": stakeholder.job_title,
                "email": stakeholder.email,
            }
            for stakeholder in self.stakeholders
        ],
        "opportunities": lambda self: [
            {
                "id": opp.id,
                "name": opp.name,
                "value": opp.value,
                "stage": opp.stage,
                "probability": opp.probability,
            }
            for opp in self.opportunities
        ],
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(255),
        nullable=False,
        info={
            "display_label": "Company Name",
            "required": True,
            "groupable": True,
            "form_include": True,
            "searchable": True,
            "search_title": True,
        },
    )
    industry = db.Column(
        db.String(100),
        info={
            "display_label": "Industry",
            "groupable": True,
            "form_include": True,
            "searchable": True,
            "search_subtitle": True,
            "choices": {
                "technology": {
                    "label": "Technology",
                    "description": "Software and technology companies",
                },
                "healthcare": {
                    "label": "Healthcare",
                    "description": "Medical and healthcare services",
                },
                "finance": {
                    "label": "Finance",
                    "description": "Financial services and banking",
                },
                "manufacturing": {
                    "label": "Manufacturing",
                    "description": "Manufacturing and production",
                },
                "retail": {"label": "Retail", "description": "Retail and e-commerce"},
                "education": {
                    "label": "Education",
                    "description": "Educational institutions",
                },
                "consulting": {
                    "label": "Consulting",
                    "description": "Professional services and consulting",
                },
                "energy": {"label": "Energy", "description": "Energy and utilities"},
                "other": {"label": "Other", "description": "Other industries"},
            },
        },
    )
    website = db.Column(
        db.String(255), info={"display_label": "Website", "url_field": True, "sortable": False}
    )

    size = db.Column(
        db.String(50),
        info={
            "display_label": "Company Size",
            "groupable": True,
            "choices": {
                "startup": {
                    "label": "Startup (1-10)",
                    "description": "Small startup company",
                },
                "small": {"label": "Small (11-50)", "description": "Small business"},
                "medium": {
                    "label": "Medium (51-200)",
                    "description": "Medium-sized company",
                },
                "large": {
                    "label": "Large (201-1,000)",
                    "description": "Large corporation",
                },
                "enterprise": {
                    "label": "Enterprise (1,000+)",
                    "description": "Enterprise-level organization",
                },
            },
        },
    )

    phone = db.Column(
        db.String(50), info={"display_label": "Phone", "contact_field": True, "sortable": False}
    )

    address = db.Column(db.Text, info={"display_label": "Address", "rows": 2, "sortable": False})

    core_rep = db.Column(
        db.String(255),
        nullable=True,
        info={
            "display_label": "Core Rep",
            "form_include": True,
            "searchable": True,
            "groupable": True,
        },
    )

    core_sc = db.Column(
        db.String(255),
        nullable=True,
        info={
            "display_label": "Core SC",
            "form_include": True,
            "searchable": True,
            "groupable": True,
        },
    )

    comments = db.Column(
        db.Text, info={"display_label": "Comments", "form_include": True, "rows": 3, "sortable": False}
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stakeholders = db.relationship("Stakeholder", back_populates="company", lazy=True)
    opportunities = db.relationship("Opportunity", back_populates="company", lazy=True)

    def get_account_team(self) -> List[Dict[str, Any]]:
        """
        Get account team members assigned to this company.

        Retrieves all users assigned to manage this company account,
        sorted by job title and name for consistent ordering.

        Returns:
            List of dictionaries containing team member information:
            - id: User ID
            - name: User's full name
            - email: User's email address
            - job_title: User's job title or None

        Example:
            >>> company = Company.query.first()
            >>> team = company.get_account_team()
            >>> print(team[0])
            {'id': 1, 'name': 'John Doe', 'email': 'john@company.com', 'job_title': 'Account Manager'}
        """
        # Use the ORM relationship and sort by job_title, name
        team_assignments = sorted(
            self.account_team_assignments,
            key=lambda x: (x.user.job_title or "", x.user.name),
        )
        return [
            {
                "id": assignment.user.id,
                "name": assignment.user.name,
                "email": assignment.user.email,
                "job_title": assignment.user.job_title,
            }
            for assignment in team_assignments
        ]

    @classmethod
    def get_industry_choices(cls) -> Dict[str, Dict[str, str]]:
        """
        Get industry choices from model metadata.

        Retrieves the available industry options defined in the model's
        field configuration for use in forms and validation.

        Returns:
            Dictionary mapping industry keys to their display information:
            - label: Human-readable industry name
            - description: Detailed industry description

        Example:
            >>> choices = Company.get_industry_choices()
            >>> print(choices['technology'])
            {'label': 'Technology', 'description': 'Software and technology companies'}
        """
        # Get choices directly from column info
        return cls.industry.info.get("choices", {})

    @property
    def size_category(self) -> str:
        """
        Calculate company size based on number of stakeholders.

        Automatically determines company size category by counting
        the number of stakeholders associated with the company.
        This provides a dynamic size assessment beyond the manually
        set size field.

        Returns:
            Size category string: 'unknown', 'small', 'medium', or 'large'.
            - unknown: No stakeholders
            - small: 1-10 stakeholders
            - medium: 11-50 stakeholders
            - large: 51+ stakeholders

        Example:
            >>> company = Company(name="Test Corp")
            >>> company.size_category
            'unknown'
        """
        stakeholder_count = len(self.stakeholders) if self.stakeholders else 0
        if stakeholder_count == 0:
            return "unknown"
        elif stakeholder_count <= 10:
            return "small"
        elif stakeholder_count <= 50:
            return "medium"
        else:
            return "large"

    def __repr__(self) -> str:
        """Return string representation of the company."""
        return f"<Company {self.name}>"
