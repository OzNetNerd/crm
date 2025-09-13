from typing import Dict, Any, List, Optional
from . import db
from .base import EntityModel
from app.utils.core.model_helpers import auto_serialize


class Company(EntityModel):
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
    
    __entity_config__ = {
        'display_name': 'Companies',
        'display_name_singular': 'Company',  
        'description': 'Manage your company relationships',
        'endpoint_name': 'companies',
        'modal_path': '/modals/Company',
        'show_dashboard_button': True
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(255),
        nullable=False,
        info={
            'display_label': 'Company Name',
            'required': True,
            'groupable': True,
            'form_include': True
        }
    )
    industry = db.Column(
        db.String(100),
        info={
            'display_label': 'Industry',
            'groupable': True,
            'form_include': True,
            'choices': {
                'technology': {
                    'label': 'Technology',
                    'description': 'Software and technology companies'
                },
                'healthcare': {
                    'label': 'Healthcare',
                    'description': 'Medical and healthcare services'
                },
                'finance': {
                    'label': 'Finance',
                    'description': 'Financial services and banking'
                },
                'manufacturing': {
                    'label': 'Manufacturing',
                    'description': 'Manufacturing and production'
                },
                'retail': {
                    'label': 'Retail',
                    'description': 'Retail and e-commerce'
                },
                'education': {
                    'label': 'Education',
                    'description': 'Educational institutions'
                },
                'consulting': {
                    'label': 'Consulting',
                    'description': 'Professional services and consulting'
                },
                'energy': {
                    'label': 'Energy',
                    'description': 'Energy and utilities'
                },
                'other': {
                    'label': 'Other',
                    'description': 'Other industries'
                }
            }
        }
    )
    website = db.Column(
        db.String(255),
        info={
            'display_label': 'Website',
            'url_field': True
        }
    )
    
    size = db.Column(
        db.String(50),
        info={
            'display_label': 'Company Size',
            'groupable': True,
            'choices': {
                'startup': {
                    'label': 'Startup (1-10)',
                    'description': 'Small startup company'
                },
                'small': {
                    'label': 'Small (11-50)',
                    'description': 'Small business'
                },
                'medium': {
                    'label': 'Medium (51-200)',
                    'description': 'Medium-sized company'
                },
                'large': {
                    'label': 'Large (201-1000)',
                    'description': 'Large corporation'
                },
                'enterprise': {
                    'label': 'Enterprise (1000+)',
                    'description': 'Enterprise-level organization'
                }
            }
        }
    )
    
    phone = db.Column(
        db.String(50),
        info={
            'display_label': 'Phone',
            'contact_field': True
        }
    )
    
    address = db.Column(
        db.Text,
        info={
            'display_label': 'Address',
            'rows': 2
        }
    )

    comments = db.Column(
        db.Text,
        info={
            'display_label': 'Comments',
            'form_include': True,
            'rows': 3
        }
    )

    # Relationships
    stakeholders = db.relationship("Stakeholder", back_populates="company", lazy=True)
    opportunities = db.relationship("Opportunity", backref="company", lazy=True)

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
        from app.utils.core.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_choices(cls, 'industry')
    
    @classmethod
    def get_industry_css_class(cls, industry_value: Optional[str]) -> str:
        """
        Get CSS class for an industry value.
        
        Generates appropriate CSS class names for styling industry-specific
        elements in the user interface.
        
        Args:
            industry_value: The industry value to get CSS class for.
                          Can be None for unknown/unset industries.
        
        Returns:
            CSS class string for the given industry value.
            Returns empty string if industry_value is None or invalid.
            
        Example:
            >>> cls = Company.get_industry_css_class('technology')
            >>> print(cls)
            'industry-technology'
        """
        from app.utils.core.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_css_class(cls, 'industry', industry_value)
    
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
            return 'unknown'
        elif stakeholder_count <= 10:
            return 'small'
        elif stakeholder_count <= 50:
            return 'medium'
        else:
            return 'large'

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert company to dictionary for JSON serialization.
        
        Creates a comprehensive dictionary representation including
        all database fields, computed properties, related entities,
        and UI helper fields like CSS classes.
        
        Returns:
            Dictionary containing:
            - All database column values
            - Computed properties (size_category, account_team)
            - Related entity summaries (stakeholders, opportunities)
            - UI helper fields (industry_css_class)
            
        Example:
            >>> company = Company(name="Acme Corp", industry="technology")
            >>> data = company.to_dict()
            >>> print(data['name'])
            'Acme Corp'
            >>> print(data['industry_css_class'])
            'industry-technology'
        """
        # Define properties to include beyond database columns
        include_properties = ["size_category", "account_team"]
        
        # Define custom transforms for relationships and CSS classes
        field_transforms = {
            "stakeholders": lambda _: [
                {
                    "id": stakeholder.id,
                    "name": stakeholder.name,
                    "job_title": stakeholder.job_title,
                    "email": stakeholder.email,
                }
                for stakeholder in self.stakeholders
            ],
            "opportunities": lambda _: [
                {
                    "id": opp.id,
                    "name": opp.name,
                    "value": opp.value,
                    "stage": opp.stage,
                    "probability": opp.probability,
                }
                for opp in self.opportunities
            ]
        }
        
        result = auto_serialize(self, include_properties, field_transforms)
        
        # Add CSS class for industry
        result["industry_css_class"] = self.get_industry_css_class(self.industry) if self.industry else ''
        
        return result

    def to_display_dict(self) -> Dict[str, Any]:
        """
        Convert company to dictionary with pre-formatted display fields.
        
        Extends the basic dictionary representation with formatted
        fields optimized for display in user interfaces. This includes
        formatted dates, currency values, and other UI-specific formatting.
        
        Returns:
            Dictionary with all standard fields plus display-formatted versions
            of fields that benefit from special formatting.
            
        Example:
            >>> company = Company(name="Acme Corp")
            >>> display_data = company.to_display_dict()
            >>> # Contains formatted fields for UI display
        """
        from app.utils.ui.formatters import create_display_dict
        
        # Get base dictionary
        result = self.to_dict()
        
        # Add formatted display fields at source
        display_fields = create_display_dict(self)
        result.update(display_fields)
        
        return result

    def __repr__(self) -> str:
        """Return string representation of the company."""
        return f"<Company {self.name}>"
