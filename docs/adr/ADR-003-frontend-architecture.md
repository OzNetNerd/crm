# ADR-003: Frontend Architecture

## Status
Accepted

## Context
Need a maintainable, performant frontend that prioritizes server-side rendering and progressive enhancement.

## Decision

### Core Stack
- **Jinja2** templates for server-side rendering
- **Tailwind CSS** for utility-first styling
- **HTMX** for dynamic interactions
- **Vanilla JavaScript** for custom behavior

### Template Structure
```
templates/
├── base.html          # Single base template
├── includes/          # Reusable components
│   ├── nav.html
│   ├── footer.html
│   └── forms/
└── pages/             # Page templates
    ├── contacts/
    ├── deals/
    └── dashboard/
```

### Styling Approach

#### Tailwind Utilities
```html
<!-- Direct utility classes, no custom CSS -->
<button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Save Contact
</button>
```

#### Custom CSS (Minimal)
```css
/* Only for things Tailwind can't handle */
.custom-chart-container {
    aspect-ratio: 16/9;
}
```

### JavaScript Strategy

#### HTMX for Interactions
```html
<!-- Server-driven interactions -->
<button hx-post="/api/contacts"
        hx-target="#contact-list"
        hx-swap="afterbegin">
    Add Contact
</button>
```

#### Vanilla JS for Enhancement
```javascript
// Simple, focused scripts
document.addEventListener('DOMContentLoaded', () => {
    // Minimal DOM manipulation
    const modal = document.getElementById('modal');
    // ...
});
```

## Implementation Rules

### Templates
- Maximum 2 levels of inheritance
- Use includes for repeated components
- Pass explicit context, no magic variables

### CSS
- Tailwind utilities first
- Custom CSS only when necessary
- No preprocessors (SASS/LESS)

### JavaScript
- No build step required
- ES6 modules for organization
- Progressive enhancement mindset

## Component Examples

### Form Pattern
```html
<form hx-post="/contacts" hx-target="#response">
    <input type="text" name="name" required
           class="w-full px-3 py-2 border rounded">
    <button type="submit"
            class="mt-2 px-4 py-2 bg-blue-500 text-white rounded">
        Submit
    </button>
</form>
```

### Table Pattern
```html
<table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
        <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Name
            </th>
        </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200">
        {% for contact in contacts %}
        <tr>
            <td class="px-6 py-4 whitespace-nowrap">
                {{ contact.name }}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

## Consequences

### Positive
- Fast initial page loads
- Works without JavaScript
- Simple debugging
- No build complexity
- SEO friendly

### Negative
- Less "app-like" feel
- Limited offline capabilities

## Notes
Server-side rendering is not old-fashioned; it's reliable and fast. Use JavaScript to enhance, not replace, server functionality.