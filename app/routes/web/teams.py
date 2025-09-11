from datetime import date
from flask import Blueprint, render_template, request
from app.models import (
    User,
    Company,
    Opportunity,
)
from app.utils.model_introspection import ModelIntrospector
from app.utils.form_configs import EntityConfigGenerator
from collections import defaultdict

teams_bp = Blueprint("teams", __name__)


@teams_bp.route("/")
def index():
    # Get filter parameters for initial state and URL persistence
    group_by = request.args.get("group_by", "job_title")
    sort_by = request.args.get("sort_by", "name")
    sort_direction = request.args.get("sort_direction", "asc")
    show_all = request.args.get("show_all", "false").lower() == "true"
    job_title_filter = (
        request.args.get("primary_filter", "").split(",")
        if request.args.get("primary_filter")
        else []
    )

    # Get all account team members
    team_members = User.query.all()

    # Get all companies and opportunities for assignments
    companies_objects = Company.query.all()
    opportunities_objects = Opportunity.query.all()

    # Convert to JSON-serializable format
    companies_data = [
        {
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "website": company.website,
        }
        for company in companies_objects
    ]

    opportunities_data = [
        {
            "id": opp.id,
            "name": opp.name,
            "value": float(opp.value) if opp.value else 0,
            "company_id": opp.company_id,
            "company_name": opp.company.name if opp.company else "Unknown Company",
        }
        for opp in opportunities_objects
    ]

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

    today = date.today()
    
    # Ultra-DRY dropdown generation using pure model introspection
    from app.utils.form_configs import DropdownConfigGenerator
    dropdown_configs = DropdownConfigGenerator.generate_entity_dropdown_configs('teams', group_by, sort_by, sort_direction, [])
    
    # Get unique job titles for dynamic filter (since User model doesn't have predefined job title choices)
    job_title_options = []
    job_titles = User.query.with_entities(User.job_title).distinct().all()
    for job_title_tuple in job_titles:
        job_title = job_title_tuple[0]
        if job_title:
            job_title_options.append({'value': job_title, 'label': job_title})
    
    # Override primary filter with dynamic job titles
    dropdown_configs['primary_filter'] = {
        'button_text': 'All Job Titles',
        'options': job_title_options,
        'current_values': [job_title_filter] if job_title_filter else [],
        'name': 'job_title_filter'
    }

    # Generate entity configuration using DRY system
    entity_config = EntityConfigGenerator.generate_entity_page_config('teams', User)
    
    # Team member stats for overview (custom format for teams)
    entity_stats = {
        'title': 'Team Overview',
        'stats': [
            {
                'value': len(team_members),
                'label': 'Total Team Members',
                'color_class': 'text-blue-600'
            },
            {
                'value': sum(len(member.get_company_assignments()) + len(member.get_opportunity_assignments()) for member in team_members),
                'label': 'Active Assignments',
                'color_class': 'text-green-600'
            },
            {
                'value': len(companies_data),
                'label': 'Companies Covered',
                'color_class': 'text-purple-600'
            },
            {
                'value': len(opportunities_data),
                'label': 'Opportunities Managed',
                'color_class': 'text-yellow-600'
            }
        ]
    }

    return render_template(
        "base/entity_index.html",
        **entity_config,
        dropdown_configs=dropdown_configs,
        entity_stats=entity_stats,
        team_members=team_members,
        team_data=team_data,
    )


def get_filtered_team_context():
    """Server-side filtering and sorting for team members HTMX endpoints"""
    # Get filter parameters
    group_by = request.args.get("group_by", "job_title")
    sort_by = request.args.get("sort_by", "name")
    sort_direction = request.args.get("sort_direction", "asc")
    
    # Parse filter arrays
    job_title_filter = []
    if request.args.get("primary_filter"):
        job_title_filter = [p.strip() for p in request.args.get("primary_filter").split(",") if p.strip()]
    
    # Start with base query
    query = User.query
    
    # Apply filters
    if job_title_filter:
        query = query.filter(User.job_title.in_(job_title_filter))
    
    # Apply sorting
    if sort_by == "name":
        if sort_direction == "desc":
            query = query.order_by(User.name.desc())
        else:
            query = query.order_by(User.name.asc())
    elif sort_by == "job_title":
        if sort_direction == "desc":
            query = query.order_by(User.job_title.desc().nulls_last())
        else:
            query = query.order_by(User.job_title.asc().nulls_last())
    elif sort_by == "email":
        if sort_direction == "desc":
            query = query.order_by(User.email.desc().nulls_last())
        else:
            query = query.order_by(User.email.asc().nulls_last())
    elif sort_by == "created_at":
        if sort_direction == "desc":
            query = query.order_by(User.created_at.desc().nulls_last())
        else:
            query = query.order_by(User.created_at.asc().nulls_last())
    else:
        # Default sort by name
        query = query.order_by(User.name.asc())
    
    filtered_team_members = query.all()
    
    # Group team members by the specified grouping
    grouped_team_members = group_team_members_by_field(filtered_team_members, group_by)
    
    return {
        "grouped_team_members": grouped_team_members,
        "group_by": group_by,
        "total_count": len(filtered_team_members),
        "sort_by": sort_by,
        "sort_direction": sort_direction,
        "job_title_filter": job_title_filter,
        "today": date.today(),
    }


def group_team_members_by_field(team_members, group_by):
    """Group team members by specified field"""
    grouped = defaultdict(list)
    
    if group_by == "job_title":
        for member in team_members:
            job_title = member.job_title or "No Job Title"
            grouped[job_title].append(member)
        
        # Return sorted by job title
        result = []
        for job_title in sorted(grouped.keys()):
            if grouped[job_title]:
                result.append({
                    "key": job_title,
                    "label": job_title,
                    "entities": grouped[job_title],
                    "count": len(grouped[job_title])
                })
        return result
        
    elif group_by == "name":
        # Group by first letter of name
        for member in team_members:
            first_letter = member.name[0].upper() if member.name else "Other"
            grouped[first_letter].append(member)
        
        # Return sorted by first letter
        result = []
        for letter in sorted(grouped.keys()):
            if grouped[letter]:
                result.append({
                    "key": letter,
                    "label": f"Names starting with {letter}",
                    "entities": grouped[letter],
                    "count": len(grouped[letter])
                })
        return result
    
    else:
        # Default: no grouping, return all in one group
        return [{
            "key": "all",
            "label": "All Team Members",
            "entities": team_members,
            "count": len(team_members)
        }]


@teams_bp.route("/content")
def content():
    """HTMX endpoint for filtered team member content"""
    context = get_filtered_team_context()
    
    # Universal template configuration using model introspection
    context.update({
        'grouped_entities': context["grouped_team_members"],
        'entity_type': 'team_member',
        'entity_name_singular': 'team member',
        'entity_name_plural': 'team members',
        'card_config': ModelIntrospector.get_card_config(User),
        'model_class': User
    })
    
    return render_template("shared/entity_content.html", **context)


