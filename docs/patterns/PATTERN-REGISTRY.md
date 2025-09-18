# Pattern Registry - Single Source of Truth

## Purpose
Document ALL existing patterns to prevent duplication. Check this BEFORE creating any new functionality.

## Selection Patterns

### ⚠️ CURRENT DUPLICATES (To Be Consolidated)

| Pattern | Location | Purpose | Status |
|---------|----------|---------|--------|
| `selectEntity()` | `app.js:155-171` | Select entity from dropdown | ❌ DUPLICATE |
| Event delegation | `app.js:121-137` | Handle entity selection clicks | ❌ DUPLICATE |
| `selectEntity()` | `search-widget.js:167-234` | Select entity (overwrites app.js) | ❌ DUPLICATE |
| `selectChoice()` | `search-widget.js:237-304` | Select choice from dropdown | ❌ DUPLICATE |

### ✅ TARGET: Single Unified Pattern

```javascript
// ONE function for ALL selections
window.selectItem = function(fieldName, itemId, itemLabel, itemType) {
    const searchField = document.getElementById(fieldName + '_search');
    const hiddenField = document.getElementById(fieldName);
    const resultsDiv = document.getElementById(fieldName + '_results');

    if (hiddenField) hiddenField.value = itemId;
    if (searchField) searchField.value = itemLabel;
    if (resultsDiv) resultsDiv.style.display = 'none';
};
```

## Search Patterns

### Current Implementation
| Pattern | Location | Purpose | Notes |
|---------|----------|---------|-------|
| Global search | `search-widget.js` | HTMX-powered search | ✅ Good pattern |
| Entity search | `search-widget.js` | Dropdown entity search | ✅ Uses HTMX |
| Choice search | Server-side | WTForms choices | ✅ Server-side |

### Decision Tree
```
Need search functionality?
├── Is it for a dropdown selection?
│   └── Use search-widget.js patterns
├── Is it for global navigation?
│   └── Use HTMX global search
└── Is it for form choices?
    └── Use WTForms server-side
```

## Event Handling Patterns

### Current Implementation
| Pattern | Location | Purpose | Status |
|---------|----------|---------|--------|
| Event delegation | `app.js` | Click handlers | ⚠️ Overused |
| Direct onclick | Templates | Inline handlers | ⚠️ Mixed approach |
| addEventListener | Various JS files | Dynamic handlers | ⚠️ Inconsistent |

### Best Practice
```javascript
// Use ONE approach per feature:
// Option 1: Event delegation (preferred for dynamic content)
document.addEventListener('click', (e) => {
    if (e.target.matches('[data-action]')) {
        // Handle based on data-action
    }
});

// Option 2: HTMX (preferred for server interactions)
// <button hx-post="/action" hx-target="#result">
```

## Modal Patterns

### Current Implementation
| Pattern | Location | Purpose | Status |
|---------|----------|---------|--------|
| `openModal()` | `app.js` | Open modals | ✅ Single implementation |
| `closeModal()` | `app.js` | Close modals | ✅ Single implementation |
| HTMX modals | Templates | Dynamic modals | ✅ Good pattern |

## Validation Patterns

### Current Implementation
| Pattern | Location | Purpose | Status |
|---------|----------|---------|--------|
| WTForms | Server-side | Primary validation | ✅ Authoritative |
| Client hints | JS (minimal) | UX only | ✅ Non-authoritative |

### Rule
**NEVER duplicate validation logic. Server is truth.**

## API Endpoint Patterns

### Current Structure
```python
# Standard RESTful pattern
@bp.route('/<model>/', methods=['GET'])          # List
@bp.route('/<model>/<id>', methods=['GET'])      # View
@bp.route('/<model>/create', methods=['POST'])   # Create
@bp.route('/<model>/<id>/edit', methods=['POST']) # Update
@bp.route('/<model>/<id>/delete', methods=['POST']) # Delete
```

### Search Endpoints
```python
# Unified search pattern
@bp.route('/search/<entity_type>')  # NOT separate endpoints per type
```

## Data Transformation Patterns

### Current Implementation
| Pattern | Location | Purpose | Status |
|---------|----------|---------|--------|
| Sorting | Server (Python) | Data ordering | ✅ Correct |
| Filtering | Server (Python) | Data filtering | ✅ Correct |
| Grouping | Server (Python) | Data grouping | ✅ Correct |
| Pagination | Server (Python) | Data paging | ✅ Correct |

### Rule
**NEVER do data transformation client-side. Use HTMX.**

## Component Patterns

### Form Components
- Location: `/app/templates/components/forms/`
- Pattern: Jinja macros with WTForms
- Extension: Add macro parameters, don't create new

### UI Components
- Location: `/app/templates/macros/ui.html`
- Pattern: Reusable Jinja macros
- Extension: Add options to existing macros

## State Management Patterns

### Current Implementation
| Pattern | Location | Purpose | Status |
|---------|----------|---------|--------|
| URL params | Server | Navigation state | ✅ Good |
| Hidden fields | Forms | Form state | ✅ Good |
| Local storage | Avoided | Persistent state | ✅ Minimal use |
| Alpine.js | Minimal | UI state only | ✅ UI only |

## File Organization Patterns

```
/app/
├── /static/
│   ├── /js/
│   │   ├── app.js           # Core functionality
│   │   └── /features/        # Feature-specific JS
│   └── /css/
│       └── main.css          # All styles
├── /templates/
│   ├── /components/          # Reusable components
│   ├── /macros/             # Jinja macros
│   └── /pages/              # Full pages
└── /routes/                 # Python blueprints
```

## How to Extend Patterns

### ❌ DON'T: Create New Similar Pattern
```javascript
// BAD: New function for similar purpose
function selectUser(userId, userName) { /* ... */ }
function selectCompany(companyId, companyName) { /* ... */ }
```

### ✅ DO: Extend Existing Pattern
```javascript
// GOOD: One function with parameters
function selectItem(fieldName, itemId, itemLabel, itemType) {
    // Handle all cases with parameters
}
```

## Compliance Checking

Before creating ANY new pattern:

1. **Check this registry** - Is there an existing pattern?
2. **Search codebase** - `grep -r "similar_function"`
3. **Run compliance** - `/compliance-check all`
4. **Document decision** - Why can't you extend existing?

## Registry Maintenance

This registry should be updated when:
- New patterns are approved and added
- Duplicates are consolidated
- Patterns are deprecated

Last Updated: 2025-01-18
Last Audit: Found 4 duplicate selection systems