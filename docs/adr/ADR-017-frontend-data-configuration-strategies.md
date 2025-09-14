# Architecture Decision Record (ADR)

## ADR-017: Universal Frontend Data Passing and Configuration Object Strategies

**Status:** Superseded
**Date:** 13-09-25-14h-30m-00s
**Updated:** 14-09-25-12h-10m-00s
**Session:** 57ad43d3-ad12-46e8-8f3e-abd7c0ebc32c.jsonl
**Todo:** Frontend data passing and configuration patterns
**Deciders:** Will Robinson, Development Team
**Superseded by:** Direct parameter passing with model metadata (14-09-25)

**Current Implementation**: Frontend data configuration uses:
- `__entity_config__` patterns in models for metadata
- `ModelRegistry` for dynamic model access
- Direct template context passing from route handlers
- Tailwind CSS for styling with minimal Alpine.js components

### Context

Web applications consistently face decisions about how to pass data from backend to frontend, particularly regarding whether to send individual variables or consolidated configuration objects. Current challenges across projects include:

- **Data Passing Inconsistency**: Some routes pass individual variables while others pass configuration objects
- **Template Context Bloat**: Templates receiving dozens of separate variables making context management difficult
- **Frontend-Backend Coupling**: Hard-coded assumptions about data structure on both sides
- **Configuration Flexibility**: Need to extend data structures without breaking frontend code
- **Maintenance Burden**: Changes to data structure require updates across multiple template calls
- **JavaScript Integration**: Difficulty passing complex data structures to frontend JavaScript

Analysis of current approaches reveals mixed patterns with no standardized strategy for when to use configuration objects versus individual variables.

### Decision

**We will establish universal frontend data passing strategies that prioritize configuration objects for flexibility while maintaining simplicity for basic cases:**

1. **Configuration Object Strategy**: Use structured configuration objects for complex, extensible data
2. **Individual Variables for Simple Data**: Keep individual variables for basic, stable data types  
3. **Nested Configuration Patterns**: Structured configuration objects with logical grouping
4. **Context Processor Standardization**: Consistent global context injection patterns
5. **Frontend Data Contracts**: Explicit contracts between backend data and frontend expectations
6. **Dynamic Configuration Generation**: Configuration objects generated from model metadata

**Universal Data Passing Architecture:**
```
Backend Data → Configuration Objects → Template Context → Frontend JavaScript
     ↓               ↓                    ↓                    ↓
Model/Form       Context Builders    Jinja Variables       JS Config
```

### Rationale

**Primary drivers:**

- **Flexibility**: Configuration objects can be extended without changing template calls
- **Maintainability**: Single configuration object easier to manage than multiple variables
- **Frontend Integration**: JavaScript can consume structured configuration objects directly
- **Consistency**: Standardized patterns reduce cognitive load and development errors
- **Scalability**: Configuration objects support complex features without template proliferation
- **Type Safety**: Structured objects enable better validation and type checking

**Technical benefits:**

- Configuration objects consolidate related data into logical structures
- Frontend JavaScript can destructure and validate configuration objects
- Template context remains clean with fewer top-level variables
- Changes to configuration structure are centralized and controlled
- Dynamic configuration generation from metadata eliminates duplication

### Alternatives Considered

- **Option A: Individual variables only** - Rejected due to template context bloat and inflexibility
- **Option B: Everything in single config object** - Rejected due to loss of simple variable access patterns
- **Option C: Framework-specific solutions** - Rejected due to lack of portability across projects
- **Option D: No standardization** - Rejected due to continued inconsistency and maintenance burden

### Consequences

**Positive:**

- ✅ **Enhanced Flexibility**: Configuration objects can be extended without breaking frontend code
- ✅ **Improved Maintainability**: Centralized data structures reduce maintenance burden  
- ✅ **Better JavaScript Integration**: Structured data easily consumed by frontend frameworks
- ✅ **Consistent Patterns**: Standardized approach reduces development errors and confusion
- ✅ **Dynamic Generation**: Configuration objects can be generated automatically from metadata
- ✅ **Cleaner Templates**: Fewer top-level variables improve template readability

**Negative:**

- ➖ **Learning Curve**: Developers must understand when to use configuration objects vs individual variables
- ➖ **Initial Overhead**: Creating configuration objects requires more upfront planning
- ➖ **Over-structuring Risk**: May create unnecessary complexity for simple data passing
- ➖ **Debugging Complexity**: Nested configuration objects may complicate debugging

**Neutral:**

- 🔄 **Migration Effort**: Existing templates may need updates to use configuration objects
- 🔄 **Documentation Requirements**: Clear documentation needed for configuration object structures
- 🔄 **Team Training**: All developers must understand configuration object patterns

### Implementation Notes

**1. Configuration Object Strategy Decision Matrix:**

```python
# app/utils/frontend_data_patterns.py
"""
Decision matrix for choosing configuration objects vs individual variables:

USE CONFIGURATION OBJECTS when:
- Data has more than 5 related properties
- Structure likely to change or extend over time  
- Data consumed by JavaScript frontend frameworks
- Logical grouping makes semantic sense
- Dynamic generation from metadata is beneficial

USE INDIVIDUAL VARIABLES when:
- Simple, stable data (strings, numbers, booleans)
- Data unlikely to change structure
- Direct template usage without JavaScript processing
- Clear semantic meaning as standalone values
"""

class DataPassingStrategy:
    """Utility for determining appropriate data passing approach"""
    
    @staticmethod
    def should_use_config_object(data_properties: list, 
                                context: dict = None) -> bool:
        """
        Determine if data should be passed as configuration object
        
        Args:
            data_properties: List of property names in the data
            context: Additional context about usage patterns
            
        Returns:
            bool: True if should use configuration object
        """
        # Use config object if more than 5 properties
        if len(data_properties) > 5:
            return True
            
        # Use config object if context indicates JavaScript consumption
        if context and context.get('javascript_usage', False):
            return True
            
        # Use config object if properties have logical grouping
        grouped_properties = DataPassingStrategy._detect_property_groups(data_properties)
        if len(grouped_properties) > 1:
            return True
            
        return False
    
    @staticmethod
    def _detect_property_groups(properties: list) -> dict:
        """Detect logical groupings in property names"""
        groups = {}
        for prop in properties:
            if '_' in prop:
                prefix = prop.split('_')[0]
                if prefix not in groups:
                    groups[prefix] = []
                groups[prefix].append(prop)
            else:
                if 'general' not in groups:
                    groups['general'] = []
                groups['general'].append(prop)
        return groups
```

**2. Universal Configuration Object Patterns:**

```python
# app/utils/context_builders.py
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from flask import request

@dataclass
class EntityConfig:
    """Standard entity configuration object"""
    entity_name: str
    entity_name_singular: str
    entity_description: str
    entity_type: str
    entity_endpoint: str
    entity_buttons: List[Dict[str, str]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template usage"""
        return asdict(self)
    
    def to_json_safe(self) -> Dict[str, Any]:
        """Convert to JSON-safe dictionary for JavaScript"""
        return self.to_dict()

@dataclass 
class UIConfig:
    """Standard UI configuration object"""
    show_filters: bool = True
    show_grouping: bool = True
    show_sorting: bool = True
    show_search: bool = True
    items_per_page: int = 20
    default_view: str = "card"  # card, table, list
    
    # Filter configurations
    available_filters: List[str] = None
    active_filters: Dict[str, Any] = None
    
    # Sorting configurations  
    available_sorts: List[str] = None
    active_sort: Dict[str, str] = None
    
    # Grouping configurations
    available_groups: List[str] = None
    active_group: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DropdownConfig:
    """Standard dropdown configuration object"""
    options: List[Dict[str, Any]]
    selected_values: List[str] = None
    placeholder: str = "Select..."
    multiple: bool = False
    searchable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class FormConfig:
    """Standard form configuration object"""
    fields: Dict[str, Dict[str, Any]]
    layout: Dict[str, Any]
    validation_rules: Dict[str, List[str]]
    submit_url: str
    method: str = "POST"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class UniversalContextBuilder:
    """Universal context builder using configuration objects"""
    
    @staticmethod
    def build_entity_index_context(entity_name: str, 
                                 entities_data: List[Dict],
                                 **kwargs) -> Dict[str, Any]:
        """
        Build standardized context for entity index pages
        
        Returns configuration objects for complex data,
        individual variables for simple data
        """
        # Get model-based entity configuration
        entity_config = UniversalContextBuilder._build_entity_config(entity_name)
        
        # Build UI configuration
        ui_config = UniversalContextBuilder._build_ui_config(entity_name, **kwargs)
        
        # Build dropdown configurations
        dropdown_configs = UniversalContextBuilder._build_dropdown_configs(entity_name)
        
        # Request parameters (simple data - use individual variables)
        request_params = UniversalContextBuilder._parse_request_params()
        
        return {
            # Configuration objects for complex, extensible data
            'entity_config': entity_config.to_dict(),
            'ui_config': ui_config.to_dict(),
            'dropdown_configs': {name: config.to_dict() 
                               for name, config in dropdown_configs.items()},
            
            # Individual variables for simple, stable data
            'current_page': request.args.get('page', 1, type=int),
            'total_items': len(entities_data),
            'has_items': len(entities_data) > 0,
            
            # Entity data (could be individual or config based on size)
            'entities': entities_data if len(entities_data) <= 20 else None,
            'entities_config': {
                'data': entities_data,
                'count': len(entities_data),
                'pagination': UniversalContextBuilder._build_pagination_config()
            } if len(entities_data) > 20 else None
        }
    
    @staticmethod
    def _build_entity_config(entity_name: str) -> EntityConfig:
        """Build entity configuration from model metadata"""
        from app.utils.model_registry import ModelRegistry
        
        metadata = ModelRegistry.get_model_metadata(entity_name)
        return EntityConfig(
            entity_name=metadata.display_name_plural,
            entity_name_singular=metadata.display_name,
            entity_description=metadata.description,
            entity_type=entity_name,
            entity_endpoint=metadata.api_endpoint,
            entity_buttons=UniversalContextBuilder._build_entity_buttons(metadata)
        )
    
    @staticmethod
    def _build_ui_config(entity_name: str, **kwargs) -> UIConfig:
        """Build UI configuration with defaults and overrides"""
        from app.utils.model_registry import ModelRegistry
        
        metadata = ModelRegistry.get_model_metadata(entity_name)
        
        return UIConfig(
            show_filters=kwargs.get('show_filters', True),
            show_grouping=kwargs.get('show_grouping', True),
            show_sorting=kwargs.get('show_sorting', True),
            show_search=kwargs.get('show_search', True),
            items_per_page=kwargs.get('items_per_page', metadata.list_per_page),
            default_view=kwargs.get('default_view', 'card'),
            available_filters=metadata.list_filters,
            available_sorts=[field for field, meta in metadata.fields.items() 
                           if meta.sortable],
            available_groups=[field for field, meta in metadata.fields.items() 
                            if meta.filterable and field != 'id']
        )
    
    @staticmethod
    def _parse_request_params() -> Dict[str, Any]:
        """Parse request parameters into simple variables"""
        return {
            'group_by': request.args.get("group_by", ""),
            'sort_by': request.args.get("sort_by", ""),  
            'sort_direction': request.args.get("sort_direction", "asc"),
            'search_query': request.args.get("q", ""),
            'page': request.args.get('page', 1, type=int)
        }
```

**3. Template Usage Patterns:**

```jinja2
<!-- templates/base/entity_index.html -->
<!-- Configuration objects for complex, extensible data -->
{% set entity = entity_config %}
{% set ui = ui_config %}
{% set dropdowns = dropdown_configs %}

<!-- Individual variables for simple, stable data -->
<div class="page-header">
    <h1>{{ entity.entity_name }}</h1>
    <p>{{ entity.entity_description }}</p>
    
    <!-- Simple variables -->
    <div class="page-stats">
        <span>Page {{ current_page }}</span>
        <span>{{ total_items }} total items</span>
        {% if has_items %}
            <span>Items loaded</span>
        {% endif %}
    </div>
</div>

<!-- Configuration object usage -->
<div class="page-controls">
    {% if ui.show_filters %}
        <div class="filters">
            {% for filter_name in ui.available_filters %}
                {{ macros.filter_dropdown(dropdowns[filter_name]) }}
            {% endfor %}
        </div>
    {% endif %}
    
    {% if ui.show_sorting %}
        <div class="sorting">
            {{ macros.sort_dropdown(dropdowns.sort_options) }}
        </div>
    {% endif %}
</div>

<!-- JavaScript configuration passing -->
<script>
    // Configuration objects easily consumed by JavaScript
    window.appConfig = {
        entity: {{ entity_config | tojson }},
        ui: {{ ui_config | tojson }},
        dropdowns: {{ dropdown_configs | tojson }},
        
        // Simple variables
        currentPage: {{ current_page }},
        totalItems: {{ total_items }},
        hasItems: {{ has_items | tojson }}
    };
    
    // Frontend framework can consume structured configuration
    new EntityManager(window.appConfig);
</script>
```

**4. Frontend Data Contracts:**

```python
# app/utils/frontend_contracts.py
from typing import Dict, List, Any, TypedDict
from dataclasses import dataclass

class EntityConfigContract(TypedDict):
    """Type contract for entity configuration objects"""
    entity_name: str
    entity_name_singular: str  
    entity_description: str
    entity_type: str
    entity_endpoint: str
    entity_buttons: List[Dict[str, str]]

class UIConfigContract(TypedDict):
    """Type contract for UI configuration objects"""
    show_filters: bool
    show_grouping: bool
    show_sorting: bool
    show_search: bool
    items_per_page: int
    default_view: str
    available_filters: List[str]
    active_filters: Dict[str, Any]
    available_sorts: List[str] 
    active_sort: Dict[str, str]
    available_groups: List[str]
    active_group: str

class FrontendContractValidator:
    """Validate configuration objects against frontend contracts"""
    
    @staticmethod
    def validate_entity_config(config: Dict[str, Any]) -> bool:
        """Validate entity configuration against contract"""
        required_fields = ['entity_name', 'entity_name_singular', 
                          'entity_type', 'entity_endpoint']
        return all(field in config for field in required_fields)
    
    @staticmethod
    def validate_ui_config(config: Dict[str, Any]) -> bool:
        """Validate UI configuration against contract"""
        required_fields = ['show_filters', 'show_grouping', 'items_per_page']
        return all(field in config for field in required_fields)
    
    @staticmethod
    def validate_context(context: Dict[str, Any]) -> List[str]:
        """Validate entire context against contracts"""
        errors = []
        
        if 'entity_config' in context:
            if not FrontendContractValidator.validate_entity_config(context['entity_config']):
                errors.append("Invalid entity_config structure")
                
        if 'ui_config' in context:
            if not FrontendContractValidator.validate_ui_config(context['ui_config']):
                errors.append("Invalid ui_config structure")
        
        return errors
```

**5. Dynamic Configuration Generation:**

```python
# app/utils/dynamic_config_generation.py
class DynamicConfigGenerator:
    """Generate configuration objects dynamically from metadata"""
    
    @staticmethod
    def generate_form_config(model_name: str, 
                           context: Dict[str, Any] = None) -> FormConfig:
        """Generate form configuration from model metadata"""
        from app.utils.model_registry import ModelRegistry
        
        metadata = ModelRegistry.get_model_metadata(model_name)
        
        # Generate field configurations
        fields = {}
        for field_name, field_meta in metadata.fields.items():
            if field_name in metadata.get_form_fields():
                fields[field_name] = {
                    'type': field_meta.field_type.value,
                    'label': field_meta.display_name,
                    'placeholder': field_meta.placeholder,
                    'required': field_meta.required,
                    'help_text': field_meta.help_text,
                    'widget': field_meta.widget,
                    'widget_attrs': field_meta.widget_attrs
                }
                
                # Add choices if applicable
                if field_meta.choices:
                    fields[field_name]['choices'] = field_meta.choices
                
                # Add validation rules
                validation_rules = []
                if field_meta.required:
                    validation_rules.append('required')
                if field_meta.max_length:
                    validation_rules.append(f'max_length:{field_meta.max_length}')
                    
                fields[field_name]['validation'] = validation_rules
        
        # Generate layout from metadata
        layout = metadata.form_layout or DynamicConfigGenerator._default_layout(fields)
        
        return FormConfig(
            fields=fields,
            layout=layout,
            validation_rules={name: field.get('validation', []) 
                            for name, field in fields.items()},
            submit_url=f'/api/{metadata.api_endpoint}',
            method='POST'
        )
    
    @staticmethod
    def generate_table_config(model_name: str) -> Dict[str, Any]:
        """Generate table configuration from model metadata"""
        from app.utils.model_registry import ModelRegistry
        
        metadata = ModelRegistry.get_model_metadata(model_name)
        
        columns = []
        for field_name in metadata.list_fields:
            field_meta = metadata.fields[field_name]
            columns.append({
                'key': field_name,
                'title': field_meta.display_name,
                'sortable': field_meta.sortable,
                'type': field_meta.field_type.value,
                'formatter': DynamicConfigGenerator._get_field_formatter(field_meta)
            })
        
        return {
            'columns': columns,
            'sortable': True,
            'filterable': True,
            'searchable': True,
            'pagination': {
                'enabled': True,
                'per_page': metadata.list_per_page
            },
            'actions': DynamicConfigGenerator._generate_table_actions(metadata)
        }
    
    @staticmethod
    def _get_field_formatter(field_meta) -> Optional[str]:
        """Get appropriate formatter for field type"""
        formatter_map = {
            'datetime': 'datetime',
            'date': 'date',
            'decimal': 'currency',
            'boolean': 'yes_no',
            'foreign_key': 'relation'
        }
        return formatter_map.get(field_meta.field_type.value)
```

**6. Context Processor Standardization:**

```python
# app/utils/context_processors.py
from flask import current_app, request, g

@current_app.context_processor
def inject_global_config():
    """Inject global configuration objects available to all templates"""
    return {
        'app_config': {
            'app_name': current_app.config['APP_NAME'],
            'version': current_app.config.get('VERSION', '1.0.0'),
            'environment': current_app.config.get('ENV', 'development'),
            'debug': current_app.debug
        },
        
        'user_config': {
            'authenticated': hasattr(g, 'current_user') and g.current_user.is_authenticated,
            'user_id': getattr(g, 'current_user', {}).get('id'),
            'permissions': getattr(g, 'user_permissions', []),
            'preferences': getattr(g, 'user_preferences', {})
        },
        
        'request_config': {
            'path': request.path,
            'method': request.method,
            'args': request.args.to_dict(),
            'is_htmx': request.headers.get('HX-Request') == 'true',
            'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        }
    }

@current_app.context_processor  
def inject_navigation_config():
    """Inject navigation configuration object"""
    if hasattr(g, 'current_user') and g.current_user.is_authenticated:
        navigation_items = [
            {'name': 'Dashboard', 'url': '/dashboard', 'icon': 'dashboard'},
            {'name': 'Companies', 'url': '/companies', 'icon': 'building'},
            {'name': 'Contacts', 'url': '/stakeholders', 'icon': 'people'},
            {'name': 'Opportunities', 'url': '/opportunities', 'icon': 'trending_up'},
            {'name': 'Tasks', 'url': '/tasks', 'icon': 'assignment'}
        ]
    else:
        navigation_items = []
    
    return {
        'navigation_config': {
            'items': navigation_items,
            'current_path': request.path,
            'mobile_friendly': True,
            'collapsible': True
        }
    }
```

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 13-09-25-14h-30m-00s | 57ad43d3-ad12-46e8-8f3e-abd7c0ebc32c.jsonl | Frontend data patterns | Initial creation | Document universal frontend data passing and configuration strategies | Establish consistent patterns for backend-frontend data contracts |

---

**Impact Assessment:** High - This establishes fundamental patterns for backend-frontend data communication affecting all web application development.

**Review Required:** Mandatory - All developers must understand when to use configuration objects versus individual variables.

## Supersession Notice

**This ADR has been superseded by a simpler approach implemented on 14-09-25.**

**New Approach:** Direct parameter passing using existing model metadata (`__entity_config__`) with minimal DRY helpers.

**Why Superseded:**
- The configuration object approach created unnecessary complexity
- Over-engineered systems (UniversalIndexHelper, context builders) caused validation errors
- Existing model metadata already provided all necessary information
- Direct parameter passing with model metadata proved simpler and more maintainable

**Replacement Implementation:**
```python
# Instead of complex configuration objects:
return render_template("base/entity_index.html",
    entity_config=Stakeholder.__entity_config__,  # Direct model metadata
    dropdown_configs=build_dropdown_configs(Stakeholder),
    entity_stats=calculate_entity_stats(Stakeholder)
)
```

**Result:** 500+ lines of code eliminated, zero validation errors, simpler maintenance.

**Reference:** PR #275 - "fix: eliminate validation errors and implement DRY route system"

---

**Original Next Steps (No longer applicable):**
1. ~~Implement configuration object patterns in all new routes and templates~~
2. ~~Create frontend JavaScript utilities for consuming configuration objects~~
3. ~~Establish validation tools for configuration object contracts~~
4. ~~Migrate existing templates to use standardized configuration patterns where beneficial~~
5. ~~Create project templates that implement these data passing patterns by default~~