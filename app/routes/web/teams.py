from datetime import date
from flask import Blueprint, render_template, request
from app.models import User, Company, Opportunity
from app.utils.route_helpers import BaseRouteHandler, EntityFilterManager, EntityGrouper
from app.utils.model_introspection import ModelIntrospector
from collections import defaultdict

teams_bp = Blueprint("teams", __name__)
team_handler = BaseRouteHandler(User, "teams")
team_filter_manager = EntityFilterManager(User, "team_member")


def team_custom_filters(query, filters):
    """Team-specific filtering logic"""
    if filters['primary_filter']:
        query = query.filter(User.job_title.in_(filters['primary_filter']))
    
    return query


def team_custom_groupers(entities, group_by):
    """Team-specific grouping logic"""
    grouped = defaultdict(list)
    
    if group_by == "job_title":
        for member in entities:
            job_title = member.job_title or "No Job Title"
            grouped[job_title].append(member)
        
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
        for member in entities:
            first_letter = member.name[0].upper() if member.name else "Other"
            grouped[first_letter].append(member)
        
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
    
    return None  # Use default grouping


@teams_bp.route("/")
def index():
    # Get filter parameters for initial state and URL persistence
    group_by = request.args.get("group_by", "job_title")
    sort_by = request.args.get("sort_by", "name")
    sort_direction = request.args.get("sort_direction", "asc")
    primary_filter = (
        request.args.get("primary_filter", "").split(",")
        if request.args.get("primary_filter")
        else []
    )

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

    today = date.today()
    
    # Ultra-DRY dropdown and entity configuration generation
    from app.utils.form_configs import DropdownConfigGenerator, EntityConfigGenerator
    dropdown_configs = DropdownConfigGenerator.generate_entity_dropdown_configs('teams', group_by, sort_by, sort_direction, primary_filter)
    
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
        'current_values': primary_filter,
        'name': 'primary_filter'
    }

    # Generate entity configuration using DRY system
    entity_config = EntityConfigGenerator.generate_entity_page_config('teams', User)
    entity_stats = EntityConfigGenerator.generate_entity_stats('teams', team_members, User)
    
    # Override with team-specific stats
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
                'value': len(companies_objects),
                'label': 'Companies Covered',
                'color_class': 'text-purple-600'
            },
            {
                'value': len(opportunities_objects),
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


