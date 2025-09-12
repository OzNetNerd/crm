# CRM MVP Architecture Plan

## Core Architecture Principles

- **DRY**: Shared templates, reusable Alpine.js components, common database patterns
- **Non-overengineered**: Standard Flask patterns, minimal JavaScript, simple queries
- **MVP-focused**: Essential features first, clean extension points
- **Scalable Structure**: Directory organization that accommodates growth

## Project Structure

```
app/
├── models/           # SQLAlchemy entities (Company, Contact, Opportunity, Task, Note)
├── routes/           # Flask blueprints (dashboard, companies, contacts, tasks, api)
├── forms/            # WTForms (TaskForm, CompanyForm, ContactForm, etc.)
├── templates/        # Jinja2 templates with shared base/components
├── static/           # Tailwind CSS build + Alpine.js components
├── utils/            # Helper functions (date calculations, search, etc.)
└── services/         # Business logic layer (future growth)
```

## Entity Relationships (Using "Opportunities" terminology)

- **Companies** to **Opportunities**: One-to-many (company has multiple opportunities)
- **Companies** to **Contacts**: One-to-many (company has multiple stakeholders)
- **Contacts** to **Opportunities**: Many-to-many (stakeholder involved in multiple opportunities)
- **Tasks**: Link to any entity (Companies/Contacts/Opportunities) via polymorphic relationship
- **Notes**: Attach to any entity (Companies/Contacts/Opportunities/Tasks) as commentary/updates

## Database Schema

```sql
companies: id, name, industry, website
contacts: id, name, role, email, phone, company_id
opportunities: id, name, company_id, value, probability, close_date, stage
contact_opportunities: contact_id, opportunity_id (many-to-many junction)
tasks: id, description, due_date, priority, status, entity_type, entity_id
notes: id, content, is_internal, entity_type, entity_id, created_at
```

## Database Design

- **5 core tables**: companies, contacts, opportunities, tasks, notes
- **Polymorphic relationships**: Tasks/Notes link to any entity via `entity_type` + `entity_id`
- **Calculated fields**: Virtual properties for days_since_contact, deal_age
- **SQLite**: Single file, zero config, perfect for MVP

## Frontend Architecture

- **Server-rendered**: Jinja2 templates for initial page load
- **Alpine.js**: Collapsible sections, inline editing, filtering, modals
- **HTMX/Fetch**: Partial updates for task completion, search results
- **Tailwind**: Utility-first styling with custom color coding for priorities

## Central Todo Page Implementation

- **Single route** (`/dashboard`) renders all tasks with sections
- **Alpine.js state**: `{ sections: {}, filters: {}, selectedTasks: [] }`
- **Collapsible sections**: Pure Alpine with localStorage persistence
- **Inline editing**: Click-to-edit with immediate save via fetch
- **Modals**: Alpine overlays with dynamic content loading

## Key Technical Decisions

1. **No frontend framework**: Alpine.js handles all interactivity needs
2. **Minimal API**: Only for partial updates (complete task, save edit, search)
3. **Template inheritance**: Base layout to dashboard to task components
4. **Component reuse**: Shared task card, modal, form field templates
5. **Progressive enhancement**: Works with JS disabled, enhanced with JS

## Data Separation

**Tasks** = Actionable outcomes that need completion

- Description, due date, priority, status (todo/in-progress/complete)
- Links to Companies/Contacts/Opportunities
- Has completion state and next step actions

**Notes** = Commentary/updates attached to any entity

- Can attach to Tasks (progress updates, obstacles, solutions)
- Can attach to Companies/Contacts/Opportunities (context, history)
- Internal vs external-facing flag
- Timestamp and rich text content

## Growth Accommodation

- **Modular blueprints**: Easy to add new entity types
- **Polymorphic relationships**: New entities automatically work with tasks/notes
- **Services layer**: Ready for complex business logic
- **API endpoints**: Foundation for mobile apps/integrations
- **Component templates**: Reusable UI patterns
- **Utility functions**: Shared logic across features

## Implementation Order

1. **Models + Database** ✅
2. **Basic routes + templates** (in progress)
3. **Central todo page with sections**
4. **Alpine.js interactivity**
5. **Modals + inline editing**
6. **Search + filtering**

**Total MVP**: ~15 hours of focused development

## Success Metrics

- Sub-second task operations (complete, edit, reschedule)
- Zero full page reloads for common actions
- Works beautifully on mobile and desktop
- Extensible for future features without architectural changes
