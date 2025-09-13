# ADR-018: JavaScript ES6 Module Standardization

## Status
Accepted

## Context
The CRM application's JavaScript files were inconsistently using ES6 module syntax (`export` statements) while being loaded as regular scripts in HTML templates. This caused syntax errors like "Uncaught SyntaxError: Unexpected token 'export'" preventing features like global search from functioning.

### Current State
- Multiple JS files use ES6 `export` statements
- HTML templates loaded these files as regular scripts without `type="module"`
- Browser couldn't parse ES6 module syntax in non-module context
- Critical features broken due to JavaScript errors

### Files Affected
- `app/static/js/features/controls.js`
- `app/static/js/features/search-htmx.js`
- `app/static/js/features/modal_handlers.js`
- `app/templates/base/layout.html`

## Decision
We will standardize on ES6 modules throughout the JavaScript codebase by:

1. **Keep ES6 export syntax** in all JavaScript files that use it
2. **Update HTML templates** to load these files with `type="module"`
3. **Maintain consistency** with modern JavaScript standards
4. **Preserve modular architecture** benefits

## Implementation
```html
<!-- Before -->
<script src="{{ url_for('static', filename='js/features/controls.js') }}"></script>

<!-- After -->
<script type="module" src="{{ url_for('static', filename='js/features/controls.js') }}"></script>
```

## Consequences

### Positive
- ✅ Modern JavaScript standards compliance
- ✅ Proper module isolation and encapsulation
- ✅ Better dependency management
- ✅ Eliminates syntax errors
- ✅ Future-proof architecture

### Negative
- ⚠️ Requires ES6-compatible browsers (IE11+ support lost)
- ⚠️ Slight changes in execution timing (modules are deferred by default)

### Neutral
- 📝 No impact on existing functionality once fixed
- 📝 Minimal code changes required

## Notes
- ES6 modules provide better encapsulation than global scripts
- Modern browsers have excellent ES6 module support
- This aligns with industry best practices for JavaScript development
- Future JavaScript files should follow ES6 module patterns

## Date
13-09-25-04h-20m-00s