"""
Dynamic Card Configuration Builder

Generates card configurations from SQLAlchemy model metadata.
Replaces hardcoded card builders with dynamic, model-driven approach.
"""

from flask import url_for
from sqlalchemy import String, Integer, DateTime, Boolean, Text, Date
from datetime import datetime, date


class CardConfigBuilder:
    """Builds card configurations dynamically from model introspection."""
    
    # Map SQLAlchemy types to display types
    TYPE_MAPPING = {
        String: 'text',
        Integer: 'number',
        DateTime: 'datetime',
        Date: 'date', 
        Boolean: 'boolean',
        Text: 'text'
    }
    
    # Special field mappings
    SPECIAL_FIELDS = {
        'value': {'type': 'currency', 'classes': 'text-green-600 font-semibold'},
        'probability': {'type': 'progress', 'max_value': 100},
        'status': {'type': 'badge', 'color': 'auto'},
        'stage': {'type': 'badge', 'color': 'blue'},
        'priority': {'type': 'badge', 'color': 'auto'},
        'role': {'type': 'badge', 'color': 'green'},
        'size': {'type': 'badge', 'color': 'blue'},
        'industry': {'type': 'text', 'classes': 'text-gray-600'},
        'email': {'type': 'link', 'url_template': 'mailto:{value}'},
        'phone': {'type': 'text', 'classes': 'font-mono'},
        'website': {'type': 'link', 'url_template': '{value}'}
    }
    
    @classmethod
    def build_card_config(cls, entity_type, entity):
        """Build complete card configuration for an entity."""
        model_class = entity.__class__
        
        return {
            'header': cls._build_header_config(model_class, entity),
            'actions': cls._build_actions_config(entity_type, entity),
            'body': cls._build_body_config(model_class, entity),
            'expanded': cls._build_expanded_config(model_class, entity)
        }
    
    @classmethod
    def _build_header_config(cls, model_class, entity):
        """Build header section with primary display fields."""
        header_fields = []
        
        # Always include name/title field first with entity-specific styling
        name_field = cls._get_name_field(model_class)
        if name_field:
            entity_name = model_class.__name__.lower()
            # Map entity types to semantic classes for consistent styling with dashboard
            entity_class_mapping = {
                'company': 'text-company-name',
                'stakeholder': 'text-stakeholder-name',
                'team': 'text-team-member',
                'opportunity': 'font-medium text-gray-900'  # Opportunity names don't have special styling
            }
            name_class = entity_class_mapping.get(entity_name, 'font-medium text-gray-900')
            header_fields.append({
                'name': name_field,
                'type': 'text',
                'classes': name_class
            })
        
        # Add important status/category fields
        for column_name, column in model_class.__table__.columns.items():
            if column_name in ['status', 'stage', 'priority', 'role', 'size']:
                field_config = cls._build_field_config(column_name, column)
                if field_config:
                    header_fields.append(field_config)
                    
        # Add value field for opportunity-like entities
        if hasattr(entity, 'value') and entity.value is not None:
            header_fields.append({
                'name': 'value',
                'type': 'currency',
                'classes': 'text-green-600 font-semibold'
            })
                    
        return {
            'type': 'fields',
            'layout': 'horizontal',
            'entity': entity,
            'fields': header_fields[:3]  # Limit header to 3 fields
        }
    
    @classmethod
    def _build_actions_config(cls, entity_type, entity):
        """Build actions section with available routes."""
        actions = []
        
        # Check for common routes and add if they exist
        route_checks = [
            (f'{entity_type}s.show', 'eye', 'View'),
            (f'{entity_type}s.edit', 'pencil', 'Edit'),
        ]
        
        for route_name, icon, text in route_checks:
            try:
                url = url_for(route_name, id=entity.id)
                actions.append({
                    'type': 'link',
                    'url': url,
                    'icon': icon,
                    'text': text,
                    'classes': 'btn btn-sm btn-outline'
                })
            except:
                # Route doesn't exist, skip
                pass
                
        return {
            'layout': 'horizontal',
            'actions': actions
        }
    
    @classmethod
    def _build_body_config(cls, model_class, entity):
        """Build body section with secondary fields."""
        body_fields = []
        
        # Add descriptive and secondary fields
        secondary_fields = ['description', 'close_date', 'expected_close_date', 
                           'probability', 'website', 'email', 'phone', 'due_date']
        
        for column_name, column in model_class.__table__.columns.items():
            if column_name in secondary_fields:
                field_config = cls._build_field_config(column_name, column)
                if field_config:
                    field_config['show_label'] = True
                    body_fields.append(field_config)
                    
        return {
            'type': 'fields',
            'layout': 'vertical',
            'entity': entity,
            'fields': body_fields
        }
    
    @classmethod 
    def _build_expanded_config(cls, model_class, entity):
        """Build expanded section with metadata fields."""
        expanded_fields = []
        
        # Add timestamps and metadata
        metadata_fields = ['created_at', 'updated_at']
        
        for column_name, column in model_class.__table__.columns.items():
            if column_name in metadata_fields:
                field_config = cls._build_field_config(column_name, column)
                if field_config:
                    field_config['show_label'] = True
                    expanded_fields.append(field_config)
                    
        return {
            'type': 'fields',
            'layout': 'vertical',
            'entity': entity,
            'fields': expanded_fields
        }
    
    @classmethod
    def _build_field_config(cls, column_name, column):
        """Build configuration for a single field."""
        # Check for special field handling
        if column_name in cls.SPECIAL_FIELDS:
            config = cls.SPECIAL_FIELDS[column_name].copy()
            config['name'] = column_name
            return config
        
        # Use column info if available
        info = column.info if hasattr(column, 'info') else {}
        field_type = cls._get_field_type(column)
        
        config = {
            'name': column_name,
            'type': field_type,
        }
        
        # Add display label from column info
        if 'display_label' in info:
            config['label'] = info['display_label']
            
        return config
    
    @classmethod
    def _get_field_type(cls, column):
        """Determine display type for a column."""
        column_type = type(column.type)
        
        # Handle special naming patterns
        column_name = column.name.lower()
        if 'date' in column_name:
            return 'date'
        elif 'email' in column_name:
            return 'link'
        elif 'url' in column_name or 'website' in column_name:
            return 'link'
        elif column_name in ['status', 'stage', 'priority', 'role']:
            return 'badge'
        elif column_name in ['value', 'price', 'cost', 'amount']:
            return 'currency'
            
        # Fall back to type mapping
        return cls.TYPE_MAPPING.get(column_type, 'text')
    
    @classmethod
    def _get_name_field(cls, model_class):
        """Get the primary name/title field for an entity."""
        # Entity-specific field mappings for proper data hierarchy
        entity_name = model_class.__name__.lower()
        entity_field_mapping = {
            'task': 'description',  # Tasks use description as primary field
            'company': 'name',
            'stakeholder': 'name',
            'opportunity': 'name',
            'team': 'name'
        }

        # Use entity-specific field if available
        if entity_name in entity_field_mapping:
            field_name = entity_field_mapping[entity_name]
            if hasattr(model_class, field_name):
                return field_name

        # Fall back to common candidates
        name_candidates = ['name', 'title', 'subject', 'email', 'description']
        for candidate in name_candidates:
            if hasattr(model_class, candidate):
                return candidate

        return None