from datetime import date
from flask import Blueprint, render_template, request
from app.models import User, Company, Opportunity, CompanyAccountTeam, OpportunityAccountTeam
from app.utils.route_helpers import BaseRouteHandler

teams_bp = Blueprint("teams", __name__)
team_handler = BaseRouteHandler(User, "teams")


@teams_bp.route("/")
def index():
    # Get filter parameters for initial state and URL persistence
    group_by = request.args.get('group_by', 'job_title')
    sort_by = request.args.get('sort_by', 'name')
    sort_direction = request.args.get('sort_direction', 'asc')
    show_completed = request.args.get('show_completed', 'false').lower() == 'true'
    primary_filter = request.args.get('primary_filter', '').split(',') if request.args.get('primary_filter') else []
    secondary_filter = request.args.get('secondary_filter', '').split(',') if request.args.get('secondary_filter') else []
    entity_filter = request.args.get('entity_filter', '').split(',') if request.args.get('entity_filter') else []
    
    # Get all account team members
    team_members = User.query.all()
    
    # Get all companies and opportunities for assignments
    companies_objects = Company.query.all()
    opportunities_objects = Opportunity.query.all()
    
    # Convert to JSON-serializable format
    companies_data = [{
        'id': company.id,
        'name': company.name,
        'industry': company.industry,
        'website': company.website
    } for company in companies_objects]
    
    opportunities_data = [{
        'id': opp.id,
        'name': opp.name,
        'value': float(opp.value) if opp.value else 0,
        'company_id': opp.company_id,
        'company_name': opp.company.name if opp.company else 'Unknown Company'
    } for opp in opportunities_objects]
    
    # Convert to JSON-serializable format for JavaScript
    team_data = []
    for member in team_members:
        # Get company assignments
        company_assignments = []
        for assignment in member.get_company_assignments():
            company_assignments.append({
                'company_id': assignment['company_id'],
                'company_name': assignment['company'].name if assignment['company'] else 'Unknown'
            })
        
        # Get opportunity assignments  
        opportunity_assignments = []
        for assignment in member.get_opportunity_assignments():
            opportunity_assignments.append({
                'opportunity_id': assignment['opportunity_id'],
                'opportunity_name': assignment['opportunity'].name if assignment['opportunity'] else 'Unknown'
            })
        
        team_data.append({
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'job_title': member.job_title,
            'company_assignments': company_assignments,
            'opportunity_assignments': opportunity_assignments,
            'created_at': member.created_at.isoformat() if hasattr(member, 'created_at') and member.created_at else None
        })
    
    today = date.today()
    
    return render_template(
        "teams/index.html", 
        team_members=team_members,
        companies=companies_data,
        opportunities=opportunities_data,
        team_data=team_data,
        today=today,
        # Filter states for URL persistence
        group_by=group_by,
        sort_by=sort_by,
        sort_direction=sort_direction,
        show_completed=show_completed,
        primary_filter=','.join(primary_filter),
        secondary_filter=','.join(secondary_filter),
        entity_filter=','.join(entity_filter)
    )


@teams_bp.route("/<int:member_id>")
def detail(member_id):
    member = User.query.get_or_404(member_id)
    return render_template("teams/detail.html", member=member)


@teams_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        return team_handler.handle_create(
            name="name",
            email="email",
            job_title="job_title"
        )

    return render_template("teams/new.html")