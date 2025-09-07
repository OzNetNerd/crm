from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from crm.models import db, Meeting, Company, ExtractedInsight
from datetime import datetime

meetings_bp = Blueprint("meetings", __name__)


@meetings_bp.route("/")
def index():
    """List all meetings"""
    meetings = Meeting.query.order_by(Meeting.created_at.desc()).all()
    companies = Company.query.order_by(Company.name).all()
    
    return render_template(
        "meetings/index.html",
        meetings=meetings,
        companies=companies
    )


@meetings_bp.route("/new", methods=["GET", "POST"])
def new():
    """Create a new meeting"""
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form
        
        meeting = Meeting(
            title=data["title"],
            transcript=data["transcript"],
            company_id=data.get("company_id") if data.get("company_id") else None,
            analysis_status="pending"
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                "status": "success", 
                "meeting_id": meeting.id,
                "message": "Meeting created successfully. Analysis will begin shortly."
            })
        else:
            flash("Meeting created successfully. Analysis will begin shortly.", "success")
            return redirect(url_for("meetings.detail", meeting_id=meeting.id))
    
    companies = Company.query.order_by(Company.name).all()
    return render_template("meetings/new.html", companies=companies)


@meetings_bp.route("/<int:meeting_id>")
def detail(meeting_id):
    """Show meeting details with extracted insights"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Get extracted insights
    insights = ExtractedInsight.query.filter_by(meeting_id=meeting_id).all()
    
    # Organize insights by type
    organized_insights = {}
    for insight in insights:
        organized_insights[insight.insight_type] = {
            'data': insight.extracted_data,
            'confidence': insight.confidence_score,
            'status': insight.review_status
        }
    
    return render_template(
        "meetings/detail.html",
        meeting=meeting,
        insights=organized_insights
    )


@meetings_bp.route("/<int:meeting_id>/analyze", methods=["POST"])
def analyze(meeting_id):
    """Trigger meeting analysis"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Update status to trigger background processing
    meeting.analysis_status = "pending"
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "message": "Meeting analysis queued. Check back in a few minutes.",
        "meeting_id": meeting_id
    })


@meetings_bp.route("/<int:meeting_id>/status")
def status(meeting_id):
    """Get meeting analysis status"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    insight_count = ExtractedInsight.query.filter_by(meeting_id=meeting_id).count()
    
    return jsonify({
        "meeting_id": meeting_id,
        "title": meeting.title,
        "status": meeting.analysis_status,
        "analyzed_at": meeting.analyzed_at.isoformat() if meeting.analyzed_at else None,
        "insights_count": insight_count
    })