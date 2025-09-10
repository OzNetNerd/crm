# Button Style Guide

## Entity-Specific Button Colors

This system automatically generates CSS classes based on button labels for consistent styling across the application.

### Color Scheme

| Entity Type | CSS Class | Colors | Usage |
|-------------|-----------|---------|-------|
| Task | `.btn-new-task` | Blue (`bg-blue-600`) | Primary actions, task creation |
| Company | `.btn-new-company` | Green (`bg-green-600`) | Business/growth related actions |
| Opportunity | `.btn-new-opportunity` | Purple (`bg-purple-600`) | Sales/revenue related actions |
| Contact | `.btn-new-contact` | Yellow (`bg-yellow-600`) | People/relationship actions |

### How It Works

1. **Auto-generated Classes**: Button labels like "New Task" automatically generate `btn-new-task` CSS class
2. **No Manual Colors**: Remove all `'color'` parameters from button configurations
3. **Consistent Styling**: All buttons get the same base styles (padding, border-radius, transitions, focus states)

### CSS Implementation

```css
.btn-new-task {
    @apply bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm font-medium rounded-lg 
           focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 
           transition-all duration-200 hover:scale-105;
}
```

### Usage in Templates

**Before (Manual):**
```jinja
{
    'label': 'New Company',
    'color': 'green',  # Manual assignment
    'onclick': 'openNewCompanyModal()'
}
```

**After (Automatic):**
```jinja
{
    'label': 'New Company',  # Color derived from "Company"
    'onclick': 'openNewCompanyModal()'
}
```

### Macro Logic

The `quick_actions_buttons` macro extracts the entity type from the label:
- "New Task" → `btn-new-task`
- "New Company" → `btn-new-company`  
- "New Opportunity" → `btn-new-opportunity`

### Adding New Entity Types

1. Add CSS class in `components.css`:
   ```css
   .btn-new-meeting {
       @apply bg-indigo-600 hover:bg-indigo-700 /* ... rest of styles */;
   }
   ```

2. Use standard label format: "New Meeting"

3. No code changes needed - class is auto-generated!

### Benefits

- **DRY**: One place to define colors (CSS)
- **Consistent**: All buttons get same base styles
- **Maintainable**: Easy to change colors globally
- **Extensible**: New entity types need only CSS rule
- **Semantic**: CSS class names reflect purpose