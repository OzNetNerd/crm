"""
Dashboard Service

Service layer for dashboard-specific business logic and aggregations.
Centralizes dashboard data fetching and processing to keep routes clean.
"""

from typing import Dict, Any, List
from datetime import date
from app.models import Task, Company, Stakeholder, Opportunity, Note, User
from app.utils.ui.formatters import DisplayFormatter


class DashboardService:
    """Service for dashboard-specific aggregations and queries."""

    @staticmethod
    def get_pipeline_stats() -> Dict[str, Any]:
        """
        Get formatted pipeline statistics for dashboard.

        Returns pipeline breakdown by stage with formatted currency values
        and metadata for display.

        Returns:
            Dictionary with title and formatted stats array
        """
        breakdown = Opportunity.get_pipeline_breakdown()

        # Get first 4 stages for dashboard display
        stages = Opportunity.get_field_choices('stage')[:4]

        stats = []
        for stage_value, stage_label in stages:
            stats.append({
                'value': DisplayFormatter.format_currency(breakdown.get(stage_value, 0)),
                'label': stage_label.title(),
                'status': stage_value
            })

        return {
            'title': 'Sales Pipeline',
            'stats': stats
        }

    @staticmethod
    def get_recent_activity() -> Dict[str, List]:
        """
        Get recent activity items for dashboard.

        Fetches recent tasks, notes, and opportunities with display formatting.

        Returns:
            Dictionary with recent_tasks, recent_notes, recent_opportunities
        """
        # Get recent items using model methods
        recent_tasks = Task.get_recent(exclude_status='complete')
        # Note doesn't inherit from EntityModel, so use direct query
        recent_notes = Note.query.order_by(Note.created_at.desc()).limit(3).all()
        recent_opportunities = Opportunity.get_recent(limit=3)

        return {
            'recent_tasks': [task.to_display_dict() for task in recent_tasks],
            'recent_notes': [note.to_display_dict() for note in recent_notes],
            'recent_opportunities': [opp.to_display_dict() for opp in recent_opportunities]
        }

    @staticmethod
    def get_critical_alerts() -> Dict[str, List]:
        """
        Get critical alerts for dashboard.

        Identifies overdue tasks and opportunities closing soon.

        Returns:
            Dictionary with overdue_tasks and closing_soon opportunities
        """
        overdue_tasks = Task.get_overdue()
        closing_soon = Opportunity.get_closing_soon()

        return {
            'overdue_tasks': [task.to_display_dict() for task in overdue_tasks],
            'closing_soon': [opp.to_display_dict() for opp in closing_soon]
        }

    @staticmethod
    def get_entity_buttons() -> List[str]:
        """
        Get dashboard entity buttons dynamically.

        Returns list of entity endpoints that should show dashboard buttons
        based on their configuration.

        Returns:
            List of endpoint names for dashboard buttons
        """
        models = [Company, Task, Opportunity, Stakeholder, User]
        buttons = []

        for model in models:
            config = model.get_entity_config()
            if config.get('show_dashboard_button', True):
                # Use just tablename for dashboard buttons, not full endpoint
                buttons.append(model.__tablename__)

        return buttons

    @staticmethod
    def get_dashboard_data() -> Dict[str, Any]:
        """
        Get all dashboard data in one call.

        Aggregates all dashboard statistics, recent activity, and alerts
        for rendering the dashboard page.

        Returns:
            Complete dashboard context dictionary
        """
        # Combine all dashboard data
        data = {
            'dashboard_stats': DashboardService.get_pipeline_stats(),
            'entity_types': DashboardService.get_entity_buttons(),
            'today': date.today()
        }

        # Add recent activity
        data.update(DashboardService.get_recent_activity())

        # Add critical alerts
        data.update(DashboardService.get_critical_alerts())

        # Add pipeline stats for backward compatibility
        breakdown = Opportunity.get_pipeline_breakdown()
        data['pipeline_stats'] = {
            'prospect': breakdown.get('prospect', 0),
            'qualified': breakdown.get('qualified', 0),
            'proposal': breakdown.get('proposal', 0),
            'negotiation': breakdown.get('negotiation', 0),
            'total_value': breakdown.get('total', 0),
            'total_count': Opportunity.query.count()
        }

        return data