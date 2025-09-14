from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from . import db
from .base import BaseModel


class Opportunity(BaseModel):
    """
    Opportunity model representing sales opportunities in the CRM system.
    
    This model tracks sales opportunities through various pipeline stages,
    including deal value, probability, timeline, and relationships with
    companies and stakeholders. Each opportunity represents a potential
    sale or business transaction.
    
    Attributes:
        id: Primary key identifier.
        name: Opportunity name/title (required).
        value: Deal value in whole dollars.
        probability: Win probability percentage (0-100).
        priority: Priority level (low, medium, high).
        expected_close_date: Expected deal closure date.
        stage: Current pipeline stage.
        created_at: Opportunity creation timestamp.
        company_id: Associated company foreign key.
        company: Related company entity.
    """
    __tablename__ = "opportunities"
    __display_name__ = "Opportunity"
    

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(255),
        nullable=False,
        info={
            'display_label': 'Opportunity Name',
            'required': True,
            'form_include': True
        }
    )
    value = db.Column(
        db.Integer,
        info={
            'display_label': 'Deal Value',
            'groupable': True,
            'sortable': True,
            'form_include': True,
            'required': True,
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
            'form_include': True,
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
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id"),
        nullable=False,
        info={
            'display_label': 'Company',
            'form_include': True,
            'required': True,
            'relationship_field': 'company',
            'relationship_display_field': 'name'
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

    @property
    def deal_age(self) -> int:
        """
        Calculate the age of the deal in days.
        
        Computes the number of days since the opportunity was created,
        providing insights into deal velocity and aging.
        
        Returns:
            Number of days since opportunity creation.
            
        Example:
            >>> opp = Opportunity(name="Test Deal")
            >>> # After 5 days
            >>> opp.deal_age
            5
        """
        return (datetime.utcnow() - self.created_at).days
    
    @property
    def calculated_priority(self) -> str:
        """
        Calculate priority based on deal value using model metadata.
        
        Automatically determines opportunity priority by comparing
        the deal value against predefined thresholds in model metadata.
        This provides dynamic priority calculation based on monetary value.
        
        Returns:
            Priority string: 'low', 'medium', or 'high'.
            Returns 'low' if value is None or doesn't meet any thresholds.
            
        Example:
            >>> opp = Opportunity(value=75000)
            >>> opp.calculated_priority
            'high'  # Assuming 50000+ is high priority threshold
        """
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
    def calculate_pipeline_value(cls, stage: Optional[str] = None) -> float:
        """
        Calculate total value for opportunities in given stage.

        Business method for calculating pipeline value, optionally filtered
        by specific stage. Used for dashboard metrics and reporting.

        Args:
            stage: Optional stage to filter by (e.g., 'proposal', 'qualified')

        Returns:
            Total value of opportunities in the specified stage

        Example:
            >>> total = Opportunity.calculate_pipeline_value()
            >>> proposal_value = Opportunity.calculate_pipeline_value('proposal')
        """
        query = cls.query
        if stage:
            query = query.filter(cls.stage == stage)
        opportunities = query.all()
        return sum(opp.value or 0 for opp in opportunities)

    @classmethod
    def get_pipeline_breakdown(cls) -> Dict[str, float]:
        """
        Get pipeline value breakdown by stage.

        Calculates total opportunity value for each pipeline stage,
        providing a complete view of the sales pipeline distribution.

        Returns:
            Dictionary mapping stage names to total values

        Example:
            >>> breakdown = Opportunity.get_pipeline_breakdown()
            >>> {'prospect': 150000, 'qualified': 250000, ...}
        """
        # Get stages using existing DRY method
        stages = cls.get_stage_choices()

        breakdown = {}
        for stage_value in stages:
            breakdown[stage_value] = cls.calculate_pipeline_value(stage_value)

        # Add total
        breakdown['total'] = cls.calculate_pipeline_value()

        return breakdown

    @classmethod
    def get_closing_soon(cls, days: int = 7, limit: int = 5) -> List:
        """
        Get opportunities closing within specified days.

        Identifies opportunities in active stages that are expected to
        close soon, useful for sales focus and priority management.

        Args:
            days: Number of days to look ahead (default: 7)
            limit: Maximum number of opportunities to return (default: 5)

        Returns:
            List of opportunities closing within the specified timeframe

        Example:
            >>> urgent = Opportunity.get_closing_soon(days=3)
            >>> this_month = Opportunity.get_closing_soon(days=30, limit=20)
        """
        cutoff = date.today() + timedelta(days=days)

        return cls.query.filter(
            cls.expected_close_date <= cutoff,
            cls.expected_close_date >= date.today(),
            cls.stage.in_(['proposal', 'negotiation'])
        ).limit(limit).all()

    @classmethod
    def get_stage_choices(cls) -> Dict[str, Dict[str, str]]:
        """
        Get stage choices from model metadata.

        Retrieves the available pipeline stage options defined in the model's
        field configuration for use in forms and validation.
        
        Returns:
            Dictionary mapping stage keys to their display information:
            - label: Human-readable stage name
            - description: Detailed stage description
            
        Example:
            >>> choices = Opportunity.get_stage_choices()
            >>> print(choices['qualified'])
            {'label': 'Qualified', 'description': 'Meets our criteria'}
        """
        # Get choices directly from column info
        return cls.stage.info.get('choices', {})
    

    def get_stakeholders(self) -> List[Dict[str, Any]]:
        """
        Get all stakeholders for this opportunity with their MEDDPICC roles.
        
        Retrieves stakeholders associated with this opportunity, including
        their contact information and MEDDPICC roles for sales methodology
        tracking. Results are sorted alphabetically by name.
        
        Returns:
            List of dictionaries containing stakeholder information:
            - id: Stakeholder ID
            - name: Stakeholder's full name
            - job_title: Stakeholder's job title
            - email: Stakeholder's email address
            - phone: Stakeholder's phone number
            - meddpicc_roles: List of MEDDPICC role names
            
        Example:
            >>> opp = Opportunity.query.first()
            >>> stakeholders = opp.get_stakeholders()
            >>> print(stakeholders[0])
            {'id': 1, 'name': 'John Doe', 'meddpicc_roles': ['Champion', 'Decision Maker']}
        """
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

    def get_full_account_team(self) -> List[Dict[str, Any]]:
        """
        Get full account team including inherited company team and opportunity-specific assignments.
        
        Combines account team members from both the parent company and
        opportunity-specific assignments. Handles deduplication when users
        are assigned at both levels, and provides source tracking to indicate
        the origin of each team member assignment.
        
        Returns:
            List of dictionaries containing team member information:
            - id: User ID
            - name: User's full name
            - email: User's email address
            - job_title: User's job title or None
            - source: Assignment source ('company', 'opportunity', or 'both')
            
        Example:
            >>> opp = Opportunity.query.first()
            >>> team = opp.get_full_account_team()
            >>> print(team[0])
            {'id': 1, 'name': 'Jane Smith', 'source': 'both'}
        """
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

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert opportunity to dictionary for JSON serialization.
        
        Creates a comprehensive dictionary representation including
        all database fields, computed properties, related entities,
        and UI helper fields like CSS classes.
        
        Returns:
            Dictionary containing:
            - All database column values
            - Computed properties (calculated_priority, deal_age)
            - Related entity summaries (stakeholders with MEDDPICC roles)
            - UI helper fields (company_name)
            
        Example:
            >>> opp = Opportunity(name="Big Deal", stage="qualified")
            >>> data = opp.to_dict()
            >>> print(data['name'])
            'Big Deal'
        """
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
        
        # Start with base serialization - convert model to dict
        result = {}
        # Serialize all columns
        for column in self.__table__.columns:
            column_name = column.name
            value = getattr(self, column_name, None)
            # Handle datetime/date serialization
            if isinstance(value, (datetime, date)):
                result[column_name] = value.isoformat() if value else None
            else:
                result[column_name] = value

        # Add custom properties and transforms
        for prop in include_properties:
            if hasattr(self, prop):
                result[prop] = getattr(self, prop)

        # Apply field transforms
        for field, transform in field_transforms.items():
            if field in result:
                result[field] = transform(result[field])
        
        # Add computed company name
        result["company_name"] = self.company.name if self.company else None
        
        return result

    def to_display_dict(self) -> Dict[str, Any]:
        """
        Convert opportunity to dictionary with pre-formatted display fields.

        Extends the basic dictionary representation with formatted
        fields optimized for display in user interfaces. This includes
        formatted currency values, percentages, and other UI-specific formatting.

        Returns:
            Dictionary with all standard fields plus display-formatted versions
            of fields that benefit from special formatting:
            - value_formatted: Currency formatted deal value
            - probability_formatted: Percentage formatted probability
            - deal_age_formatted: Human-readable deal age
            - stage_display: Human-readable stage (e.g., "Closed Won" instead of "closed-won")
            - priority_display: Human-readable priority

        Example:
            >>> opp = Opportunity(value=50000, probability=75, stage="closed-won")
            >>> display_data = opp.to_display_dict()
            >>> print(display_data['value_formatted'])
            '$50,000'
            >>> print(display_data['probability_formatted'])
            '75%'
            >>> print(display_data['stage_display'])
            'Closed Won'
        """
        # Get base dictionary
        result = self.to_dict()

        # Add opportunity-specific computed fields
        result['deal_age_formatted'] = f"{self.deal_age} days old"

        # Add display-friendly versions of choice fields
        result['stage_display'] = self.stage.replace('-', ' ').replace('_', ' ').title() if self.stage else ''
        result['priority_display'] = self.priority.replace('-', ' ').replace('_', ' ').title() if self.priority else ''

        return result

    def __repr__(self) -> str:
        """Return string representation of the opportunity."""
        return f"<Opportunity {self.name}>"
