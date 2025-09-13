"""
Dynamic CSS Class Generation
ADR-011: Simple CSS Architecture Implementation

Provides functions for generating entity-specific CSS classes dynamically.
Supports patterns like {{entity_name}}-card, {{entity_name}}-{{status}}, etc.
"""

from typing import Dict, Optional, List
from flask import request


class DynamicCSSGenerator:
    """
    Dynamic CSS class generator for entity-specific styling.
    
    Implements ADR-011 dynamic class generation patterns:
    - Entity cards: companies-card, tasks-card, etc.
    - Entity states: companies-active, tasks-completed, etc.
    - Entity buttons: btn-companies-primary, btn-tasks-primary, etc.
    """
    
    # Entity name mappings (singular → plural for consistency)
    ENTITY_MAPPINGS = {
        'company': 'companies',
        'task': 'tasks', 
        'opportunity': 'opportunities',
        'stakeholder': 'stakeholders',
        'team': 'teams',
        'user': 'users'
    }
    
    @classmethod
    def get_entity_name(cls, entity_or_model) -> str:
        """
        Extract entity name from various inputs.
        
        Args:
            entity_or_model: Can be string, model class, or model instance
            
        Returns:
            Standardized entity name (plural form)
        """
        if isinstance(entity_or_model, str):
            entity_name = entity_or_model.lower()
        elif hasattr(entity_or_model, '__tablename__'):
            # SQLAlchemy model class or instance
            entity_name = entity_or_model.__tablename__.rstrip('s')  # Remove plural 's'
        elif hasattr(entity_or_model, '__class__'):
            # Model instance
            entity_name = entity_or_model.__class__.__name__.lower()
        else:
            entity_name = str(entity_or_model).lower()
            
        # Convert to plural using mapping
        return cls.ENTITY_MAPPINGS.get(entity_name, f"{entity_name}s")
    
    @classmethod
    def entity_card_class(cls, entity_or_model, additional_classes: List[str] = None) -> str:
        """
        Generate entity-specific card CSS class.
        
        Args:
            entity_or_model: Entity identifier
            additional_classes: Additional classes to include
            
        Returns:
            CSS class string like "companies-card" or "tasks-card"
        """
        entity_name = cls.get_entity_name(entity_or_model)
        classes = [f"{entity_name}-card"]
        
        if additional_classes:
            classes.extend(additional_classes)
            
        return " ".join(classes)
    
    @classmethod
    def entity_status_class(cls, entity_or_model, status: str) -> str:
        """
        Generate entity-specific status CSS class.
        
        Args:
            entity_or_model: Entity identifier
            status: Status value (active, inactive, completed, etc.)
            
        Returns:
            CSS class string like "companies-active" or "tasks-completed"
        """
        entity_name = cls.get_entity_name(entity_or_model)
        return f"{entity_name}-{status.lower()}"
    
    @classmethod
    def entity_button_class(cls, entity_or_model, variant: str = "primary") -> str:
        """
        Generate entity-specific button CSS class.
        
        Args:
            entity_or_model: Entity identifier
            variant: Button variant (primary, secondary, etc.)
            
        Returns:
            CSS class string like "btn-companies-primary"
        """
        entity_name = cls.get_entity_name(entity_or_model)
        return f"btn-{entity_name}-{variant}"
    
    @classmethod
    def entity_badge_class(cls, entity_or_model) -> str:
        """
        Generate entity-specific badge CSS class.
        
        Args:
            entity_or_model: Entity identifier
            
        Returns:
            CSS class string like "companies-badge"
        """
        entity_name = cls.get_entity_name(entity_or_model)
        return f"{entity_name}-badge"
    
    @classmethod
    def get_current_entity_context(cls) -> Optional[str]:
        """
        Extract current entity context from request path.
        
        Returns:
            Current entity name based on URL path, or None
        """
        if not request:
            return None
            
        path_parts = request.path.strip('/').split('/')
        
        # Check for entity names in path
        for part in path_parts:
            if part.lower() in cls.ENTITY_MAPPINGS.values():
                return part.lower()
            elif part.lower() in cls.ENTITY_MAPPINGS.keys():
                return cls.ENTITY_MAPPINGS[part.lower()]
                
        return None


def inject_css_context() -> Dict[str, any]:
    """
    Flask context processor for CSS class generation.
    ADR-011: Provides dynamic CSS class generation to all templates.
    
    Returns:
        Dictionary of CSS generation functions for template use
    """
    return {
        'css_entity_card': DynamicCSSGenerator.entity_card_class,
        'css_entity_status': DynamicCSSGenerator.entity_status_class,
        'css_entity_button': DynamicCSSGenerator.entity_button_class,
        'css_entity_badge': DynamicCSSGenerator.entity_badge_class,
        'current_entity': DynamicCSSGenerator.get_current_entity_context(),
    }


# Template helper functions for backward compatibility
def get_entity_css_classes(entity_or_model, status: Optional[str] = None) -> Dict[str, str]:
    """
    Get all CSS classes for an entity.
    
    Args:
        entity_or_model: Entity identifier
        status: Optional status for status-specific classes
        
    Returns:
        Dictionary of CSS class types and their values
    """
    generator = DynamicCSSGenerator()
    
    classes = {
        'card': generator.entity_card_class(entity_or_model),
        'button': generator.entity_button_class(entity_or_model),
        'badge': generator.entity_badge_class(entity_or_model),
    }
    
    if status:
        classes['status'] = generator.entity_status_class(entity_or_model, status)
    
    return classes