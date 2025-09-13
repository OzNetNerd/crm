# Example Usage of Simplified Styling System

## Template Usage Examples

### 1. Using Streamlined Imports

```jinja2
{% extends "base/layout.html" %}
{% from "macros/imports/streamlined.html" import activate_imports, modal_container, simple_page_header %}
{% from "macros/cards_simplified.html" import entity_card, card_list %}

{% block content %}
{{ simple_page_header('Companies', 'Manage your company relationships', buttons=action_buttons) }}

<!-- Use simplified card list -->
{{ card_list(companies, actions=company_actions, empty_message="No companies found") }}

{% endblock %}
```

### 2. Using Semantic CSS Classes

#### Before (Verbose Tailwind):
```html
<div class="w-full px-3 py-2 border border-gray-200 rounded-md text-sm bg-gray-50">
    {{ value }}
</div>
```

#### After (Semantic CSS):
```html
<div class="field-readonly">
    {{ value }}
</div>
```

### 3. Entity-Themed Components

#### Cards with Entity Theming:
```jinja2
<!-- Automatically applies company colors -->
{{ entity_card(company) }}

<!-- Automatically applies task colors -->
{{ entity_card(task) }}
```

#### Buttons with Entity Theming:
```html
<button class="btn-company">Company Action</button>
<button class="btn-task btn-sm">Small Task Action</button>
```

### 4. Form Fields with Entity Theming

```html
<!-- Automatically applies company focus colors -->
<input class="field-editable field-company" />

<!-- Read-only field -->
<div class="field-readonly">{{ value }}</div>

<!-- Form labels -->
<label class="text-form-label">Field Name</label>
```

### 5. Dropdown Components

```jinja2
<!-- Fixed dropdown with proper styling -->
{{ css_dropdown('Select Status', status_options,
    name='status',
    current_value=current_status,
    hx_target='#content',
    hx_get='/update-status') }}
```

## CSS Class Reference

### Entity-Themed Classes
- `card-{entity}` - Entity-themed cards (card-company, card-task, etc.)
- `btn-{entity}` - Entity-themed buttons (btn-company, btn-task, etc.)
- `badge-{entity}` - Entity-themed badges
- `form-{entity}` - Entity-themed forms

### Component Classes
- `field-readonly` - Read-only form fields
- `field-editable` - Editable form fields
- `field-{entity}` - Entity-themed field focus states
- `text-form-label` - Form labels
- `dropdown-button` - Dropdown buttons
- `dropdown-menu` - Dropdown menus
- `dropdown-option` - Dropdown options

### Layout Classes
- `main-container` - Main page container
- `nav-container`, `nav-inner`, `nav-content` - Navigation layout
- `page-header` - Page headers
- `section-header` - Section headers
- `grid-2` - Two-column grid
- `grid-responsive` - Responsive grid
- `flex-between` - Flex with space-between
- `flex-center` - Flex centered

### Modal Classes
- `modal-field` - Modal form fields
- `modal-field-group` - Modal field groups
- `modal-field-grid` - Modal field grids
- `modal-buttons` - Modal button areas
- `btn-secondary` - Secondary buttons

## Benefits Achieved

1. **Fixed Broken Components**: Dropdowns now work properly with defined CSS classes
2. **Semantic Class Names**: Code intent is clear from class names
3. **Reduced Verbosity**: 50+ character Tailwind chains → 10-15 character semantic classes
4. **Entity Theming**: Consistent colors across all components for each entity type
5. **Simpler Macro Architecture**: Reduced from 34 macro files to focused, maintainable system
6. **CDN Tailwind Compatible**: No build process required, works with browser Tailwind
7. **Easier Maintenance**: Changes to component styling require only CSS updates