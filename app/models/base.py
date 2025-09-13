from typing import Dict, Any
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