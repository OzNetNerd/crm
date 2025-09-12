from . import db


class Company(db.Model):
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
            'required': True
        }
    )
    industry = db.Column(
        db.String(100),
        info={
            'display_label': 'Industry',
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

    # Relationships
    stakeholders = db.relationship("Stakeholder", back_populates="company", lazy=True)
    opportunities = db.relationship("Opportunity", backref="company", lazy=True)

    def get_account_team(self):
        """Get account team members assigned to this company"""
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
    def get_industry_choices(cls):
        """Get industry choices from model metadata"""
        from app.utils.core.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_choices(cls, 'industry')
    
    @classmethod
    def get_industry_css_class(cls, industry_value):
        """Get CSS class for an industry value"""
        from app.utils.core.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_css_class(cls, 'industry', industry_value)
    
    @property
    def size_category(self):
        """Calculate company size based on number of stakeholders"""
        stakeholder_count = len(self.stakeholders) if self.stakeholders else 0
        if stakeholder_count == 0:
            return 'unknown'
        elif stakeholder_count <= 10:
            return 'small'
        elif stakeholder_count <= 50:
            return 'medium'
        else:
            return 'large'

    def to_dict(self):
        """Convert company to dictionary for JSON serialization"""
        from app.utils.model_helpers import auto_serialize
        
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

    def __repr__(self):
        return f"<Company {self.name}>"
