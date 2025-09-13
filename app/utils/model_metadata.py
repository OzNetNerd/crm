"""
Universal Model Metadata Framework - ADR-016 Implementation

Provides comprehensive metadata management for dynamic model handling,
form generation, API serialization, and UI configuration.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class FieldType(Enum):
    """Universal field type enumeration"""
    STRING = "string"
    INTEGER = "integer" 
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    FOREIGN_KEY = "foreign_key"
    MANY_TO_MANY = "many_to_many"
    EMAIL = "email"
    URL = "url"
    TEXT = "text"
    JSON = "json"


@dataclass
class FieldMetadata:
    """Comprehensive field metadata for universal model handling"""
    name: str
    field_type: FieldType
    
    # Display metadata
    display_name: str = None
    help_text: str = None
    placeholder: str = None
    
    # Validation metadata
    required: bool = False
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    choices: Optional[List[tuple]] = None
    validators: List[Callable] = field(default_factory=list)
    
    # Form metadata
    widget: str = None
    widget_attrs: Dict[str, Any] = field(default_factory=dict)
    form_field_class: str = None
    
    # API metadata
    serializable: bool = True
    read_only: bool = False
    write_only: bool = False
    api_name: str = None
    
    # Relationship metadata
    related_model: str = None
    related_field: str = None
    
    # UI metadata
    sortable: bool = True
    filterable: bool = True
    searchable: bool = False
    list_display: bool = True
    detail_display: bool = True
    
    def __post_init__(self):
        if self.display_name is None:
            self.display_name = self.name.replace('_', ' ').title()
        if self.api_name is None:
            self.api_name = self.name


@dataclass
class ModelMetadata:
    """Comprehensive model metadata for universal handling"""
    model_class: type
    fields: Dict[str, FieldMetadata] = field(default_factory=dict)
    
    # Display metadata
    display_name: str = None
    display_name_plural: str = None
    description: str = None
    
    # API metadata
    api_endpoint: str = None
    allowed_methods: List[str] = field(default_factory=lambda: ['GET', 'POST', 'PUT', 'DELETE'])
    
    # Form metadata
    form_fields: List[str] = field(default_factory=list)
    form_exclude: List[str] = field(default_factory=list)
    form_layout: Dict[str, Any] = field(default_factory=dict)
    
    # List/Table metadata
    list_fields: List[str] = field(default_factory=list)
    list_filters: List[str] = field(default_factory=list)
    list_search_fields: List[str] = field(default_factory=list)
    list_per_page: int = 20
    
    # Permissions metadata
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        # Extract from entity config first if available - USE THE PROVIDED VALUES
        if hasattr(self.model_class, '__entity_config__'):
            config = self.model_class.__entity_config__
            if self.display_name is None:
                self.display_name = config.get('display_name_singular', self.model_class.__name__)
            if self.display_name_plural is None:
                self.display_name_plural = config.get('display_name', self.display_name + 's')
            if self.api_endpoint is None:
                self.api_endpoint = config.get('endpoint_name', self.display_name.lower() + 's')
        else:
            # Fallback to defaults
            if self.display_name is None:
                self.display_name = self.model_class.__name__
            if self.display_name_plural is None:
                self.display_name_plural = self.display_name + 's'
            if self.api_endpoint is None:
                if hasattr(self.model_class, '__tablename__'):
                    self.api_endpoint = self.model_class.__tablename__
                else:
                    self.api_endpoint = self.display_name.lower() + 's'
            
        # Auto-discover fields if not provided
        if not self.fields:
            self._discover_fields()
            
        # Set default form and list fields
        if not self.form_fields:
            self.form_fields = [name for name, meta in self.fields.items() 
                              if not meta.read_only and name != 'id']
        if not self.list_fields:
            self.list_fields = [name for name, meta in self.fields.items() 
                              if meta.list_display][:6]  # Limit to 6 columns
    
    def _discover_fields(self):
        """Discover fields from model class using introspection"""
        # This integrates with existing __entity_config__ until full migration
        if hasattr(self.model_class, '__entity_config__'):
            config = self.model_class.__entity_config__
            # Extract field information from existing config
            self._extract_from_entity_config(config)
        else:
            # Fallback to SQLAlchemy introspection
            self._discover_from_sqlalchemy()
    
    def _extract_from_entity_config(self, config):
        """Extract field metadata from existing __entity_config__"""
        # This is transitional - allows gradual migration from legacy patterns
        if hasattr(self.model_class, '__table__'):
            for column in self.model_class.__table__.columns:
                field_type = self._map_sqlalchemy_type(column.type)
                self.fields[column.name] = FieldMetadata(
                    name=column.name,
                    field_type=field_type,
                    required=not column.nullable,
                    max_length=getattr(column.type, 'length', None)
                )
    
    def _discover_from_sqlalchemy(self):
        """Discover fields directly from SQLAlchemy model"""
        if hasattr(self.model_class, '__table__'):
            for column in self.model_class.__table__.columns:
                field_type = self._map_sqlalchemy_type(column.type)
                self.fields[column.name] = FieldMetadata(
                    name=column.name,
                    field_type=field_type,
                    required=not column.nullable,
                    max_length=getattr(column.type, 'length', None),
                    sortable=True,
                    filterable=column.name != 'id',
                    list_display=column.name in ['id', 'name', 'title', 'created_at', 'status']
                )
    
    def _map_sqlalchemy_type(self, column_type):
        """Map SQLAlchemy types to FieldType enum"""
        from sqlalchemy import String, Integer, DateTime, Date, Boolean, Text, Numeric
        
        type_mapping = {
            String: FieldType.STRING,
            Integer: FieldType.INTEGER,
            Numeric: FieldType.DECIMAL,
            DateTime: FieldType.DATETIME,
            Date: FieldType.DATE,
            Boolean: FieldType.BOOLEAN,
            Text: FieldType.TEXT,
        }
        
        for sql_type, field_type in type_mapping.items():
            if isinstance(column_type, sql_type):
                return field_type
        
        return FieldType.STRING  # Default fallback
    
    def get_field_metadata(self, field_name: str) -> FieldMetadata:
        """Get metadata for specific field"""
        if field_name not in self.fields:
            raise ValueError(f"Field '{field_name}' not found in {self.model_class.__name__}")
        return self.fields[field_name]
    
    def get_serializable_fields(self, context='api') -> List[str]:
        """Get fields appropriate for serialization in given context"""
        return [name for name, meta in self.fields.items() 
                if meta.serializable and not meta.write_only]
    
    def get_form_fields(self, exclude_readonly=True) -> List[str]:
        """Get fields appropriate for forms"""
        fields = self.form_fields.copy()
        if exclude_readonly:
            fields = [f for f in fields if not self.fields[f].read_only]
        return [f for f in fields if f not in self.form_exclude]
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against field metadata"""
        validated = {}
        for field_name, value in data.items():
            if field_name in self.fields:
                field_meta = self.fields[field_name]
                # Apply validation logic based on field metadata
                validated_value = self._validate_field_value(field_meta, value)
                validated[field_name] = validated_value
            else:
                validated[field_name] = value  # Pass through unknown fields
        return validated
    
    def _validate_field_value(self, field_meta: FieldMetadata, value):
        """Apply field-specific validation logic"""
        if value is None and field_meta.required:
            raise ValueError(f"Field '{field_meta.name}' is required")
        
        if value is not None:
            # Apply max_length validation
            if field_meta.max_length and isinstance(value, str):
                if len(value) > field_meta.max_length:
                    raise ValueError(f"Field '{field_meta.name}' exceeds maximum length of {field_meta.max_length}")
            
            # Apply custom validators
            for validator in field_meta.validators:
                validator(value)
        
        return value