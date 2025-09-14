from datetime import date
from flask import Blueprint, render_template, request
from app.models import User, Company, Opportunity
from app.utils.routes import add_content_route
from app.utils.route_helpers.helpers import build_dropdown_configs, calculate_entity_stats, build_entity_buttons
from collections import defaultdict

# Create blueprint and add DRY content route
teams_bp = Blueprint("teams", __name__)
add_content_route(teams_bp, User)


@teams_bp.route("/")
def index():
    # Get team member data for templates that need it
    team_members = User.query.all()

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

    return render_template("base/entity_index.html",
        entity_config={
            **User.get_entity_config(),
            'entity_buttons': build_entity_buttons(User)
        },
        dropdown_configs=build_dropdown_configs(User),
        entity_stats=calculate_entity_stats(User),
        team_members=team_members,
        team_data=team_data
    )


# Content route provided by DRY factory


