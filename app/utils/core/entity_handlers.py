"""
Entity Handler System - DRY OOP Solution for Entity Logic

Provides abstract base classes and composition patterns to eliminate
duplicated custom filtering, sorting, and grouping functions across
all entity route files.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
from sqlalchemy.orm import Query


class EntityHandler(ABC):
    """
    Abstract base class for entity-specific logic.

    Each entity (Opportunity, Company, etc.) implements this interface
    to provide sorting, filtering, and grouping configurations without
    duplicating the underlying logic.
    """

    @abstractmethod
    def get_sort_mapping(self) -> Dict[str, str]:
        """
        Return mapping of sort field names to SQLAlchemy expressions.

        Returns:
            Dict mapping sort keys to model attribute names

        Example:
            {'name': 'Opportunity.name', 'value': 'Opportunity.value'}
        """
        pass

    @abstractmethod
    def get_filter_mapping(self) -> Dict[str, str]:
        """
        Return mapping of filter types to model attribute names.

        Returns:
            Dict mapping filter keys to model attribute names

        Example:
            {'primary_filter': 'stage', 'secondary_filter': 'company.name'}
        """
        pass

    @abstractmethod
    def get_group_mapping(self) -> Dict[str, Dict[str, Any]]:
        """
        Return mapping of group field names to grouping configurations.

        Returns:
            Dict mapping group keys to grouping config dictionaries

        Example:
            {
                'stage': {
                    'field': 'stage',
                    'order': ['prospect', 'qualified', 'proposal'],
                    'default_value': 'Other'
                }
            }
        """
        pass

    def get_default_sort_field(self) -> str:
        """
        Return the default sort field for this entity.

        Returns:
            Default sort field name
        """
        sort_mapping = self.get_sort_mapping()
        return list(sort_mapping.keys())[0] if sort_mapping else 'id'


class UniversalEntityManager:
    """
    Universal entity management using composition pattern.

    Handles filtering, sorting, and grouping for any entity type
    using the provided EntityHandler implementation.
    """

    def __init__(self, model_class, entity_handler: EntityHandler):
        """
        Initialize with model class and entity handler.

        Args:
            model_class: SQLAlchemy model class
            entity_handler: EntityHandler implementation for this entity
        """
        self.model_class = model_class
        self.handler = entity_handler
        self._sort_mapping = entity_handler.get_sort_mapping()
        self._filter_mapping = entity_handler.get_filter_mapping()
        self._group_mapping = entity_handler.get_group_mapping()

    def apply_custom_filters(self, query: Query, filters: Dict[str, Any]) -> Query:
        """
        Apply entity-specific filters to query.

        Args:
            query: SQLAlchemy query object
            filters: Dict of filter values

        Returns:
            Filtered query object
        """
        for filter_key, filter_values in filters.items():
            if not filter_values:
                continue

            # Get the model attribute from mapping
            if filter_key in self._filter_mapping:
                attr_path = self._filter_mapping[filter_key]

                # Handle nested attributes (e.g., 'company.name')
                if '.' in attr_path:
                    # For now, handle simple join cases
                    # More complex joins can be added as needed
                    if filter_key == 'secondary_filter':
                        # This handles Company.name filtering for opportunities
                        from app.models import Company
                        query = query.filter(Company.name.in_(filter_values))
                else:
                    # Direct model attribute
                    model_attr = getattr(self.model_class, attr_path)
                    query = query.filter(model_attr.in_(filter_values))

        return query

    def apply_custom_sorting(self, query: Query, sort_by: str, sort_direction: str = 'asc') -> Query:
        """
        Apply entity-specific sorting to query.

        Args:
            query: SQLAlchemy query object
            sort_by: Sort field name
            sort_direction: 'asc' or 'desc'

        Returns:
            Sorted query object
        """
        if sort_by not in self._sort_mapping:
            # Fallback to default sort
            sort_by = self.handler.get_default_sort_field()

        if sort_by in self._sort_mapping:
            attr_name = self._sort_mapping[sort_by]
            model_attr = getattr(self.model_class, attr_name)

            if sort_direction == 'desc':
                return query.order_by(model_attr.desc().nulls_last())
            else:
                return query.order_by(model_attr.asc().nulls_last())

        return query

    def apply_custom_grouping(self, entities: List[Any], group_by: str) -> Optional[List[Dict[str, Any]]]:
        """
        Apply entity-specific grouping to entities.

        Args:
            entities: List of entity objects
            group_by: Group field name

        Returns:
            List of grouped entity dictionaries or None for default grouping
        """
        if group_by not in self._group_mapping:
            return None

        group_config = self._group_mapping[group_by]
        field_name = group_config['field']
        default_value = group_config.get('default_value', 'Other')
        order = group_config.get('order', [])

        # Group entities by field value
        grouped = defaultdict(list)
        for entity in entities:
            field_value = getattr(entity, field_name, None)

            # Handle relationship fields (e.g., entity.company.name)
            if field_value is None and '.' in field_name:
                obj = entity
                for attr in field_name.split('.'):
                    obj = getattr(obj, attr, None) if obj else None
                field_value = obj

            group_key = field_value or default_value
            grouped[group_key].append(entity)

        # Build result in specified order
        result = []
        if order:
            # Use specified order
            for key in order:
                if key in grouped and grouped[key]:
                    result.append({
                        "key": key,
                        "label": self._format_group_label(key, group_config),
                        "entities": grouped[key],
                        "count": len(grouped[key])
                    })
        else:
            # Use alphabetical order
            for key in sorted(grouped.keys()):
                if grouped[key]:
                    result.append({
                        "key": key,
                        "label": self._format_group_label(key, group_config),
                        "entities": grouped[key],
                        "count": len(grouped[key])
                    })

        return result

    def _format_group_label(self, key: str, group_config: Dict[str, Any]) -> str:
        """
        Format group label for display.

        Args:
            key: Group key
            group_config: Group configuration

        Returns:
            Formatted label string
        """
        # Handle special formatting rules
        if key and '-' in key:
            return key.replace('-', ' ').title()
        return str(key).title() if key else 'Other'


class MetadataDrivenHandler(EntityHandler):
    """
    Metadata-driven handler that automatically extracts configurations
    from SQLAlchemy model metadata instead of hardcoding values.
    """

    def __init__(self, model_class):
        """Initialize with SQLAlchemy model class."""
        self.model_class = model_class
        self._sort_mapping = None
        self._filter_mapping = None
        self._group_mapping = None

    def get_sort_mapping(self) -> Dict[str, str]:
        """Extract sortable fields from model metadata."""
        if self._sort_mapping is None:
            self._sort_mapping = {}
            for column in self.model_class.__table__.columns:
                info = column.info or {}
                if info.get('sortable', False) or column.name in ['name', 'id', 'created_at']:
                    self._sort_mapping[column.name] = column.name
        return self._sort_mapping

    def get_filter_mapping(self) -> Dict[str, str]:
        """Extract filterable fields from model metadata."""
        if self._filter_mapping is None:
            # For now, use simple heuristics based on field types and choices
            self._filter_mapping = {}
            for column in self.model_class.__table__.columns:
                info = column.info or {}
                if 'choices' in info:
                    # Fields with choices become primary filters
                    if not self._filter_mapping.get('primary_filter'):
                        self._filter_mapping['primary_filter'] = column.name

            # Add relationship-based filters
            if hasattr(self.model_class, 'company'):
                self._filter_mapping['secondary_filter'] = 'company.name'

        return self._filter_mapping

    def get_group_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Extract groupable fields from model metadata."""
        if self._group_mapping is None:
            self._group_mapping = {}

            for column in self.model_class.__table__.columns:
                info = column.info or {}

                # Check if field is marked as groupable
                if info.get('groupable', False):
                    group_config = {
                        'field': column.name,
                        'default_value': 'Other'
                    }

                    # Extract choices order if available
                    if 'choices' in info:
                        choices = info['choices']
                        group_config['order'] = list(choices.keys()) + ['Other']

                    # Handle special date groupings
                    if 'date_groupings' in info:
                        group_config.update(info['date_groupings'])

                    self._group_mapping[column.name] = group_config

            # Add relationship-based grouping
            if hasattr(self.model_class, 'company'):
                self._group_mapping['company'] = {
                    'field': 'company.name',
                    'default_value': 'No Company'
                }

        return self._group_mapping


class OpportunityHandler(MetadataDrivenHandler):
    """Opportunity handler using metadata-driven approach."""

    def __init__(self):
        from app.models.opportunity import Opportunity
        super().__init__(Opportunity)


class CompanyHandler(MetadataDrivenHandler):
    """Company handler using metadata-driven approach."""

    def __init__(self):
        from app.models.company import Company
        super().__init__(Company)


class StakeholderHandler(MetadataDrivenHandler):
    """Stakeholder handler using metadata-driven approach."""

    def __init__(self):
        from app.models.stakeholder import Stakeholder
        super().__init__(Stakeholder)


class TeamHandler(MetadataDrivenHandler):
    """Team handler using metadata-driven approach."""

    def __init__(self):
        from app.models.user import User
        super().__init__(User)


class TaskHandler(MetadataDrivenHandler):
    """Task handler using metadata-driven approach."""

    def __init__(self):
        from app.models.task import Task
        super().__init__(Task)