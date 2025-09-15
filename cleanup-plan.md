# CRM Template & CSS Cleanup Plan

## Current State Analysis

### Major Issues Found

#### 1. Inline JavaScript Event Handlers
- `onclick` attributes with complex logic throughout templates
- Event dispatching directly in HTML attributes
- JavaScript business logic embedded in Jinja templates

#### 2. Parameter Abuse
- `additional_class` / `additional_classes` parameters enabling bad practices
- Animation/rotation classes passed as icon parameters
- Style decisions passed through macro parameters instead of using CSS

#### 3. CSS-in-Jinja Anti-patterns
```jinja
{%- set size_classes = {'sm': 'h-4 w-4', 'md': 'h-6 w-6'} -%}
```
This violates ADR-011 - Jinja should generate class names, not define styles

#### 4. Directory Structure Chaos
- 17 directories for 35 template files
- Duplicate concepts: `components/` AND `macros/components/`
- Unclear separation: `base/` vs `core/` vs `ui/` vs `widgets/`

#### 5. Tailwind Overuse
- 10+ utility classes per element in some cases
- No semantic meaning in class names
- Repeated patterns not extracted to CSS components

## Cleanup Actions

### 1. Remove ALL Animation/Rotation Parameters

**Delete:**
```jinja
{{ icon('chevron-down', 'sm', 'rotate-180 transition-transform') }}
{{ icon('spinner', 'md', 'animate-spin') }}
```

**Replace with:**
```jinja
{{ icon('chevron-down', 'sm') }}
{{ icon('spinner', 'md') }}
```

Rotation/animation should be handled by CSS classes on parent elements, not icon parameters.

### 2. Remove ALL `additional_class` Parameters

**Files to clean:**
- `/macros/base/icons.html` - Remove `additional_class` parameter
- `/macros/ui/badges.html` - Remove `additional_classes` parameter
- `/macros/ui/utilities.html` - Remove all `additional_classes`
- `/macros/base/buttons.html` - Remove `classes` parameter

These parameters encourage inline styling instead of proper CSS architecture.

### 3. Extract Inline JavaScript

**Current (BAD):**
```html
onclick="event.stopPropagation(); confirmAction('delete', '{{ entity_type }}', {{ entity.id }})"
```

**New (GOOD):**
```html
data-action="delete"
data-entity-type="{{ entity_type }}"
data-entity-id="{{ entity.id }}"
```

Move ALL event handlers to external JavaScript files using data attributes for configuration.

### 4. Move Style Logic to CSS

**Delete from templates:**
```jinja
{%- set size_classes = {'sm': 'h-4 w-4', 'md': 'h-6 w-6', 'lg': 'h-8 w-8'} -%}
```

**Add to CSS:**
```css
.icon-sm { @apply h-4 w-4; }
.icon-md { @apply h-6 w-6; }
.icon-lg { @apply h-8 w-8; }
```

### 5. Simplify Directory Structure

**Current (17 directories):**
```
templates/
├── base/
├── components/
│   ├── dashboard/
│   ├── empty_states/
│   ├── modals/
│   └── notes/
├── dashboard/
├── macros/
│   ├── base/
│   ├── components/
│   ├── core/
│   ├── dashboard/
│   ├── modals/
│   ├── ui/
│   └── widgets/
└── shared/
```

**New (4 directories):**
```
templates/
├── layouts/      # Page layouts only
├── pages/        # Complete pages
├── components/   # ALL reusable components
└── macros/       # Pure helper functions only
```

### 6. Tailwind Best Practices

#### Use Tailwind for:
- Basic spacing: `p-4`, `mt-2`
- Simple flexbox: `flex`, `items-center`
- One-off utilities that don't repeat

#### Use CSS Components for:
- Repeated patterns (used 3+ times)
- Complex multi-state components
- Semantic elements

**Example:**
```css
/* Instead of repeating this Tailwind soup everywhere */
.entity-card {
  @apply flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow;
}
```

## Implementation Priority

### Phase 1: Critical Fixes
1. Remove ALL inline JavaScript event handlers
2. Fix the `None.get()` error in forms.html
3. Remove animation/rotation from icon calls

### Phase 2: Parameter Cleanup
1. Remove all `additional_class` parameters
2. Move size mappings from Jinja to CSS
3. Clean up button macros

### Phase 3: Structure
1. Consolidate 17 directories to 4
2. Merge duplicate modal templates
3. Merge duplicate dropdown templates

### Phase 4: CSS Components
1. Extract repeated Tailwind patterns to CSS classes
2. Create semantic component classes
3. Remove Tailwind soup from templates

## Expected Results

### Metrics
- **Code Reduction:** ~40% fewer lines
- **Directory Reduction:** 17 → 4 directories
- **Template Files:** 35 → ~20 files
- **Inline JS:** 100% removed
- **Inline Style Logic:** 100% removed

### Benefits
- **Maintainability:** Single source of truth for each component
- **Performance:** Better caching with external JS/CSS
- **Debugging:** Clear separation of concerns
- **ADR Compliance:** Follows ADR-011 architecture

## Files to Delete Completely

1. `/macros/formatting.html` - Consolidated into date_formatting.html
2. `/macros/modals/base/` - Duplicate modal system
3. `/macros/dropdowns.html` - Old dropdown implementation
4. Empty directories after consolidation

## Anti-patterns to Prevent

1. **Never:** Pass CSS classes as macro parameters
2. **Never:** Use onclick attributes
3. **Never:** Define style mappings in Jinja
4. **Never:** Create template variants for CSS differences
5. **Never:** Mix JavaScript logic in templates

## Success Criteria

- [ ] Zero inline event handlers
- [ ] Zero `additional_class` parameters
- [ ] Zero style mappings in Jinja
- [ ] Maximum 4 template directories
- [ ] All repeated patterns extracted to CSS
- [ ] Clean separation: HTML structure / CSS presentation / JS behavior