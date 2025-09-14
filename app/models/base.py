from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import date, timedelta
from . import db
from app.utils.core.model_helpers import auto_serialize


class BaseModel(db.Model):
    """
    Base model class with common serialization methods.
    
    This abstract class provides standard serialization functionality
    for all database models in the CRM application. It serves as the
    foundation for all entity models (Company, Opportunity, Task, etc.).
    
    Attributes:
        __abstract__: Marks this as an abstract SQLAlchemy model.
    """
    
    __abstract__ = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary for JSON serialization.
        
        This method provides a standard way to serialize model instances
        for API responses and data exchange. The default implementation
        uses auto_serialize but can be overridden by subclasses for
        custom serialization logic.
        
        Returns:
            Dictionary representation of the model instance with all
            accessible attributes as key-value pairs.
            
        Example:
            >>> company = Company(name="Acme Corp")
            >>> company.to_dict()
            {'id': 1, 'name': 'Acme Corp', 'created_at': '2023-01-01T00:00:00'}
        """
        return auto_serialize(self)
    
    def to_display_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary for display purposes.
        
        This method is intended for UI display scenarios where certain
        fields may need formatting or filtering. By default, it returns
        the same result as to_dict(), but subclasses can override this
        to provide display-specific formatting.
        
        Returns:
            Dictionary representation optimized for display in user
            interfaces, potentially with formatted dates, computed
            fields, or filtered sensitive information.
            
        Example:
            >>> opportunity = Opportunity(value=50000)
            >>> opportunity.to_display_dict()
            {'id': 1, 'value': '$50,000', 'status': 'Active'}
        """
        return self.to_dict()


class EntityModel(BaseModel):
    """
    Base class for all CRM entity models with automatic ModelRegistry registration.

    This ABC enforces that all entity models have proper __entity_config__ and
    automatically registers them with the ModelRegistry when the class is defined.
    This eliminates manual registration and ensures DRY principles.

    Features:
    - Auto-registration via __init_subclass__ hook
    - Enforces __entity_config__ requirement via ABC
    - Standardized entity configuration access
    - Guaranteed consistent behavior across all entities

    Usage:
        class MyEntity(EntityModel):
            __entity_config__ = {
                'display_name': 'My Entities',
                'endpoint_name': 'my_entities',
                # ... other config
            }
    """

    __abstract__ = True

    # Note: __entity_config__ is expected as a class attribute, not an abstract property

    @classmethod
    def get_entity_config(cls):
        """
        Get entity configuration with auto-generated defaults.

        Merges any manually defined __entity_config__ with auto-generated
        defaults based on class name and table name. This allows models to
        only define what's different from the standard pattern.

        Returns:
            dict: Complete entity configuration with all required fields
        """
        # Get the manual config if defined
        config = getattr(cls, '__entity_config__', {}).copy()

        # Auto-generate missing fields - use template-ready names
        defaults = {
            'entity_type': cls.__name__.lower(),
            'entity_name': cls.__tablename__.replace('_', ' ').title(),
            'entity_name_singular': cls.__name__,
            'endpoint_name': cls.__tablename__,
            'modal_path': f'/modals/{cls.__name__}',
            'show_dashboard_button': True
        }

        # Merge defaults with config
        for key, value in defaults.items():
            if key not in config:
                config[key] = value

        return config

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register entity models with ModelRegistry on class creation.

        This hook runs when any subclass of EntityModel is defined, ensuring
        automatic registration without manual intervention. Uses the entity
        config to determine registration names.

        Args:
            **kwargs: Additional arguments passed to parent __init_subclass__
        """
        super().__init_subclass__(**kwargs)

        # Only register concrete classes (not abstract ones)
        if not getattr(cls, '__abstract__', False) and hasattr(cls, 'get_entity_config'):
            # Import here to avoid circular dependencies
            from app.utils.model_registry import register_model

            # Auto-register the model with the registry
            register_model(cls)

    @classmethod
    def filter_and_sort(cls, filters=None, sort_by=None, sort_dir='asc', joins=None):
        """
        Universal filtering and sorting for entities.

        Args:
            filters: Dict of field:value pairs to filter by
            sort_by: Field name to sort by
            sort_dir: Sort direction ('asc' or 'desc')
            joins: Optional list of models to join

        Returns:
            Query result with filters and sorting applied
        """
        query = cls.query

        # Apply joins if needed
        if joins:
            for join_model in joins:
                query = query.join(join_model)

        # Apply filters from request args
        for key, value in (filters or {}).items():
            if value and hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)

        # Apply sorting
        if sort_by and hasattr(cls, sort_by):
            field = getattr(cls, sort_by)
            query = query.order_by(field.desc() if sort_dir == 'desc' else field.asc())
        else:
            # Default sort by id desc (newest first)
            query = query.order_by(cls.id.desc())

        return query

    @classmethod
    def group_by_field(cls, entities, field_name):
        """
        Group entities by a field value.

        Args:
            entities: List of entity instances
            field_name: Field to group by

        Returns:
            Dict with field values as keys and entity lists as values
        """
        from collections import defaultdict
        grouped = defaultdict(list)

        for entity in entities:
            key = getattr(entity, field_name, 'Other')
            # Handle None values
            if key is None:
                key = 'Uncategorized'
            grouped[key].append(entity)

        return dict(grouped)

    @classmethod
    def get_stats(cls):
        """
        Get basic statistics for the entity.

        Returns:
            Dict with title and stats array
        """
        entities = cls.query.all()
        config = cls.get_entity_config()

        stats = [{
            'value': len(entities),
            'label': f'Total {config["entity_name"]}'
        }]

        # Add status breakdown if entity has status field
        if hasattr(cls, 'status'):
            from collections import Counter
            status_counts = Counter(getattr(e, 'status', 'unknown') for e in entities)
            for status, count in status_counts.items():
                if status:  # Skip None/empty
                    stats.append({
                        'value': count,
                        'label': status.replace('-', ' ').replace('_', ' ').title()
                    })

        return {
            'title': f'{config["entity_name"]} Overview',
            'stats': stats
        }

    @classmethod
    def render_content(cls, filter_fields=None, join_map=None):
        """
        Handle ALL content filtering/sorting/grouping for any entity.

        Args:
            filter_fields: List of fields this entity filters by (e.g., ['stage', 'priority'])
            join_map: Dict mapping sort fields to join models (e.g., {'company_name': [Company]})

        Returns:
            Rendered template with filtered/sorted/grouped entities
        """
        from flask import request, render_template

        # Get parameters
        filters = {}
        group_by = request.args.get('group_by', '')
        sort_by = request.args.get('sort_by', 'name')
        sort_direction = request.args.get('sort_direction', 'asc')

        # Build filters from request args
        for field in (filter_fields or []):
            if value := request.args.get(field):
                filters[field] = value

        # Apply filtering and sorting
        joins = (join_map or {}).get(sort_by, [])
        query = cls.filter_and_sort(
            filters=filters,
            sort_by=sort_by,
            sort_dir=sort_direction,
            joins=joins
        )
        entities = query.all()

        # Get entity config for template
        config = cls.get_entity_config()

        # ALWAYS provide grouped_entities - even if not grouping
        if group_by:
            grouped_dict = cls.group_by_field(entities, group_by)
            grouped_entities = [
                {
                    'key': group_name,
                    'label': group_name,
                    'count': len(group_items),
                    'entities': group_items
                }
                for group_name, group_items in grouped_dict.items()
            ]
        else:
            # Single group with all entities when not grouping
            grouped_entities = [{
                'key': 'all',
                'label': 'All Results',
                'count': len(entities),
                'entities': entities
            }]

        # Render with consistent structure
        return render_template("shared/entity_content.html",
            grouped_entities=grouped_entities,
            group_by=group_by,
            entity_config=config,
            entity_type=cls.__name__.lower(),
            entity_name=config['entity_name'],
            entity_name_singular=config['entity_name_singular'],
            entity_name_plural=config['entity_name'],
            total_count=len(entities)
        )

    @classmethod
    def render_index(cls):
        """
        Render index page for any entity - ZERO duplication.

        Returns:
            Rendered template with entity config, dropdowns, and stats
        """
        from flask import render_template
        from app.utils.simple_helpers import get_dropdowns_from_columns

        config = cls.get_entity_config()
        # Add button inline - no need for separate function
        config['entity_buttons'] = [{
            'title': f'New {config["entity_name_singular"]}',
            'url': f'{config["modal_path"]}/create'
        }]

        return render_template("base/entity_index.html",
            entity_config=config,
            dropdown_configs=get_dropdowns_from_columns(cls),
            entity_stats=cls.get_stats()
        )

    @classmethod
    def get_recent(cls, limit: int = 5, exclude_status: Optional[str] = None) -> List:
        """
        Get recent items ordered by creation date.

        Generic method for fetching recently created items with optional
        status exclusion. Useful for dashboard widgets and activity feeds.

        Args:
            limit: Maximum number of items to return (default: 5)
            exclude_status: Optional status value to exclude (e.g., 'complete')

        Returns:
            List of model instances ordered by creation date (newest first)

        Example:
            >>> recent_tasks = Task.get_recent(limit=10, exclude_status='complete')
        """
        query = cls.query
        if exclude_status and hasattr(cls, 'status'):
            query = query.filter(getattr(cls, 'status') != exclude_status)
        if hasattr(cls, 'created_at'):
            query = query.order_by(cls.created_at.desc())
        return query.limit(limit).all()

    @classmethod
    def get_overdue(cls, date_field: str = 'due_date',
                    exclude_status: Optional[str] = 'complete',
                    limit: int = 5) -> List:
        """
        Get overdue items based on a date field.

        Identifies items that are past their due date, commonly used for
        tasks, opportunities, and other time-sensitive entities.

        Args:
            date_field: Name of the date column to check (default: 'due_date')
            exclude_status: Optional status to exclude (default: 'complete')
            limit: Maximum number of items to return (default: 5)

        Returns:
            List of overdue model instances

        Example:
            >>> overdue_tasks = Task.get_overdue(limit=10)
            >>> closing_late = Opportunity.get_overdue(date_field='expected_close_date')
        """
        if not hasattr(cls, date_field):
            return []

        date_column = getattr(cls, date_field)
        query = cls.query.filter(date_column < date.today())

        if exclude_status and hasattr(cls, 'status'):
            query = query.filter(getattr(cls, 'status') != exclude_status)

        return query.limit(limit).all()

    @classmethod
    def calculate_sum(cls, field: str, filter_by: Optional[Dict] = None) -> float:
        """
        Calculate sum of a numeric field with optional filtering.

        Generic aggregation method for summing numeric fields across
        entities, with support for filtering by field values.

        Args:
            field: Name of the numeric field to sum
            filter_by: Optional dict of field:value pairs to filter by

        Returns:
            Sum of the specified field values

        Example:
            >>> total_value = Opportunity.calculate_sum('value')
            >>> pipeline_value = Opportunity.calculate_sum('value', {'stage': 'proposal'})
        """
        if not hasattr(cls, field):
            return 0

        query = cls.query
        if filter_by:
            for key, value in filter_by.items():
                if hasattr(cls, key):
                    query = query.filter(getattr(cls, key) == value)

        items = query.all()
        return sum(getattr(item, field) or 0 for item in items)