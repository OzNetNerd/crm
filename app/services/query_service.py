"""Query service for building and executing database queries."""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Query


class QueryService:
    """Service for building and executing database queries."""

    @staticmethod
    def build_filtered_query(model: type, filters: Dict[str, Any]) -> Query:
        """Build a filtered query for a model.

        Args:
            model: SQLAlchemy model class.
            filters: Dictionary of field:value filters.

        Returns:
            Filtered SQLAlchemy query.
        """
        query = model.query

        for field, value in filters.items():
            if value and hasattr(model, field):
                query = query.filter(getattr(model, field) == value)

        return query

    @staticmethod
    def apply_sorting(
        query: Query,
        model: type,
        sort_by: str,
        direction: str = "asc"
    ) -> Query:
        """Apply sorting to a query.

        Args:
            query: SQLAlchemy query to sort.
            model: SQLAlchemy model class.
            sort_by: Field name to sort by.
            direction: Sort direction ('asc' or 'desc').

        Returns:
            Sorted SQLAlchemy query.
        """
        if not hasattr(model, sort_by):
            sort_by = "id"

        sort_field = getattr(model, sort_by)

        if direction.lower() == "desc":
            return query.order_by(sort_field.desc())

        return query.order_by(sort_field)