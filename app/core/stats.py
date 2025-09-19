"""Entity statistics generation - DRY, configurable, extensible."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import db


@dataclass
class Stat:
    """Single statistic configuration.

    Attributes:
        label: Display label for the stat.
        value: The computed value or callable to compute it.
        formatter: Optional formatter for the value.
    """

    label: str
    value: Any
    formatter: Optional[Callable[[Any], str]] = None

    def format(self) -> str:
        """Format the stat value for display.

        Returns:
            Formatted string representation of the value.
        """
        if self.formatter:
            return self.formatter(self.value)
        return str(self.value)


def format_currency(value: float) -> str:
    """Format currency values with appropriate units.

    Args:
        value: The numeric value to format.

    Returns:
        Formatted currency string (e.g., "$1.5M", "$250K", "$100").
    """
    if value > 1000000:
        return f"${value/1000000:.1f}M"
    elif value > 1000:
        return f"${value/1000:.0f}K"
    return f"${value:.0f}"


def format_percentage(value: float) -> str:
    """Format percentage values.

    Args:
        value: The numeric value to format as percentage.

    Returns:
        Formatted percentage string (e.g., "75%").
    """
    return f"{int(value)}%"


class StatsGenerator:
    """Generate statistics for entities with zero duplication.

    Attributes:
        model: SQLAlchemy model class.
        table_name: Database table name.
    """

    def __init__(self, model: type, table_name: str) -> None:
        """Initialize stats generator.

        Args:
            model: SQLAlchemy model class.
            table_name: Database table name.
        """
        self.model = model
        self.table_name = table_name

    def generate(self) -> List[Dict[str, Any]]:
        """Generate statistics based on entity type.

        Returns:
            List of stat dictionaries with value and label.
        """
        stats = [self._total_stat()]

        # Route to specific stat generators
        generators = {
            "companies": self._company_stats,
            "stakeholders": self._stakeholder_stats,
            "opportunities": self._opportunity_stats,
            "tasks": self._task_stats,
            "users": self._user_stats,
        }

        if generator := generators.get(self.table_name):
            stats.extend(generator())

        return [{"value": stat.format(), "label": stat.label} for stat in stats]

    def _total_stat(self) -> Stat:
        """Generate total count stat.

        Returns:
            Stat with total count.
        """
        total = self.model.query.count()
        label = f"Total {self.model.get_display_name_plural()}"
        return Stat(label=label, value=total)

    def _company_stats(self) -> List[Stat]:
        """Generate company-specific statistics.

        Returns:
            List of company statistics.
        """
        from app.models import Opportunity

        stats = []

        # Active companies
        active = (
            db.session.query(func.count(func.distinct(self.model.id)))
            .join(Opportunity)
            .scalar()
            or 0
        )
        stats.append(Stat(label="Active Companies", value=active))

        # Total opportunities
        total_opps = Opportunity.query.count()
        stats.append(Stat(label="Total Opportunities", value=total_opps))

        # Top industry
        top_industry = (
            db.session.query(self.model.industry, func.count(self.model.id))
            .filter(self.model.industry.isnot(None))
            .group_by(self.model.industry)
            .order_by(func.count(self.model.id).desc())
            .first()
        )

        if top_industry:
            stats.append(
                Stat(label=f"In {top_industry[0].title()}", value=top_industry[1])
            )

        return stats

    def _stakeholder_stats(self) -> List[Stat]:
        """Generate stakeholder-specific statistics.

        Returns:
            List of stakeholder statistics.
        """
        stats = []

        # Decision makers
        decision_titles = [
            "%CEO%",
            "%CTO%",
            "%CFO%",
            "%President%",
            "%VP%",
            "%Director%",
            "%Vice President%",
        ]
        conditions = [self.model.job_title.ilike(title) for title in decision_titles]
        decision_makers = self.model.query.filter(db.or_(*conditions)).count()
        stats.append(Stat(label="Decision Makers", value=decision_makers))

        # With email
        with_email = self.model.query.filter(self.model.email.isnot(None)).count()
        stats.append(Stat(label="With Email", value=with_email))

        # Companies represented
        companies = (
            db.session.query(func.count(func.distinct(self.model.company_id))).scalar()
            or 0
        )
        stats.append(Stat(label="Companies", value=companies))

        return stats

    def _opportunity_stats(self) -> List[Stat]:
        """Generate opportunity-specific statistics.

        Returns:
            List of opportunity statistics.
        """
        stats = []

        # Pipeline value
        total_value = db.session.query(func.sum(self.model.value)).scalar() or 0
        stats.append(
            Stat(label="Pipeline Value", value=total_value, formatter=format_currency)
        )

        # Average deal size
        avg_value = db.session.query(func.avg(self.model.value)).scalar() or 0
        stats.append(
            Stat(label="Avg Deal Size", value=avg_value, formatter=format_currency)
        )

        # Win rate
        closed_won = self.model.query.filter_by(stage="closed_won").count()
        closed_lost = self.model.query.filter_by(stage="closed_lost").count()
        total_closed = closed_won + closed_lost

        if total_closed > 0:
            win_rate = (closed_won / total_closed) * 100
            stats.append(
                Stat(label="Win Rate", value=win_rate, formatter=format_percentage)
            )
        else:
            stats.append(Stat(label="Win Rate", value="N/A"))

        return stats

    def _task_stats(self) -> List[Stat]:
        """Generate task-specific statistics.

        Returns:
            List of task statistics.
        """
        stats = []
        now = datetime.now().date()

        # Overdue
        overdue = self.model.query.filter(
            self.model.due_date < now, self.model.status != "completed"
        ).count()
        stats.append(Stat(label="Overdue", value=overdue))

        # Due this week
        week_end = now + timedelta(days=7)
        due_week = self.model.query.filter(
            self.model.due_date.between(now, week_end), self.model.status != "completed"
        ).count()
        stats.append(Stat(label="Due This Week", value=due_week))

        # Completed
        completed = self.model.query.filter_by(status="completed").count()
        stats.append(Stat(label="Completed", value=completed))

        return stats

    def _user_stats(self) -> List[Stat]:
        """Generate user/team statistics.

        Returns:
            List of user statistics.
        """
        from app.models import Task, Opportunity, User

        stats = []

        # Total team members
        team_members = User.query.count()
        stats.append(Stat(label="Team Members", value=team_members))

        # Total opportunities
        total_opps = Opportunity.query.count()
        stats.append(Stat(label="Total Opportunities", value=total_opps))

        # Open tasks
        open_tasks = Task.query.filter(Task.status != "complete").count()
        stats.append(Stat(label="Open Tasks", value=open_tasks))

        return stats
