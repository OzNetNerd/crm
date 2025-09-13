# Architecture Decision Record (ADR)

## ADR-014: Universal Jinja Template DRY Patterns and Best Practices

**Status:** Accepted  
**Date:** 13-09-25-13h-15m-00s  
**Session:** 57ad43d3-ad12-46e8-8f3e-abd7c0ebc32c  
**Todo:** Universal ADR coverage implementation  
**Deciders:** Will Robinson, Development Team

### Context

Web applications using Jinja2 templating frequently suffer from template duplication and poor maintainability due to inconsistent DRY (Don't Repeat Yourself) implementation. Common issues across projects include:

- **Template Duplication**: Repeated HTML structures across multiple templates
- **Macro Proliferation**: Dozens of similar macros with overlapping functionality  
- **Poor Template Inheritance**: Shallow inheritance hierarchies missing abstraction opportunities
- **Inconsistent Include Patterns**: Mixed use of `{% include %}` and `{% import %}` without clear guidelines
- **Context Repetition**: Same data structures passed repeatedly to templates
- **Maintenance Burden**: Changes require updates across multiple similar templates

This pattern occurs across all web frameworks using Jinja2 (Flask, Django with Jinja2, FastAPI, etc.) and significantly impacts development velocity and code quality.

### Decision

**We will establish comprehensive DRY patterns for Jinja2 templates that apply universally across all web application projects:**

1. **Template Inheritance Hierarchy**: Multi-level base template structure for maximum code reuse
2. **Macro Organization System**: Logical grouping and systematic macro patterns  
3. **Include vs Import Strategy**: Clear guidelines for template composition
4. **Dynamic Template Generation**: Context-driven template rendering patterns
5. **Shared Component Library**: Reusable UI component macros across all projects
6. **Context Standardization**: Consistent data passing patterns to reduce template duplication

**Universal DRY Architecture:**
```
Base Template → Layout Templates → Page Templates → Macro Components
     ↓              ↓                ↓                 ↓
Common Structure  Layout Variants  Specific Pages  Reusable Components
```

### Rationale

**Primary drivers:**

- **Universal Applicability**: Patterns work across all web frameworks using Jinja2
- **Maintainability**: Single source of truth reduces bugs and inconsistencies across projects
- **Development Velocity**: New pages/features require minimal template code due to abstractions
- **Code Quality**: Systematic DRY implementation prevents template debt accumulation
- **Team Efficiency**: Standardized patterns reduce onboarding time and increase productivity
- **Consistency**: Uniform template behavior and appearance across entire application

**Technical benefits:**

- Template inheritance eliminates HTML duplication across all page types
- Macro systems provide consistent UI components throughout applications  
- Dynamic template generation reduces manual template creation
- Standardized context patterns enable predictable data flow
- Component libraries enable cross-project template sharing

### Alternatives Considered

- **Option A: Framework-specific template patterns** - Rejected due to lack of universal applicability
- **Option B: Minimal template structure** - Rejected due to continued duplication issues
- **Option C: Component-based frameworks (React/Vue)** - Rejected due to server-side rendering requirements
- **Option D: Template generation tools** - Rejected due to maintenance complexity and learning overhead

### Consequences

**Positive:**

- ✅ **Universal Template Patterns**: Consistent DRY implementation across all projects
- ✅ **Reduced Template Code**: 60-80% reduction in template duplication through inheritance and macros
- ✅ **Improved Maintainability**: Changes cascade through inheritance hierarchy automatically
- ✅ **Development Efficiency**: New pages require minimal template code due to base structures
- ✅ **Enhanced Consistency**: Uniform UI patterns and behavior across entire application
- ✅ **Cross-Project Reusability**: Template patterns and components work across all projects

**Negative:**

- ➖ **Learning Curve**: Developers must understand inheritance hierarchies and macro patterns  
- ➖ **Abstraction Complexity**: Deep inheritance may complicate debugging for complex templates
- ➖ **Over-Engineering Risk**: May create unnecessary abstraction layers for simple projects
- ➖ **Template Performance**: Deep inheritance adds minimal rendering overhead

**Neutral:**

- 🔄 **Documentation Requirements**: Comprehensive documentation needed for template patterns
- 🔄 **Team Training**: All developers must understand and follow established DRY patterns
- 🔄 **Pattern Discipline**: Ongoing vigilance required to maintain DRY principles in new development

### Implementation Notes

**1. Template Inheritance Hierarchy:**

```jinja2
<!-- templates/base/core.html - Universal base template -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ config.APP_NAME }}{% endblock %}</title>
    {% block meta %}{% endblock %}
    {% block styles %}
        <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    {% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    {% block header %}
        {% include 'components/navigation.html' %}
    {% endblock %}
    
    <main class="main-content">
        {% block main %}
            <div class="container">
                {% block content %}{% endblock %}
            </div>
        {% endblock %}
    </main>
    
    {% block footer %}
        {% include 'components/footer.html' %}
    {% endblock %}
    
    {% block scripts %}
        <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% endblock %}
</body>
</html>

<!-- templates/layouts/dashboard.html - Layout-specific template -->
{% extends "base/core.html" %}

{% block body_class %}dashboard-layout{% endblock %}

{% block main %}
    <div class="dashboard-container">
        <aside class="sidebar">
            {% block sidebar %}
                {% include 'components/dashboard-navigation.html' %}
            {% endblock %}
        </aside>
        <main class="dashboard-main">
            {% block dashboard_content %}{% endblock %}
        </main>
    </div>
{% endblock %}

<!-- templates/pages/entity-list.html - Page-specific template -->
{% extends "layouts/dashboard.html" %}

{% block title %}{{ entity_type|title }} List - {{ super() }}{% endblock %}

{% block dashboard_content %}
    <div class="entity-list-page">
        {% block entity_header %}
            {{ macros.page_header(entity_type|title, actions=entity_actions) }}
        {% endblock %}
        
        {% block entity_filters %}
            {{ macros.filter_bar(available_filters, active_filters) }}
        {% endblock %}
        
        {% block entity_table %}
            {{ macros.data_table(items, columns, table_config) }}
        {% endblock %}
        
        {% block entity_pagination %}
            {{ macros.pagination(pagination) }}
        {% endblock %}
    </div>
{% endblock %}
```

**2. Macro Organization System:**

```
templates/macros/
├── base/                   # Core foundational macros
│   ├── forms.html         # Form input macros (text, select, checkbox)
│   ├── buttons.html       # Button variations (primary, secondary, danger)
│   ├── layout.html        # Layout helpers (grid, flexbox, containers)
│   └── typography.html    # Text formatting macros
├── components/            # UI component macros
│   ├── navigation.html    # Menu, breadcrumb, pagination macros
│   ├── data-display.html  # Table, list, card display macros
│   ├── feedback.html      # Alert, notification, progress macros
│   └── modals.html        # Modal, dialog, popup macros
├── entities/              # Domain-specific macros (adaptable per project)
│   ├── list-views.html    # Generic list display patterns
│   ├── detail-views.html  # Generic detail display patterns
│   └── form-views.html    # Generic form patterns
└── utilities/             # Helper and utility macros
    ├── formatters.html    # Date, currency, text formatting
    ├── conditionals.html  # Common conditional display patterns
    └── loops.html         # Iteration and grouping patterns
```

**3. Universal Macro Patterns:**

```jinja2
<!-- templates/macros/base/forms.html -->
{% macro text_input(name, label=None, value="", placeholder="", required=False, 
                   error=None, help_text=None, input_class="", wrapper_class="") %}
    <div class="form-group {{ wrapper_class }} {% if error %}has-error{% endif %}">
        {% if label %}
            <label for="{{ name }}" class="form-label {% if required %}required{% endif %}">
                {{ label }}
            </label>
        {% endif %}
        
        <input type="text" 
               id="{{ name }}" 
               name="{{ name }}" 
               value="{{ value }}"
               {% if placeholder %}placeholder="{{ placeholder }}"{% endif %}
               {% if required %}required{% endif %}
               class="form-control {{ input_class }}"
               aria-describedby="{% if error %}{{ name }}-error{% endif %} {% if help_text %}{{ name }}-help{% endif %}">
        
        {% if help_text %}
            <small id="{{ name }}-help" class="form-text">{{ help_text }}</small>
        {% endif %}
        
        {% if error %}
            <div id="{{ name }}-error" class="form-error">{{ error }}</div>
        {% endif %}
    </div>
{% endmacro %}

<!-- templates/macros/components/data-display.html -->
{% macro data_table(items, columns, config={}) %}
    {% set table_class = config.get('table_class', 'table table-striped') %}
    {% set show_actions = config.get('show_actions', True) %}
    {% set action_column_title = config.get('action_column_title', 'Actions') %}
    
    <div class="table-responsive">
        <table class="{{ table_class }}">
            <thead>
                <tr>
                    {% for column in columns %}
                        <th {% if column.sortable %}class="sortable"{% endif %}>
                            {% if column.sortable %}
                                <a href="{{ url_for(request.endpoint, sort=column.key, 
                                                   order='desc' if request.args.get('sort') == column.key 
                                                   and request.args.get('order') == 'asc' else 'asc') }}">
                                    {{ column.title }}
                                    {% if request.args.get('sort') == column.key %}
                                        <span class="sort-indicator">
                                            {% if request.args.get('order') == 'asc' %}↑{% else %}↓{% endif %}
                                        </span>
                                    {% endif %}
                                </a>
                            {% else %}
                                {{ column.title }}
                            {% endif %}
                        </th>
                    {% endfor %}
                    {% if show_actions %}
                        <th>{{ action_column_title }}</th>
                    {% endif %}
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                    <tr>
                        {% for column in columns %}
                            <td>
                                {% if column.template %}
                                    {% include column.template %}
                                {% elif column.formatter %}
                                    {{ column.formatter(item[column.key]) }}
                                {% else %}
                                    {{ item[column.key] }}
                                {% endif %}
                            </td>
                        {% endfor %}
                        {% if show_actions %}
                            <td class="actions">
                                {% block table_actions %}
                                    {% if config.actions %}
                                        {% for action in config.actions %}
                                            <a href="{{ action.url(item) }}" 
                                               class="btn btn-sm {{ action.class|default('btn-outline-primary') }}"
                                               {% if action.confirm %}
                                                   onclick="return confirm('{{ action.confirm }}')"
                                               {% endif %}>
                                                {{ action.title }}
                                            </a>
                                        {% endfor %}
                                    {% endif %}
                                {% endblock %}
                            </td>
                        {% endif %}
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
{% endmacro %}
```

**4. Dynamic Template Generation Patterns:**

```python
# app/utils/template_helpers.py
def get_entity_context(entity_type, entity_data=None, page_type='list'):
    """Generate standardized context for entity templates"""
    base_context = {
        'entity_type': entity_type,
        'entity_type_title': entity_type.replace('_', ' ').title(),
        'page_type': page_type,
    }
    
    if page_type == 'list':
        base_context.update({
            'columns': get_entity_columns(entity_type),
            'actions': get_entity_actions(entity_type),
            'filters': get_entity_filters(entity_type),
        })
    elif page_type == 'detail' and entity_data:
        base_context.update({
            'entity': entity_data,
            'fields': get_entity_detail_fields(entity_type),
            'related_entities': get_related_entities(entity_type, entity_data.id),
        })
    elif page_type == 'form':
        base_context.update({
            'form_fields': get_entity_form_fields(entity_type),
            'form_config': get_entity_form_config(entity_type),
        })
    
    return base_context

def get_entity_columns(entity_type):
    """Return column configuration for entity list views"""
    # This would be customized per project but follows consistent pattern
    common_columns = [
        {'key': 'id', 'title': 'ID', 'sortable': True},
        {'key': 'name', 'title': 'Name', 'sortable': True},
        {'key': 'created_at', 'title': 'Created', 'sortable': True, 
         'formatter': 'date_formatter'},
        {'key': 'status', 'title': 'Status', 'template': 'partials/status_badge.html'},
    ]
    return common_columns
```

**5. Include vs Import Strategy:**

```jinja2
<!-- Use {% include %} for templates that need current context -->
{% include 'components/flash_messages.html' %}  <!-- Needs current flash messages -->
{% include 'components/navigation.html' %}       <!-- Needs current user context -->

<!-- Use {% import %} for macro libraries -->
{% from 'macros/base/forms.html' import text_input, select_input %}
{% from 'macros/components/data-display.html' import data_table, card %}

<!-- Use {% import %} with context when macros need template variables -->
{% from 'macros/entities/list-views.html' import entity_list with context %}
```

**6. Context Standardization Patterns:**

```python
# app/utils/context_processors.py
@app.context_processor
def inject_universal_context():
    """Inject commonly needed template variables"""
    return {
        'app_name': current_app.config['APP_NAME'],
        'version': current_app.config['VERSION'],
        'current_user': current_user if current_user.is_authenticated else None,
        'current_route': request.endpoint,
        'query_params': request.args.to_dict(),
        'flash_messages': get_flashed_messages(with_categories=True),
    }

def get_standard_pagination_context(query, page, per_page=20):
    """Generate consistent pagination context"""
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': paginated.items,
        'pagination': {
            'page': page,
            'pages': paginated.pages,
            'per_page': per_page,
            'total': paginated.total,
            'has_prev': paginated.has_prev,
            'prev_num': paginated.prev_num,
            'has_next': paginated.has_next,
            'next_num': paginated.next_num,
        }
    }
```

**7. Loop and Iteration Patterns:**

```jinja2
<!-- templates/macros/utilities/loops.html -->
{% macro grouped_items(items, group_by_key, group_template=None) %}
    {% set grouped = items | groupby(group_by_key) %}
    {% for group_name, group_items in grouped %}
        <div class="item-group" data-group="{{ group_name }}">
            {% if group_template %}
                {% include group_template %}
            {% else %}
                <h3 class="group-header">{{ group_name }}</h3>
                <div class="group-items">
                    {% for item in group_items %}
                        {% block group_item %}{{ item }}{% endblock %}
                    {% endfor %}
                </div>
            {% endif %}
        </div>
    {% endfor %}
{% endmacro %}

{% macro batch_processor(items, batch_size=10, batch_template=None) %}
    {% for batch in items | batch(batch_size) %}
        <div class="batch-group" data-batch="{{ loop.index }}">
            {% if batch_template %}
                {% include batch_template %}
            {% else %}
                {% for item in batch %}
                    {% block batch_item %}{{ item }}{% endblock %}
                {% endfor %}
            {% endif %}
        </div>
    {% endfor %}
{% endmacro %}
```

**8. Template Performance Optimization:**

```jinja2
<!-- Cache expensive template operations -->
{% set cached_navigation = cache.get('navigation_' + current_user.role) %}
{% if not cached_navigation %}
    {% set cached_navigation = generate_navigation(current_user.role) %}
    {{ cache.set('navigation_' + current_user.role, cached_navigation, timeout=300) }}
{% endif %}

<!-- Use template fragment caching for expensive renders -->
{% cache 300, 'entity_stats', entity_type, current_user.id %}
    {{ macros.entity_statistics(entity_type, current_user) }}
{% endcache %}

<!-- Optimize loops with batch processing for large datasets -->
{% if items | length > 100 %}
    {{ macros.batch_processor(items, batch_size=20) }}
{% else %}
    {% for item in items %}
        {{ macros.item_card(item) }}
    {% endfor %}
{% endif %}
```

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 13-09-25-13h-15m-00s | 57ad43d3-ad12-46e8-8f3e-abd7c0ebc32c.jsonl | Universal ADR coverage | Initial creation | Document comprehensive Jinja DRY patterns | Establish universal template standards applicable to all projects |

---

**Impact Assessment:** High - This establishes fundamental template architecture patterns that affect all web application development.

**Review Required:** Mandatory - All team members must understand and implement these DRY patterns in their template development.

**Next Steps:**
1. Implement template inheritance hierarchy in all new projects
2. Create macro libraries following established organization patterns
3. Establish template code review checklist for DRY compliance
4. Create project templates that implement these patterns by default
5. Document project-specific adaptations of these universal patterns