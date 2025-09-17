"""Simple opportunity utilities - business logic extracted from model."""
from datetime import datetime
from typing import Dict, List, Optional, Any


def calculate_deal_age(created_at: datetime) -> int:
    """Calculate deal age in days."""
    return (datetime.utcnow() - created_at).days


def calculate_priority_by_value(value: Optional[int]) -> str:
    """Calculate priority based on deal value."""
    if not value:
        return "low"

    # Simple priority ranges - no need to fetch from metadata
    if value >= 50000:
        return "high"
    elif value >= 10000:
        return "medium"
    return "low"


def get_pipeline_value(opportunity_model_class, stage: Optional[str] = None) -> float:
    """Calculate total pipeline value for stage."""
    query = opportunity_model_class.query
    if stage:
        query = query.filter(opportunity_model_class.stage == stage)
    return sum(opp.value or 0 for opp in query.all())


def get_pipeline_breakdown(opportunity_model_class) -> Dict[str, float]:
    """Get pipeline value breakdown by stage."""
    stages = get_stage_choices()
    breakdown = {stage: get_pipeline_value(opportunity_model_class, stage) for stage in stages}
    breakdown["total"] = get_pipeline_value(opportunity_model_class)
    return breakdown


def get_closing_soon(opportunity_model_class, days: int = 7, limit: int = 5) -> List:
    """Get opportunities closing soon."""
    from datetime import date, timedelta
    cutoff_date = date.today() + timedelta(days=days)
    return (opportunity_model_class.query
            .filter(opportunity_model_class.expected_close_date <= cutoff_date)
            .filter(opportunity_model_class.expected_close_date >= date.today())
            .order_by(opportunity_model_class.expected_close_date)
            .limit(limit)
            .all())


def get_stage_choices() -> Dict[str, Dict[str, str]]:
    """Get available opportunity stages."""
    return {
        "prospect": {"label": "Prospect", "description": "Initial contact"},
        "qualified": {"label": "Qualified", "description": "Qualified lead"},
        "proposal": {"label": "Proposal", "description": "Proposal sent"},
        "negotiation": {"label": "Negotiation", "description": "In negotiation"},
        "closed-won": {"label": "Closed Won", "description": "Deal won"},
        "closed-lost": {"label": "Closed Lost", "description": "Deal lost"},
    }


def get_stakeholders(opportunity_id: int) -> List[Dict[str, Any]]:
    """Get stakeholders for opportunity."""
    if not opportunity_id:
        return []

    # Import here to avoid circular imports
    from .. import db
    from ..models.stakeholder import stakeholder_opportunities

    # Query the junction table
    linked = (db.session.query(stakeholder_opportunities.c.stakeholder_id)
              .filter(stakeholder_opportunities.c.opportunity_id == opportunity_id)
              .all())

    stakeholders = []
    for (stakeholder_id,) in linked:
        from ..models.stakeholder import Stakeholder
        stakeholder = Stakeholder.query.get(stakeholder_id)
        if stakeholder:
            stakeholders.append({
                "id": stakeholder.id,
                "name": stakeholder.name,
                "job_title": stakeholder.job_title,
                "email": stakeholder.email,
                "meddpicc_roles": stakeholder.meddpicc_roles,
            })

    return stakeholders


def get_full_account_team(opportunity_id: int) -> List[Dict[str, Any]]:
    """Get full account team for opportunity."""
    # Get direct stakeholders first
    stakeholders = get_stakeholders(opportunity_id)

    # Add company stakeholders if they exist
    if not opportunity_id:
        return stakeholders

    from ..models.opportunity import Opportunity
    opportunity = Opportunity.query.get(opportunity_id)
    if not opportunity or not opportunity.company:
        return stakeholders

    # Add company stakeholders
    company_stakeholders = opportunity.company.stakeholders
    for stakeholder in company_stakeholders:
        # Avoid duplicates
        if not any(s["id"] == stakeholder.id for s in stakeholders):
            stakeholders.append({
                "id": stakeholder.id,
                "name": stakeholder.name,
                "job_title": stakeholder.job_title,
                "email": stakeholder.email,
                "meddpicc_roles": stakeholder.meddpicc_roles,
                "source": "company",
            })

    return stakeholders