from . import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(255), 
        nullable=False,
        info={
            'display_label': 'Company Name',
            'sortable': True,
            'required': True
        }
    )
    industry = db.Column(
        db.String(100),
        info={
            'display_label': 'Industry',
            'groupable': True,
            'sortable': True,
            'choices': {
                'technology': {
                    'label': 'Technology',
                    'css_class': 'industry-technology',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Software and technology companies',
                    'icon': 'computer-desktop',
                    'order': 1
                },
                'healthcare': {
                    'label': 'Healthcare',
                    'css_class': 'industry-healthcare',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Medical and healthcare services',
                    'icon': 'heart',
                    'order': 2
                },
                'finance': {
                    'label': 'Finance',
                    'css_class': 'industry-finance',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Financial services and banking',
                    'icon': 'currency-dollar',
                    'order': 3
                },
                'manufacturing': {
                    'label': 'Manufacturing',
                    'css_class': 'industry-manufacturing',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Manufacturing and production',
                    'icon': 'cog',
                    'order': 4
                },
                'retail': {
                    'label': 'Retail',
                    'css_class': 'industry-retail',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Retail and e-commerce',
                    'icon': 'shopping-bag',
                    'order': 5
                },
                'education': {
                    'label': 'Education',
                    'css_class': 'industry-education',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Educational institutions',
                    'icon': 'academic-cap',
                    'order': 6
                },
                'consulting': {
                    'label': 'Consulting',
                    'css_class': 'industry-consulting',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Professional services and consulting',
                    'icon': 'light-bulb',
                    'order': 7
                },
                'energy': {
                    'label': 'Energy',
                    'css_class': 'industry-energy',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Energy and utilities',
                    'icon': 'bolt',
                    'order': 8
                },
                'other': {
                    'label': 'Other',
                    'css_class': 'industry-other',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Other industries',
                    'icon': 'ellipsis-horizontal',
                    'order': 99
                }
            }
        }
    )
    website = db.Column(
        db.String(255),
        info={
            'display_label': 'Website',
            'sortable': True,
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
        from app.utils.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_choices(cls, 'industry')
    
    @classmethod
    def get_industry_css_class(cls, industry_value):
        """Get CSS class for an industry value"""
        from app.utils.model_introspection import ModelIntrospector
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
