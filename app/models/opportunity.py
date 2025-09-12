from datetime import datetime
from . import db


class Opportunity(db.Model):
    __tablename__ = "opportunities"
    
    __entity_config__ = {
        'display_name': 'Opportunities',
        'display_name_singular': 'Opportunity',
        'description': 'Manage your sales opportunities',
        'endpoint_name': 'opportunities', 
        'modal_path': '/modals/Opportunity',
        'show_dashboard_button': True
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(
        db.Integer,
        info={
            'display_label': 'Deal Value',
            'groupable': True,
            'sortable': True,
            'priority_ranges': [
                (50000, 'high', 'High Value ($50K+)'),
                (10000, 'medium', 'Medium Value ($10K-$50K)'),
                (0, 'low', 'Low Value (<$10K)')
            ]
        }
    )  # Store monetary value in whole dollars
    probability = db.Column(
        db.Integer, 
        default=0,
        info={
            'display_label': 'Win Probability',
            'groupable': True,
            'sortable': True,
            'unit': '%',
            'min_value': 0,
            'max_value': 100
        }
    )  # 0-100 percentage
    
    priority = db.Column(
        db.String(50),
        info={
            'display_label': 'Priority',
            'choices': {
                'low': {
                    'label': 'Low',
                    'description': 'Low priority opportunity'
                },
                'medium': {
                    'label': 'Medium', 
                    'description': 'Medium priority opportunity'
                },
                'high': {
                    'label': 'High',
                    'description': 'High priority opportunity'
                }
            }
        }
    )
    
    expected_close_date = db.Column(
        db.Date,
        info={
            'display_label': 'Expected Close Date',
            'groupable': True,
            'sortable': True,
            'date_groupings': {
                'overdue': 'Overdue',
                'this_week': 'This Week',
                'this_month': 'This Month', 
                'later': 'Later',
                'no_date': 'No Close Date'
            }
        }
    )
    stage = db.Column(
        db.String(50), 
        default="prospect",
        info={
            'display_label': 'Pipeline Stage',
            'choices': {
                'prospect': {
                    'label': 'Prospect',
                    'description': 'Initial contact made'
                },
                'qualified': {
                    'label': 'Qualified',
                    'description': 'Meets our criteria'
                },
                'proposal': {
                    'label': 'Proposal',
                    'description': 'Formal proposal submitted'
                },
                'negotiation': {
                    'label': 'Negotiation',
                    'description': 'Terms discussion in progress'
                },
                'closed-won': {
                    'label': 'Closed Won',
                    'description': 'Deal successful'
                },
                'closed-lost': {
                    'label': 'Closed Lost',
                    'description': 'Deal unsuccessful'
                }
            }
        }
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    @property
    def deal_age(self):
        return (datetime.utcnow() - self.created_at).days
    
    @property
    def calculated_priority(self):
        """Calculate priority based on deal value using model metadata"""
        if not self.value:
            return 'low'
            
        # Get priority ranges from model metadata
        value_info = self.__class__.value.property.columns[0].info
        priority_ranges = value_info.get('priority_ranges', [])
        
        for min_value, priority, label in priority_ranges:
            if self.value >= min_value:
                return priority
                
        return 'low'
    
    @classmethod
    def get_stage_choices(cls):
        """Get stage choices from model metadata"""
        from app.utils.core.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_choices(cls, 'stage')
    
    @classmethod
    def get_stage_css_class(cls, stage_value):
        """Get CSS class for a stage value"""
        from app.utils.core.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_css_class(cls, 'stage', stage_value)

    def get_stakeholders(self):
        """Get all stakeholders for this opportunity with their MEDDPICC roles"""
        # Use the ORM relationship and sort by name
        sorted_stakeholders = sorted(self.stakeholders, key=lambda s: s.name)

        return [
            {
                "id": stakeholder.id,
                "name": stakeholder.name,
                "job_title": stakeholder.job_title,
                "email": stakeholder.email,
                "phone": stakeholder.phone,
                "meddpicc_roles": stakeholder.get_meddpicc_role_names(),  # Use existing method
            }
            for stakeholder in sorted_stakeholders
        ]

    def get_full_account_team(self):
        """Get full account team including inherited company team and opportunity-specific assignments"""
        # Get company account team members using ORM
        company_team = []
        if self.company:
            for assignment in self.company.account_team_assignments:
                company_team.append(
                    {
                        "id": assignment.user.id,
                        "name": assignment.user.name,
                        "email": assignment.user.email,
                        "job_title": assignment.user.job_title,
                        "source": "company",
                    }
                )

        # Get opportunity-specific account team members using ORM
        opp_team = []
        for assignment in self.account_team_assignments:
            opp_team.append(
                {
                    "id": assignment.user.id,
                    "name": assignment.user.name,
                    "email": assignment.user.email,
                    "job_title": assignment.user.job_title,
                    "source": "opportunity",
                }
            )

        # Combine teams and deduplicate (user might be on both company and opportunity teams)
        all_team = {}
        for member in company_team + opp_team:
            user_id = member["id"]
            if user_id not in all_team:
                all_team[user_id] = member
            elif (
                all_team[user_id]["source"] == "company"
                and member["source"] == "opportunity"
            ):
                # Upgrade source to opportunity if they're on both
                all_team[user_id]["source"] = "both"

        # Sort by job_title, name and return
        return sorted(
            all_team.values(), key=lambda x: (x["job_title"] or "", x["name"])
        )

    def to_dict(self):
        """Convert opportunity to dictionary for JSON serialization"""
        from app.utils.model_helpers import auto_serialize
        
        # Define properties to include beyond database columns
        include_properties = ["calculated_priority", "deal_age"]
        
        # Define custom transforms for specific fields and relationships
        field_transforms = {
            "value": lambda val: float(val) if val else None,
            "stakeholders": lambda _: [
                {
                    "id": stakeholder["id"],
                    "name": stakeholder["name"],
                    "job_title": stakeholder["job_title"],
                    "email": stakeholder["email"],
                    "meddpicc_roles": stakeholder["meddpicc_roles"],
                }
                for stakeholder in self.get_stakeholders()
            ]
        }
        
        result = auto_serialize(self, include_properties, field_transforms)
        
        # Add computed company name and CSS class
        result["company_name"] = self.company.name if self.company else None
        result["stage_css_class"] = self.get_stage_css_class(self.stage)
        
        return result

    def to_display_dict(self):
        """Convert opportunity to dictionary with pre-formatted display fields"""
        from app.utils.ui.formatters import create_display_dict, DisplayFormatter
        
        # Get base dictionary
        result = self.to_dict()
        
        # Add formatted display fields at source
        display_fields = create_display_dict(self)
        result.update(display_fields)
        
        # Add opportunity-specific formatted fields
        result['value_formatted'] = DisplayFormatter.format_currency(self.value)
        result['probability_formatted'] = DisplayFormatter.format_percentage(self.probability / 100.0 if self.probability else 0)
        result['deal_age_formatted'] = f"{self.deal_age} days old"
        
        return result

    def __repr__(self):
        return f"<Opportunity {self.name}>"
