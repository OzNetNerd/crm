# Notes API Refactor

## Overview

Refactoring the notes API from a generic entity-based structure to a more RESTful resource-hierarchy approach.

## Rationale

- **RESTful Convention**: Standard REST APIs use resource hierarchy (`/tasks/123/notes` not `/notes/task/123`)
- **Consistency**: Aligns with existing route patterns (`/tasks/123`, `/companies/456`)  
- **Clarity**: Notes are clearly sub-resources of their parent entities
- **Scalability**: Easy to extend with other sub-resources (`/tasks/123/attachments`)

## API Structure Changes

### Before (Generic Entity Routes)

```
GET    /api/notes/entity/task/123        # Get notes for task 123
GET    /api/notes/entity/company/456     # Get notes for company 456
POST   /api/notes/                       # Create note (requires entity_type/entity_id in body)
PUT    /api/notes/789                    # Update note 789
DELETE /api/notes/789                    # Delete note 789
```

### After (Resource Hierarchy)

```
GET    /api/tasks/123/notes              # Get notes for task 123
POST   /api/tasks/123/notes              # Create note for task 123
GET    /api/companies/456/notes          # Get notes for company 456
POST   /api/companies/456/notes          # Create note for company 456
PUT    /api/notes/789                    # Update note 789 (unchanged)
DELETE /api/notes/789                    # Delete note 789 (unchanged)
```

## Implementation Details

### Route Distribution

- Notes routes added to respective entity blueprints:
  - `tasks_bp`: `/api/tasks/<id>/notes`
  - `companies_bp`: `/api/companies/<id>/notes`
  - `contacts_bp`: `/api/contacts/<id>/notes`
  - `opportunities_bp`: `/api/opportunities/<id>/notes`

### Frontend Changes

- Task card: `/api/notes/task/123` → `/api/tasks/123/notes`
- Other modals: Update any similar API calls

### Backend Changes

- Remove generic `/api/notes/entity/` route
- Keep specific note operations (`PUT/DELETE /api/notes/<id>`)
- Add entity-specific routes that handle their own notes

## Benefits

1. **Standard REST Practice**: Follows conventional resource hierarchy
2. **Better Organization**: Notes routes distributed to relevant blueprints
3. **Clearer Intent**: URL structure shows ownership relationship
4. **Future-Proof**: Easy to add other sub-resources per entity

## Migration Notes

- Update all frontend API calls to use new structure
- Test all CRUD operations (Create, Read, Update, Delete)
- Ensure backward compatibility during transition if needed
