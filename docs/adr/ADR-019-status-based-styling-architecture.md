# Architecture Decision Record (ADR)

## ADR-019: Status-Based Styling Architecture

**Status:** Accepted
**Date:** 13-09-25-16h-43m-27s
**Session:** /home/will/.claude/projects/-home-will-code-crm--worktrees-col/06f7f6fb-815d-4ff7-a2ce-a100944f55f7.jsonl
**Todo:** /home/will/.claude/todos/06f7f6fb-815d-4ff7-a2ce-a100944f55f7-agent-*.json
**Deciders:** Will Robinson, Development Team

### Context

The CRM application displays sales pipeline statuses with colored text elements throughout the interface. The initial implementation had several issues:

- **Template Logic Pollution**: Status-to-color mapping was hardcoded in Jinja templates
- **No Python Data Flow**: Status information was calculated in templates instead of passed from Python
- **Inline Color Utilities**: Used verbose Tailwind utilities instead of semantic CSS classes
- **DRY Violations**: Color definitions scattered across multiple template files
- **Maintenance Burden**: Changes required updating multiple template locations

Example problematic pattern:
```html
<!-- Before: Template-side calculation and inline utilities -->
{% set value_color = 'green' if status == 'prospect' else 'blue' %}
<div class="text-xl font-bold text-{{ value_color }}-600 mb-1">
```

### Decision

**We will implement a status-based styling architecture that follows Python → CSS → Template data flow:**

1. **Python Provides Status Data**: Backend includes status fields in data structures passed to templates
2. **CSS Defines Status Classes**: Semantic CSS classes handle all status-based styling
3. **Templates Use CSS Classes**: Templates apply status classes without color calculations
4. **CSS Variable Foundation**: Status colors use existing CSS variable system for consistency

**Implementation Pattern:**
```
Python Data → CSS Classes → Template Usage
{status: 'qualified'} → .text-status-qualified → class="text-status-{{ stat.status }}"
```

### Rationale

**Primary drivers:**

- **Separation of Concerns**: Python handles data, CSS handles styling, templates handle structure
- **CSS-First Approach**: Colors defined once in CSS variables, reused consistently
- **Template Simplicity**: No color calculations or conditional logic in Jinja
- **Maintainability**: Status colors changed in one location (CSS variables)
- **Performance**: No runtime color calculation in templates
- **ADR-011 Compliance**: Follows established entity-driven CSS architecture

### Implementation Details

#### 1. CSS Status Classes (`entities.css`)

Following the established pattern from ADR-011, add status-specific classes:

```css
/* Pipeline Status Classes */
.status-prospect {
    border-left-color: var(--color-secondary) !important;
    background-color: var(--color-secondary-lighter);
}

.text-status-prospect {
    color: var(--color-secondary);
}

/* Additional statuses: qualified, proposal, negotiation, closed-won, closed-lost */
```

#### 2. Python Data Structure Enhancement

Backend data structures include status information:

```python
# Before: Only value and label
dashboard_stats = {
    'stats': [{'value': '$50K', 'label': 'Prospect'}]
}

# After: Include status for CSS class generation
dashboard_stats = {
    'stats': [{'value': '$50K', 'label': 'Prospect', 'status': 'prospect'}]
}
```

#### 3. Template Usage Simplification

Templates use semantic CSS classes instead of inline utilities:

```html
<!-- Before: Template logic + inline utilities -->
<div class="text-xl font-bold text-{{ get_status_text_color(status) }} mb-1">

<!-- After: Semantic CSS class -->
<div class="text-xl font-bold text-status-{{ stat.status }} mb-1">
```

### Status Color Mapping

Following design system consistency:

| Status | CSS Variable | Color |
|--------|-------------|-------|
| Prospect | `--color-secondary` | Green |
| Qualified | `--color-primary` | Blue |
| Proposal | `--warning-color` | Yellow |
| Negotiation | `--color-accent` | Purple |
| Closed Won | `--color-secondary` | Green |
| Closed Lost | `--danger-color` | Red |

### Migration Strategy

1. **Add CSS Classes**: Implement status classes in `entities.css`
2. **Update Python Data**: Include status in data structures
3. **Update Templates**: Replace inline utilities with CSS classes
4. **Remove Template Utilities**: Delete status color calculation utilities

### Benefits

- **DRY Principle**: Status colors defined once in CSS
- **Template Clarity**: No color logic in templates
- **Type Safety**: Status values validated in Python models
- **Consistency**: Reuses existing CSS variable system
- **Performance**: No runtime template calculations
- **Scalability**: Easy to add new statuses

### Consequences

**Positive:**
- Simplified template maintenance
- Consistent color application
- Better separation of concerns
- Faster template rendering

**Negative:**
- Requires coordination between Python models and CSS classes
- Initial migration effort for existing templates

### Compliance

This ADR extends ADR-011 (Simple CSS Architecture) by:
- Following entity-driven CSS class patterns
- Using CSS variables for color consistency
- Maintaining flat CSS organization
- Supporting dynamic class generation from Python context

### Related Decisions

- **ADR-011**: Simple CSS Architecture - Establishes entity-driven CSS patterns
- **ADR-008**: DRY Principle Implementation - Eliminates template color logic
- **ADR-014**: Universal Jinja DRY Patterns - Template simplification approach