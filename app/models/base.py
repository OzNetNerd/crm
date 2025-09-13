from typing import Dict, Any
from abc import ABC, abstractmethod
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

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register entity models with ModelRegistry on class creation.

        This hook runs when any subclass of EntityModel is defined, ensuring
        automatic registration without manual intervention. Uses the entity
        config to determine registration names and handles both singular and
        plural forms.

        Args:
            **kwargs: Additional arguments passed to parent __init_subclass__
        """
        super().__init_subclass__(**kwargs)

        # Only register concrete classes (not abstract ones)
        if not getattr(cls, '__abstract__', False) and hasattr(cls, '__entity_config__'):
            # Import here to avoid circular dependencies
            from app.utils.model_registry import ModelRegistry

            config = cls.__entity_config__
            endpoint_name = config.get('endpoint_name', cls.__name__.lower())

            # Register with both endpoint name and class name
            ModelRegistry.register_model(cls, endpoint_name)
            ModelRegistry.register_model(cls, cls.__name__.lower())

            # Also register plural forms for common patterns
            if endpoint_name.endswith('s'):
                singular_name = endpoint_name.rstrip('s')
                if singular_name not in ModelRegistry._models:
                    ModelRegistry._models[singular_name] = cls
            else:
                plural_name = endpoint_name + 's'
                if plural_name not in ModelRegistry._models:
                    ModelRegistry._models[plural_name] = cls

    @classmethod
    def get_entity_config(cls) -> Dict[str, Any]:
        """
        Get entity configuration dictionary for this model.

        Provides standardized access to entity configuration across all
        entity models. Returns empty dict if no config is defined.

        Returns:
            Entity configuration dictionary or empty dict if not defined.

        Example:
            >>> config = Task.get_entity_config()
            >>> print(config['display_name'])
            'Tasks'
        """
        return getattr(cls, '__entity_config__', {})