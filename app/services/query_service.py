"""Query service for building and executing database queries."""

from typing import Any, Dict
from sqlalchemy.orm import Query


class QueryService:
    """Service for building and executing database queries."""

    @staticmethod
    def build_filtered_query(model: type, filters: Dict[str, Any]) -> Query:
        """Build a filtered query for a model.

        Args:
            model: SQLAlchemy model class.
            filters: Dictionary of field:value filters.
                     Values can be single values or lists for multi-select.

        Returns:
            Filtered SQLAlchemy query.
        """
        query = model.query

        for field, value in filters.items():
            if value and hasattr(model, field):
                # Special handling for probability field with ranges
                if field == "probability" and model.__name__ == "Opportunity":
                    # Parse probability ranges and build filter
                    if isinstance(value, str):
                        values = [v.strip() for v in value.split(",") if v.strip()]
                    elif isinstance(value, list):
                        values = value
                    else:
                        values = [value]

                    # Build OR conditions for each range
                    from sqlalchemy import or_
                    conditions = []
                    for range_val in values:
                        if range_val == "0-20":
                            conditions.append(model.probability <= 20)
                        elif range_val == "21-40":
                            conditions.append((model.probability > 20) & (model.probability <= 40))
                        elif range_val == "41-60":
                            conditions.append((model.probability > 40) & (model.probability <= 60))
                        elif range_val == "61-80":
                            conditions.append((model.probability > 60) & (model.probability <= 80))
                        elif range_val == "81-100":
                            conditions.append(model.probability > 80)

                    if conditions:
                        query = query.filter(or_(*conditions))

                # Handle regular fields
                elif isinstance(value, str) and "," in value:
                    values = [v.strip() for v in value.split(",") if v.strip()]
                    if values:
                        query = query.filter(getattr(model, field).in_(values))
                elif isinstance(value, list):
                    # Handle list directly
                    if value:
                        query = query.filter(getattr(model, field).in_(value))
                else:
                    # Single value
                    query = query.filter(getattr(model, field) == value)

        return query

    @staticmethod
    def apply_sorting(
        query: Query, model: type, sort_by: str, direction: str = "asc"
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
