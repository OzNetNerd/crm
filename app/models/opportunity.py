from datetime import datetime
from . import db


class Opportunity(db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(
        db.Integer,
        info={
            'display_label': 'Deal Value',
            'groupable': True,
            'sortable': True,
            'priority_ranges': [
                (50000, 'high', 'High Value ($50K+)', 'priority-high'),
                (10000, 'medium', 'Medium Value ($10K-$50K)', 'priority-medium'),
                (0, 'low', 'Low Value (<$10K)', 'priority-low')
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
    expected_close_date = db.Column(
        db.Date,
        info={
            'display_label': 'Expected Close Date',
            'groupable': True,
            'sortable': True,
            'date_groupings': {
                'overdue': {'label': 'Overdue', 'css_class': 'date-overdue'},
                'this_week': {'label': 'This Week', 'css_class': 'date-soon'},
                'this_month': {'label': 'This Month', 'css_class': 'date-current'},
                'later': {'label': 'Later', 'css_class': 'date-future'},
                'no_date': {'label': 'No Close Date', 'css_class': 'date-missing'}
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
                    'css_class': 'status-prospect',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Initial contact made',
                    'icon': 'user-plus',
                    'order': 1
                },
                'qualified': {
                    'label': 'Qualified',
                    'css_class': 'status-qualified',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Meets our criteria',
                    'icon': 'check-circle',
                    'order': 2
                },
                'proposal': {
                    'label': 'Proposal',
                    'css_class': 'status-proposal',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Formal proposal submitted',
                    'icon': 'document-text',
                    'order': 3
                },
                'negotiation': {
                    'label': 'Negotiation',
                    'css_class': 'status-negotiating',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Terms discussion in progress',
                    'icon': 'handshake',
                    'order': 4
                },
                'closed-won': {
                    'label': 'Closed Won',
                    'css_class': 'status-won',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Deal successful',
                    'icon': 'trophy',
                    'order': 5
                },
                'closed-lost': {
                    'label': 'Closed Lost',
                    'css_class': 'status-lost',
                    'groupable': True,
                    'sortable': True,
                    'description': 'Deal unsuccessful',
                    'icon': 'x-circle',
                    'order': 6
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
        
        for min_value, priority, label, css_class in priority_ranges:
            if self.value >= min_value:
                return priority
                
        return 'low'
    
    @classmethod
    def get_stage_choices(cls):
        """Get stage choices from model metadata"""
        from app.utils.model_introspection import ModelIntrospector
        return ModelIntrospector.get_field_choices(cls, 'stage')
    
    @classmethod
    def get_stage_css_class(cls, stage_value):
        """Get CSS class for a stage value"""
        from app.utils.model_introspection import ModelIntrospector
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

    def __repr__(self):
        return f"<Opportunity {self.name}>"
