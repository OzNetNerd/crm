from datetime import date
from flask import Blueprint, render_template, request
from app.models import User, Company, Opportunity
from app.utils.routes import add_content_route
from collections import defaultdict

# Create blueprint and add DRY content route
teams_bp = Blueprint("teams", __name__)
add_content_route(teams_bp, User)


@teams_bp.route("/")
def index():
    
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
    
    # Simple context building - no over-engineered helpers
    context = {
        'entity_config': {
            'entity_name': 'Team Members',
            'entity_name_singular': 'Team Member',
            'entity_description': 'Manage your team members',
            'entity_type': 'team',
            'entity_endpoint': 'teams',
            'entity_buttons': ['teams']
        },
        'entity_stats': entity_stats,
        'team_members': team_members,
        'team_data': team_data,
        'dropdown_configs': {
            'group_by': {
                'options': [
                    {'value': 'job_title', 'label': 'Job Title'},
                    {'value': 'name', 'label': 'Name'}
                ],
                'current_value': request.args.get('group_by', 'job_title'),
                'placeholder': 'Group by...'
            },
            'sort_by': {
                'options': [
                    {'value': 'name', 'label': 'Name'},
                    {'value': 'job_title', 'label': 'Job Title'},
                    {'value': 'created_at', 'label': 'Created Date'}
                ],
                'current_value': request.args.get('sort_by', 'name'),
                'placeholder': 'Sort by...'
            }
        }
    }

    return render_template("base/entity_index.html", **context)


def get_filtered_team_context():
    """Server-side filtering and sorting for team members HTMX endpoints - DRY version"""
    return team_filter_manager.get_filtered_context(
        custom_filters=team_custom_filters,
        custom_grouper=team_custom_groupers
    )




# Content route now provided by DRY factory


