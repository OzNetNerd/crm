"""
Entity Configuration System - DRY approach using actual model metadata

Extracts configuration from SQLAlchemy models automatically where possible,
with minimal overrides for presentation-specific data (icons, empty states).

This follows DRY principles by utilizing existing model information rather than duplicating it.
"""

import inspect
from dataclasses import dataclass
from typing import Dict, Optional, Type

# Pluralization engine for automatic plural forms
try:
    from inflect import engine
    p = engine()
except ImportError:
    # Fallback if inflect is not available
    class SimplePluralizationEngine:
        def plural(self, word):
            # Simple pluralization rules
            if word.endswith('y'):
                return word[:-1] + 'ies'
            elif word.endswith(('s', 'sh', 'ch', 'x', 'z')):
                return word + 'es'
            else:
                return word + 's'
    
    p = SimplePluralizationEngine()


@dataclass
class EmptyStateConfig:
    """Configuration for empty state displays"""
    title: str
    subtitle: str


@dataclass 
class EntityConfig:
    """Complete configuration for an entity type"""
    icon: str
    singular: str
    plural: str
    empty_state: EmptyStateConfig
    
    # Optional display configurations
    display_name: Optional[str] = None
    model_class: Optional[Type] = None
    table_name: Optional[str] = None


class EntityConfigRegistry:
    """Registry for all entity configurations - DRY approach using model metadata"""
    
    # Only store presentation-specific data (icons)
    # All text and labels come from model configs to avoid duplication
    _presentation_overrides: Dict[str, Dict] = {
        'task': {
            'icon': 'clipboard-list'
        },
        'stakeholder': {
            'icon': 'user'
        },
        'company': {
            'icon': 'building-office-alt'
        },
        'opportunity': {
            'icon': 'currency-dollar-circle'
        },
        'user': {
            'icon': 'user-circle'
        },
        'note': {
            'icon': 'document-text'
        }
    }
    
    _model_registry: Dict[str, Type] = {}
    
    @classmethod
    def _register_models(cls):
        """Auto-register models from app.models - DRY approach"""
        if cls._model_registry:
            return  # Already registered
            
        try:
            from app.utils.core.model_introspection import get_all_entity_models
            
            # Build mapping dynamically from model configurations
            all_models = get_all_entity_models()
            cls._model_registry = {}
            
            for model_class in all_models:
                # Use model metadata for proper singular/plural handling
                from app.utils.model_registry import ModelRegistry
                model_name = model_class.__name__.lower()
                metadata = ModelRegistry.get_model_metadata(model_name)

                # Register by singular display name
                entity_type = metadata.display_name.lower()
                cls._model_registry[entity_type] = model_class

                # Also register by plural display name
                plural_type = metadata.display_name_plural.lower()
                cls._model_registry[plural_type] = model_class
                        
        except ImportError:
            # Fallback if models aren't available
            pass
    
    @classmethod
    def _extract_from_model(cls, entity_type: str) -> Dict:
        """Extract metadata from SQLAlchemy model - avoiding duplication"""
        cls._register_models()
        
        model_class = cls._model_registry.get(entity_type)
        if not model_class:
            return {}
            
        # Extract singular form from model class name
        class_name = model_class.__name__.lower()
        
        # Extract plural from table name if available
        table_name = getattr(model_class, '__tablename__', None)
        
        # Generate plural form automatically
        singular = class_name
        plural = table_name if table_name else p.plural(singular)
        
        return {
            'singular': singular,
            'plural': plural,
            'model_class': model_class,
            'table_name': table_name,
            'display_name': class_name.title()
        }
    
    @classmethod  
    def _build_config(cls, entity_type: str) -> EntityConfig:
        """Build complete config from model data + presentation overrides"""
        # Get base data from model
        model_data = cls._extract_from_model(entity_type)
        
        # Get presentation overrides
        overrides = cls._presentation_overrides.get(entity_type, {})
        
        # Use model __entity_config__ as primary source, then overrides, then model data
        model_class = model_data.get('model_class')
        if model_class and hasattr(model_class, '__entity_config__'):
            entity_config = model_class.__entity_config__
            singular = entity_config.get('display_name_singular', entity_type)
            plural = entity_config.get('display_name', f"{entity_type}s")
            display_name = entity_config.get('display_name', singular.title())
        else:
            # Fallback to extracted data
            singular = model_data.get('singular', entity_type)
            plural = model_data.get('plural', f"{entity_type}s")
            display_name = model_data.get('display_name', singular.title())
        
        icon = overrides.get('icon', 'document')
        
        # Generate empty state dynamically from model configuration
        empty_state = EmptyStateConfig(
            title=f'No {plural.lower()} found',
            subtitle=f'Try adjusting your filters or create a new {singular.lower()}.'
        )
        
        return EntityConfig(
            icon=icon,
            singular=singular,
            plural=plural,
            display_name=display_name,
            empty_state=empty_state,
            model_class=model_data.get('model_class'),
            table_name=model_data.get('table_name')
        )
    
    @classmethod
    def get_config(cls, entity_type: str) -> EntityConfig:
        """Get configuration for an entity type - built dynamically from models"""
        return cls._build_config(entity_type)
    
    @classmethod
    def get_icon(cls, entity_type: str) -> str:
        """Get icon name for entity type"""
        return cls.get_config(entity_type).icon
    
    @classmethod
    def get_labels(cls, entity_type: str) -> Dict[str, str]:
        """Get singular/plural labels for entity type"""
        config = cls.get_config(entity_type)
        return {
            'singular': config.singular,
            'plural': config.plural,
            'display_name': config.display_name or config.singular.title()
        }
    
    @classmethod
    def get_empty_state(cls, entity_type: str) -> Dict[str, str]:
        """Get empty state configuration for entity type"""
        config = cls.get_config(entity_type)
        return {
            'title': config.empty_state.title,
            'subtitle': config.empty_state.subtitle
        }
    
    @classmethod
    def get_all_types(cls) -> list[str]:
        """Get list of all configured entity types"""
        cls._register_models()
        return list(cls._model_registry.keys())
    
    @classmethod
    def register_entity(cls, entity_type: str, model_class: Type, overrides: Dict = None) -> None:
        """Register a new entity (for plugins/extensions) - DRY approach"""
        cls._model_registry[entity_type] = model_class
        if overrides:
            cls._presentation_overrides[entity_type] = overrides


# Convenience functions for common use cases
def get_entity_config(entity_type: str) -> EntityConfig:
    """Get complete entity configuration"""
    return EntityConfigRegistry.get_config(entity_type)


def get_entity_icon(entity_type: str) -> str:
    """Get icon name for entity"""
    return EntityConfigRegistry.get_icon(entity_type)


def get_entity_labels(entity_type: str) -> Dict[str, str]:
    """Get labels for entity"""
    return EntityConfigRegistry.get_labels(entity_type)


def get_empty_state_config(entity_type: str) -> Dict[str, str]:
    """Get empty state config for entity"""
    return EntityConfigRegistry.get_empty_state(entity_type)


@dataclass
class DashboardConfig:
    """Configuration for dashboard-specific content to prevent pollution"""
    show_entity_metrics: bool = False  # Only for entity index pages
    show_pipeline: bool = True
    show_recent_activity: bool = True
    show_alerts: bool = True
    show_task_quick_stats: bool = False  # Only for task-specific pages


class DashboardConfigRegistry:
    """Registry for dashboard content configuration"""
    
    @classmethod
    def get_dashboard_config(cls) -> DashboardConfig:
        """Get standard dashboard configuration"""
        return DashboardConfig()
    
    @classmethod
    def should_show_entity_metrics(cls) -> bool:
        """Check if entity metrics should be displayed (False for dashboard)"""
        return cls.get_dashboard_config().show_entity_metrics
    
    @classmethod
    def should_show_pipeline(cls) -> bool:
        """Check if pipeline should be displayed"""
        return cls.get_dashboard_config().show_pipeline
    
    @classmethod
    def should_show_recent_activity(cls) -> bool:
        """Check if recent activity should be displayed"""
        return cls.get_dashboard_config().show_recent_activity
    
    @classmethod
    def should_show_alerts(cls) -> bool:
        """Check if alerts should be displayed"""
        return cls.get_dashboard_config().show_alerts


# Convenience functions for dashboard configuration
def get_dashboard_config() -> DashboardConfig:
    """Get dashboard configuration"""
    return DashboardConfigRegistry.get_dashboard_config()


def should_show_entity_metrics_on_dashboard() -> bool:
    """Check if entity metrics should be shown on dashboard (always False)"""
    return DashboardConfigRegistry.should_show_entity_metrics()