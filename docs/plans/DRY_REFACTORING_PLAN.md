# DRY Utils Refactoring: Self-Describing Models Plan

## Objective
Transform utils directory from static, duplicated configuration to completely self-describing models that define all their UI/API behavior through SQLAlchemy column metadata.

## Core Principle
**Models are the single source of truth for ALL configuration**
- Field choices, CSS classes, grouping options, sorting behavior, icons, descriptions
- No duplication in forms, JavaScript, templates, or seed data
- Everything pulls from `column.info` metadata

## Implementation Strategy

### Phase 1: Model Self-Description System

#### 1.1 Enhanced Column Metadata Format
```python
stage = db.Column(
    db.String(50), 
    default="prospect",
    info={
        'choices': {
            'prospect': {
                'label': 'Prospect',
                'css_class': 'status-prospect',
                'groupable': True,
                'sortable': True,
                'description': 'Initial contact made',
                'icon': 'user-plus',
                'order': 1
            },
            'qualified': {
                'label': 'Qualified',
                'css_class': 'status-qualified', 
                'groupable': True,
                'sortable': True,
                'description': 'Meets our criteria',
                'icon': 'check-circle',
                'order': 2
            }
            # ... etc
        }
    }
)
```

#### 1.2 Universal Model Introspection System
```python
# New file: app/utils/model_introspection.py
class ModelIntrospector:
    @staticmethod
    def get_field_choices(model_class, field_name):
        """Get choices from column info metadata"""
        
    @staticmethod
    def get_field_css_class(model_class, field_name, value):
        """Get CSS class for a field value"""
        
    @staticmethod 
    def get_groupable_fields(model_class):
        """Get all fields that can be grouped by"""
        
    @staticmethod
    def get_sortable_fields(model_class):
        """Get all fields that can be sorted by"""
```

### Phase 2: Model Updates

#### 2.1 Opportunity Model
- Add complete `stage` choices with CSS classes and metadata
- Add `priority` calculation metadata (value ranges → priority levels)
- Define groupable/sortable field behavior

#### 2.2 Task Model  
- Add `priority` choices (high/medium/low) with CSS classes
- Add `status` choices (todo/in-progress/complete) with CSS classes
- Add `task_type` choices with metadata
- Define grouping and sorting behavior

#### 2.3 Company Model
- Add `industry` choices with CSS classes and icons
- Define size calculation metadata
- Add grouping options

#### 2.4 Stakeholder Model
- Add role-based choices and metadata
- Define contact info quality groupings

### Phase 3: Dynamic Infrastructure

#### 3.1 Enhanced Form System
```python
# Update app/utils/form_configs.py
class DynamicFormBuilder:
    @staticmethod
    def build_select_field(model_class, field_name):
        """Build SelectField from model metadata"""
        choices = ModelIntrospector.get_field_choices(model_class, field_name)
        return SelectField(choices=choices)
```

#### 3.2 API Configuration Endpoints
```python
# Update app/routes/api.py
@api_bp.route('/config/<model_name>')
def get_model_config(model_name):
    """Serve complete model configuration"""
    
@api_bp.route('/config/<model_name>/<field_name>')  
def get_field_config(model_name, field_name):
    """Serve specific field configuration"""
```

#### 3.3 Template Filters and Globals
```python
# Update app/utils/template_filters.py
@app.template_filter('css_class')
def css_class_filter(value, model_class, field_name):
    """Convert model value to CSS class"""
    return ModelIntrospector.get_field_css_class(model_class, field_name, value)
```

### Phase 4: Clean Up Static Data

#### 4.1 Seed Data Refactoring
```python
# Update seed_data.py
def create_opportunities():
    stage_choices = list(ModelIntrospector.get_field_choices(Opportunity, 'stage').keys())
    for i in range(10):
        opp = Opportunity(
            stage=random.choice(stage_choices),  # From model metadata!
            value=random.randint(10000, 300000)
        )
```

#### 4.2 Form Updates
- Remove all hardcoded choices from `entity_forms.py`
- Use dynamic form builder
- Pull choices from model metadata

#### 4.3 JavaScript Configuration
- Replace static `entity-configs.js` with API-driven configuration
- Fetch grouping, sorting, CSS classes from model config endpoints
- Generate UI options dynamically

### Phase 5: Template and Route Updates

#### 5.1 Template Enhancements
- Use new template filters for CSS classes
- Pull dropdown options from model APIs
- Remove hardcoded choice lists

#### 5.2 Route Simplification
- Remove hardcoded stage/priority logic from routes
- Use model introspection for filtering and grouping
- Simplify dashboard aggregation using model metadata

## Files to Modify

### New Files
- `app/utils/model_introspection.py` - Core introspection system
- `app/utils/dynamic_form_builder.py` - Dynamic form generation

### Enhanced Files
- `app/models/opportunity.py` - Add complete field metadata
- `app/models/task.py` - Add complete field metadata  
- `app/models/company.py` - Add complete field metadata
- `app/models/stakeholder.py` - Add complete field metadata
- `app/utils/form_configs.py` - Use model introspection
- `app/routes/api.py` - Add model config endpoints
- `app/utils/template_filters.py` - Add CSS class filters

### Cleaned Up Files
- `seed_data.py` - Remove static lists, use model metadata
- `app/forms/entity_forms.py` - Remove hardcoded choices
- `app/static/js/core/entity-configs.js` - Make API-driven
- All templates - Use dynamic filters and APIs

## Eliminated Files/Code
- Static `INDUSTRIES`, `ROLES`, `STAGES` lists
- Hardcoded JavaScript configuration objects
- Duplicate choice definitions across files
- Static CSS class mappings

## Benefits Achieved
✅ **Zero Duplication**: Models define everything once
✅ **Self-Documenting**: All behavior visible in model definition  
✅ **Dynamic UI**: Frontend automatically adapts to model changes
✅ **Maintainable**: Change model metadata → entire system updates
✅ **Type Safe**: Configuration lives with data definition
✅ **Discoverable**: Everything in `column.info` is introspectable

## Success Criteria
- [ ] All forms use model-driven choices
- [ ] All JavaScript configs pull from API endpoints
- [ ] All templates use dynamic CSS class filters  
- [ ] Seed data uses model metadata for choices
- [ ] Zero static choice lists remain in utils
- [ ] System learns from actual data usage patterns