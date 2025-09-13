# Architecture Decision Record (ADR)

## ADR-016: Universal Dynamic Model and Metadata Management Patterns

**Status:** Accepted  
**Date:** 13-09-25-14h-00m-00s  
**Session:** 57ad43d3-ad12-46e8-8f3e-abd7c0ebc32c.jsonl  
**Todo:** Dynamic model patterns and metadata management  
**Deciders:** Will Robinson, Development Team

### Context

Web applications consistently require dynamic model handling and comprehensive metadata management as they scale beyond simple CRUD operations. Common challenges across all projects include:

- **Dynamic Model Access**: Need to reference and instantiate models by string names for generic operations
- **Metadata Scattered**: Model metadata (validation rules, display names, field types) scattered across codebase
- **Inconsistent Introspection**: No standard patterns for accessing model field information dynamically
- **Form Generation Complexity**: Manual form creation despite predictable patterns from model structure
- **API Serialization Inconsistency**: Different serialization approaches across models and endpoints
- **Configuration Inflexibility**: Hard-coded model behavior instead of configurable metadata-driven patterns

These issues occur across all web frameworks and significantly impact development velocity, code maintainability, and system flexibility.

### Decision

**We will establish comprehensive universal patterns for dynamic model handling and metadata management applicable across all web application projects:**

1. **Model Registry System**: Centralized model discovery and dynamic instantiation by string names
2. **Comprehensive Metadata Framework**: Structured metadata storage covering validation, display, API, and form generation
3. **Model Introspection Utilities**: Standardized utilities for accessing model structure and metadata programmatically  
4. **Dynamic Form Generation**: Metadata-driven form creation eliminating manual form definitions
5. **Flexible Serialization Patterns**: Configurable serialization based on context (API, templates, exports)
6. **Metadata Inheritance System**: Hierarchical metadata with composition and override capabilities

**Universal Architecture Pattern:**
```
Model Registry → Metadata Framework → Introspection Utilities → Dynamic Generation
     ↓                ↓                      ↓                      ↓
Model Discovery   Field Metadata      Model Analysis      Forms/APIs/Views
```

### Rationale

**Primary drivers:**

- **Universal Applicability**: Patterns work across all web frameworks and ORM systems
- **Development Velocity**: Metadata-driven approach eliminates repetitive boilerplate code
- **Maintainability**: Centralized metadata reduces duplication and improves consistency
- **Flexibility**: Configuration-driven behavior enables rapid feature development
- **Scalability**: Systematic patterns support applications from MVP to enterprise scale
- **Team Efficiency**: Standardized metadata patterns reduce cognitive load and onboarding time

**Technical benefits:**

- Dynamic model access enables generic CRUD operations and utilities
- Comprehensive metadata enables automated form, API, and view generation
- Centralized metadata management reduces bugs and inconsistencies
- Model introspection utilities support advanced dynamic functionality
- Flexible serialization patterns adapt to different output contexts

### Alternatives Considered

- **Option A: Framework-specific model patterns** - Rejected due to lack of portability across projects
- **Option B: Manual model handling** - Rejected due to maintenance burden and code duplication
- **Option C: External schema definition** - Rejected due to model-code synchronization complexity
- **Option D: Minimal metadata approach** - Rejected due to limited flexibility and continued duplication

### Consequences

**Positive:**

- ✅ **Universal Model Patterns**: Consistent dynamic model handling across all projects
- ✅ **Automated Generation**: Metadata-driven forms, APIs, and views reduce manual development
- ✅ **Enhanced Flexibility**: Configuration-driven behavior enables rapid feature iteration
- ✅ **Improved Consistency**: Centralized metadata eliminates scattered validation and display logic
- ✅ **Reduced Boilerplate**: Dynamic patterns eliminate repetitive model-related code
- ✅ **Better Maintainability**: Single source of truth for model behavior and structure

**Negative:**

- ➖ **Learning Curve**: Developers must understand metadata framework and dynamic patterns
- ➖ **Abstraction Complexity**: Deep metadata systems may complicate debugging
- ➖ **Performance Overhead**: Dynamic model access adds minimal runtime cost
- ➖ **Over-Engineering Risk**: May create unnecessary complexity for simple models

**Neutral:**

- 🔄 **Metadata Investment**: Upfront investment in metadata definition for long-term benefits
- 🔄 **Documentation Requirements**: Comprehensive documentation needed for metadata patterns
- 🔄 **Team Training**: All developers must understand dynamic model patterns

### Implementation Notes

**1. Universal Model Registry System:**

```python
# app/utils/model_registry.py
class ModelRegistry:
    """Universal model registry for dynamic model access"""
    _models = {}
    _metadata_cache = {}
    
    @classmethod
    def register_model(cls, model_class, name=None):
        """Register a model class for dynamic access"""
        model_name = name or model_class.__name__.lower()
        cls._models[model_name] = model_class
        
        # Cache metadata on registration
        cls._metadata_cache[model_name] = ModelMetadata(model_class)
        
        return model_class
    
    @classmethod  
    def get_model(cls, model_name):
        """Get model class by name"""
        if model_name not in cls._models:
            raise ValueError(f"Model '{model_name}' not registered")
        return cls._models[model_name]
    
    @classmethod
    def get_model_metadata(cls, model_name):
        """Get cached metadata for model"""
        if model_name not in cls._metadata_cache:
            model_class = cls.get_model(model_name)
            cls._metadata_cache[model_name] = ModelMetadata(model_class)
        return cls._metadata_cache[model_name]
    
    @classmethod
    def list_models(cls):
        """Get all registered model names"""
        return list(cls._models.keys())
    
    @classmethod
    def create_instance(cls, model_name, **kwargs):
        """Create model instance with validation"""
        model_class = cls.get_model(model_name)
        metadata = cls.get_model_metadata(model_name)
        
        # Apply field validation from metadata
        validated_data = metadata.validate_data(kwargs)
        return model_class(**validated_data)

# Usage with decorator for automatic registration
@ModelRegistry.register_model
class Product(BaseModel):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

# Or manual registration
ModelRegistry.register_model(User, 'user')
ModelRegistry.register_model(Order, 'order')
```

**2. Comprehensive Metadata Framework:**

```python
# app/utils/model_metadata.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

class FieldType(Enum):
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
    """Comprehensive field metadata"""
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
    """Comprehensive model metadata"""
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
        if self.display_name is None:
            self.display_name = self.model_class.__name__
        if self.display_name_plural is None:
            # Use proper pluralization instead of string manipulation
            try:
                from inflect import engine
                p = engine()
                self.display_name_plural = p.plural(self.display_name)
            except ImportError:
                # Fallback to simple pluralization if inflect not available
                if self.display_name.endswith('y'):
                    self.display_name_plural = self.display_name[:-1] + 'ies'
                elif self.display_name.endswith(('s', 'sh', 'ch', 'x', 'z')):
                    self.display_name_plural = self.display_name + 'es'
                else:
                    self.display_name_plural = self.display_name + 's'
        if self.api_endpoint is None:
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
        # This would be implemented per framework (Django, SQLAlchemy, etc.)
        for field in self._get_model_fields():
            field_metadata = self._create_field_metadata(field)
            self.fields[field.name] = field_metadata
    
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
```

**3. Model Introspection Utilities:**

```python
# app/utils/model_introspection.py
class ModelIntrospector:
    """Universal model introspection utilities"""
    
    @staticmethod
    def get_field_names(model_class) -> List[str]:
        """Get all field names for a model"""
        metadata = ModelRegistry.get_model_metadata(model_class.__name__.lower())
        return list(metadata.fields.keys())
    
    @staticmethod
    def get_field_type(model_class, field_name: str) -> FieldType:
        """Get the type of a specific field"""
        metadata = ModelRegistry.get_model_metadata(model_class.__name__.lower())
        return metadata.get_field_metadata(field_name).field_type
    
    @staticmethod
    def get_related_fields(model_class) -> Dict[str, str]:
        """Get all relationship fields and their related models"""
        metadata = ModelRegistry.get_model_metadata(model_class.__name__.lower())
        return {
            name: field_meta.related_model
            for name, field_meta in metadata.fields.items()
            if field_meta.field_type in [FieldType.FOREIGN_KEY, FieldType.MANY_TO_MANY]
        }
    
    @staticmethod
    def get_filterable_fields(model_class) -> List[str]:
        """Get fields that can be used for filtering"""
        metadata = ModelRegistry.get_model_metadata(model_class.__name__.lower())
        return [
            name for name, field_meta in metadata.fields.items()
            if field_meta.filterable
        ]
    
    @staticmethod
    def get_searchable_fields(model_class) -> List[str]:
        """Get fields that can be used for text search"""
        metadata = ModelRegistry.get_model_metadata(model_class.__name__.lower())
        return [
            name for name, field_meta in metadata.fields.items()
            if field_meta.searchable
        ]
    
    @staticmethod
    def has_field(model_class, field_name: str) -> bool:
        """Check if model has a specific field"""
        try:
            metadata = ModelRegistry.get_model_metadata(model_class.__name__.lower())
            return field_name in metadata.fields
        except ValueError:
            return False
    
    @staticmethod
    def get_field_choices(model_class, field_name: str) -> Optional[List[tuple]]:
        """Get choices for a field if it has any"""
        metadata = ModelRegistry.get_model_metadata(model_class.__name__.lower())
        field_meta = metadata.get_field_metadata(field_name)
        return field_meta.choices

# Usage examples
filterable_fields = ModelIntrospector.get_filterable_fields(Product)
related_models = ModelIntrospector.get_related_fields(Order)
has_email = ModelIntrospector.has_field(User, 'email')
```

**4. Dynamic Form Generation:**

```python
# app/utils/dynamic_forms.py
class DynamicFormGenerator:
    """Universal dynamic form generation from model metadata"""
    
    @staticmethod
    def generate_form_class(model_name: str, base_form_class=None, exclude_fields=None):
        """Generate form class from model metadata"""
        metadata = ModelRegistry.get_model_metadata(model_name)
        exclude_fields = exclude_fields or []
        
        form_fields = {}
        form_fields_to_include = [
            f for f in metadata.get_form_fields() 
            if f not in exclude_fields
        ]
        
        for field_name in form_fields_to_include:
            field_meta = metadata.get_field_metadata(field_name)
            form_field = DynamicFormGenerator._create_form_field(field_meta)
            form_fields[field_name] = form_field
        
        # Create dynamic form class
        form_class_name = f"{metadata.display_name}Form"
        base_class = base_form_class or BaseForm
        
        dynamic_form_class = type(form_class_name, (base_class,), form_fields)
        return dynamic_form_class
    
    @staticmethod
    def _create_form_field(field_meta: FieldMetadata):
        """Create appropriate form field from metadata"""
        field_kwargs = {
            'label': field_meta.display_name,
            'help_text': field_meta.help_text,
            'required': field_meta.required,
        }
        
        if field_meta.widget_attrs:
            field_kwargs['widget_attrs'] = field_meta.widget_attrs
            
        # Map field types to form field classes
        field_type_mapping = {
            FieldType.STRING: 'CharField',
            FieldType.TEXT: 'TextField', 
            FieldType.EMAIL: 'EmailField',
            FieldType.URL: 'URLField',
            FieldType.INTEGER: 'IntegerField',
            FieldType.DECIMAL: 'DecimalField',
            FieldType.BOOLEAN: 'BooleanField',
            FieldType.DATE: 'DateField',
            FieldType.DATETIME: 'DateTimeField',
            FieldType.FOREIGN_KEY: 'ModelChoiceField',
            FieldType.MANY_TO_MANY: 'ModelMultipleChoiceField',
        }
        
        field_class_name = field_type_mapping.get(field_meta.field_type, 'CharField')
        
        # Handle special cases
        if field_meta.choices:
            field_class_name = 'ChoiceField'
            field_kwargs['choices'] = field_meta.choices
            
        if field_meta.max_length:
            field_kwargs['max_length'] = field_meta.max_length
            
        # Return appropriate form field instance
        return FormFieldFactory.create_field(field_class_name, **field_kwargs)
    
    @staticmethod
    def generate_form_layout(model_name: str) -> Dict[str, Any]:
        """Generate form layout configuration from metadata"""
        metadata = ModelRegistry.get_model_metadata(model_name)
        
        if metadata.form_layout:
            return metadata.form_layout
            
        # Generate default layout
        form_fields = metadata.get_form_fields()
        return {
            'layout': 'vertical',
            'sections': [
                {
                    'title': 'Basic Information',
                    'fields': form_fields[:5]  # First 5 fields
                },
                {
                    'title': 'Additional Details',
                    'fields': form_fields[5:]  # Remaining fields
                }
            ] if len(form_fields) > 5 else [
                {
                    'title': metadata.display_name + ' Information',
                    'fields': form_fields
                }
            ]
        }

# Usage
ProductForm = DynamicFormGenerator.generate_form_class('product')
UserForm = DynamicFormGenerator.generate_form_class('user', exclude_fields=['password_hash'])
form_layout = DynamicFormGenerator.generate_form_layout('product')
```

**5. Flexible Serialization Patterns:**

```python
# app/utils/dynamic_serialization.py
class DynamicSerializer:
    """Context-aware dynamic serialization based on metadata"""
    
    @staticmethod
    def serialize_model(instance, context='api', include_relationships=False):
        """Serialize model instance based on context and metadata"""
        model_name = instance.__class__.__name__.lower()
        metadata = ModelRegistry.get_model_metadata(model_name)
        
        # Get fields appropriate for context
        if context == 'api':
            fields = metadata.get_serializable_fields('api')
        elif context == 'template':
            fields = [name for name, meta in metadata.fields.items() 
                     if not meta.write_only]
        elif context == 'export':
            fields = list(metadata.fields.keys())  # All fields
        else:
            fields = metadata.get_serializable_fields()
        
        result = {}
        for field_name in fields:
            if hasattr(instance, field_name):
                field_meta = metadata.get_field_metadata(field_name)
                value = getattr(instance, field_name)
                
                # Apply field-specific serialization
                serialized_value = DynamicSerializer._serialize_field_value(
                    value, field_meta, context
                )
                
                # Use API name if specified
                output_name = field_meta.api_name if context == 'api' else field_name
                result[output_name] = serialized_value
        
        # Handle relationships if requested
        if include_relationships:
            related_fields = ModelIntrospector.get_related_fields(instance.__class__)
            for field_name, related_model in related_fields.items():
                if hasattr(instance, field_name):
                    related_obj = getattr(instance, field_name)
                    if related_obj:
                        if hasattr(related_obj, '__iter__'):  # Many-to-many
                            result[field_name] = [
                                DynamicSerializer.serialize_model(obj, context, False)
                                for obj in related_obj.all()
                            ]
                        else:  # Foreign key
                            result[field_name] = DynamicSerializer.serialize_model(
                                related_obj, context, False
                            )
        
        return result
    
    @staticmethod
    def _serialize_field_value(value, field_meta: FieldMetadata, context: str):
        """Apply field-specific serialization logic"""
        if value is None:
            return None
            
        # Handle different field types
        if field_meta.field_type == FieldType.DATETIME:
            return value.isoformat() if hasattr(value, 'isoformat') else str(value)
        elif field_meta.field_type == FieldType.DATE:
            return value.isoformat() if hasattr(value, 'isoformat') else str(value)
        elif field_meta.field_type == FieldType.DECIMAL:
            return float(value) if context == 'api' else str(value)
        elif field_meta.field_type == FieldType.JSON:
            return value if isinstance(value, (dict, list)) else str(value)
        else:
            return value
    
    @staticmethod
    def serialize_queryset(queryset, context='api', include_relationships=False):
        """Serialize a queryset of model instances"""
        return [
            DynamicSerializer.serialize_model(instance, context, include_relationships)
            for instance in queryset
        ]

# Usage
api_data = DynamicSerializer.serialize_model(product, 'api', True)
template_data = DynamicSerializer.serialize_model(product, 'template')
export_data = DynamicSerializer.serialize_queryset(Product.objects.all(), 'export')
```

**6. Metadata Inheritance and Configuration:**

```python
# app/utils/metadata_inheritance.py
class MetadataInheritance:
    """Handle metadata inheritance and composition"""
    
    @staticmethod
    def inherit_metadata(base_metadata: ModelMetadata, 
                        child_metadata: ModelMetadata) -> ModelMetadata:
        """Merge child metadata with base metadata, child takes precedence"""
        # Deep copy base metadata
        inherited = copy.deepcopy(base_metadata)
        
        # Override with child metadata values
        for attr_name in ['display_name', 'display_name_plural', 'description', 
                         'api_endpoint', 'allowed_methods']:
            child_value = getattr(child_metadata, attr_name)
            if child_value is not None:
                setattr(inherited, attr_name, child_value)
        
        # Merge field metadata
        for field_name, child_field_meta in child_metadata.fields.items():
            if field_name in inherited.fields:
                # Merge field metadata
                base_field_meta = inherited.fields[field_name]
                merged_field_meta = MetadataInheritance._merge_field_metadata(
                    base_field_meta, child_field_meta
                )
                inherited.fields[field_name] = merged_field_meta
            else:
                # Add new field
                inherited.fields[field_name] = child_field_meta
        
        return inherited
    
    @staticmethod
    def _merge_field_metadata(base: FieldMetadata, child: FieldMetadata) -> FieldMetadata:
        """Merge field metadata with child taking precedence"""
        merged = copy.deepcopy(base)
        
        # Override with child values where they differ from defaults
        for field_name, field_value in child.__dict__.items():
            if field_value != getattr(FieldMetadata(), field_name, None):
                setattr(merged, field_name, field_value)
        
        return merged

# Example usage with model inheritance
class BaseProductMetadata(ModelMetadata):
    def __init__(self):
        super().__init__(Product)
        self.fields['name'].display_name = 'Product Name'
        self.fields['description'].widget = 'textarea'

class DigitalProductMetadata(BaseProductMetadata):
    def __init__(self):
        super().__init__(DigitalProduct)
        self.fields['download_url'] = FieldMetadata(
            name='download_url',
            field_type=FieldType.URL,
            display_name='Download URL',
            required=True
        )

# Register with inheritance
base_meta = BaseProductMetadata()
digital_meta = DigitalProductMetadata()
inherited_meta = MetadataInheritance.inherit_metadata(base_meta, digital_meta)
```

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 13-09-25-14h-00m-00s | 57ad43d3-ad12-46e8-8f3e-abd7c0ebc32c.jsonl | Dynamic model patterns | Initial creation | Document universal dynamic model and metadata patterns | Establish comprehensive metadata-driven development standards |

---

**Impact Assessment:** High - This establishes foundational patterns for dynamic model handling that affect all data-driven application development.

**Review Required:** Mandatory - All developers must understand and implement these metadata patterns in their models and applications.

**Next Steps:**
1. Implement model registry system in all new projects
2. Create framework-specific metadata discovery utilities (Django, SQLAlchemy, etc.)
3. Build dynamic form and API generation tools using these patterns
4. Establish metadata documentation standards and validation tools
5. Create project templates that implement these metadata patterns by default