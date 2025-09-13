from datetime import date
from flask import Blueprint, render_template, request
from app.models import User, Company, Opportunity
from app.utils.core.base_handlers import BaseRouteHandler, EntityFilterManager, EntityGrouper
from app.utils.core.model_introspection import ModelIntrospector
from app.utils.core.entity_handlers import TeamHandler, UniversalEntityManager
from collections import defaultdict

teams_bp = Blueprint("teams", __name__)
team_handler = BaseRouteHandler(User, "teams")

# Create metadata-driven universal entity manager
team_entity_manager = UniversalEntityManager(User, TeamHandler())
team_filter_manager = EntityFilterManager(User, "team_member")


# Use universal entity manager methods instead of duplicated functions
def team_custom_filters(query, filters):
    """Team-specific filtering using universal manager"""
    return team_entity_manager.apply_custom_filters(query, filters)


def team_custom_groupers(entities, group_by):
    """Team-specific grouping using universal manager"""
    return team_entity_manager.apply_custom_grouping(entities, group_by)


@teams_bp.route("/")
def index():
    from app.utils.ui.index_helpers import UniversalIndexHelper
    
    # Get all account team members
    team_members = User.query.all()

    # Get all companies and opportunities for assignments
    companies_objects = Company.query.all()
    opportunities_objects = Opportunity.query.all()

    # Convert to JSON-serializable format for JavaScript
    team_data = []
    for member in team_members:
        # Get company assignments
        company_assignments = []
        for assignment in member.get_company_assignments():
            company_assignments.append(
                {
                    "company_id": assignment["company_id"],
                    "company_name": (
                        assignment["company"].name
                        if assignment["company"]
                        else "Unknown"
                    ),
                }
            )

        # Get opportunity assignments
        opportunity_assignments = []
        for assignment in member.get_opportunity_assignments():
            opportunity_assignments.append(
                {
                    "opportunity_id": assignment["opportunity_id"],
                    "opportunity_name": (
                        assignment["opportunity"].name
                        if assignment["opportunity"]
                        else "Unknown"
                    ),
                }
            )

        team_data.append(
            {
                "id": member.id,
                "name": member.name,
                "email": member.email,
                "job_title": member.job_title,
                "company_assignments": company_assignments,
                "opportunity_assignments": opportunity_assignments,
                "created_at": (
                    member.created_at.isoformat()
                    if hasattr(member, "created_at") and member.created_at
                    else None
                ),
            }
        )
    
    # Generate team stats directly
    entity_stats = {
        'title': 'Team Overview',
        'stats': [
            {
                'value': len(team_members),
                'label': 'Total Team Members'
            },
            {
                'value': sum(len(member.get_company_assignments()) + len(member.get_opportunity_assignments()) for member in team_members),
                'label': 'Active Assignments'
            },
            {
                'value': len(companies_objects),
                'label': 'Companies Covered'
            },
            {
                'value': len(opportunities_objects),
                'label': 'Opportunities Managed'
            }
        ]
    }
    
    # Get standardized context using universal helper
    context = UniversalIndexHelper.get_standardized_index_context(
        entity_name='teams',
        default_group_by='job_title',
        default_sort_by='name',
        additional_context={
            'entity_stats': entity_stats,
            'team_members': team_members,
            'team_data': team_data,
        }
    )

    return render_template("base/entity_index.html", **context)


def get_filtered_team_context():
    """Server-side filtering and sorting for team members HTMX endpoints - DRY version"""
    return team_filter_manager.get_filtered_context(
        custom_filters=team_custom_filters,
        custom_grouper=team_custom_groupers
    )




@teams_bp.route("/content")
def content():
    """HTMX endpoint for filtered team member content - DRY version"""
    context = team_filter_manager.get_content_context(
        custom_filters=team_custom_filters,
        custom_grouper=team_custom_groupers
    )
    
    return render_template("shared/entity_content.html", **context)


