from . import db
from app.utils.core.model_helpers import auto_serialize


class BaseModel(db.Model):
    """Base model class with common serialization methods"""
    
    __abstract__ = True
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        # Default implementation - can be overridden by subclasses
        return auto_serialize(self)
    
    def to_display_dict(self):
        """Convert model to dictionary for display purposes"""
        # Default implementation - can be overridden by subclasses
        return self.to_dict()