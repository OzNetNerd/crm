# CRM MVP Application

A simple yet powerful CRM system built with Python/Flask, focused on task management and sales pipeline tracking.

## Features

### Core Functionality
- **Task Management Dashboard**: Central hub with collapsible sections (Overdue, Today, This Week, etc.)
- **Companies**: Manage company relationships and information
- **Contacts**: Track stakeholders with company associations
- **Opportunities**: Sales pipeline tracking with stages and probability
- **Notes**: Attach contextual notes to any entity (companies, contacts, opportunities, tasks)

### Key Features
- **Inline Task Editing**: Click to edit task descriptions directly
- **Quick Actions**: Complete, reschedule (+1 day, +1 week), delete tasks
- **Collapsible Sections**: Organized task view with persistent state
- **Global Search**: Search across all entities (companies, contacts, opportunities, tasks)
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Task operations without page reloads

### Technical Stack
- **Backend**: Flask, SQLAlchemy, WTForms
- **Database**: SQLite (zero configuration)
- **Frontend**: Tailwind CSS, Alpine.js (no build step required)
- **Templates**: Jinja2 with component reuse

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Sample Data (Optional)
```bash
python sample_data.py
```

### 3. Run the Application
```bash
python3 main.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
app/
├── models/           # Database models (Company, Contact, Opportunity, Task, Note)
├── routes/           # Flask blueprints for each entity + search
├── forms/            # WTForms for validation
├── templates/        # Jinja2 templates
│   ├── base/         # Base layout
│   ├── components/   # Reusable components (task cards, modals)
│   ├── dashboard/    # Task dashboard
│   └── [entities]/   # Entity-specific templates
├── static/
│   ├── js/           # Alpine.js components and interactions
│   └── css/          # Custom styles (minimal)
└── utils/            # Helper functions
```

## Architecture Highlights

### Database Design
- **Polymorphic relationships**: Tasks and Notes can link to any entity via `entity_type` + `entity_id`
- **Many-to-many**: Contacts can be associated with multiple Opportunities
- **Calculated properties**: Deal age, days since contact, overdue status

### Frontend Approach
- **Server-rendered**: Initial page loads with Jinja2 templates
- **Progressive enhancement**: Alpine.js adds interactivity
- **Component-based**: Reusable template macros for task cards, modals
- **No build process**: Uses CDN for Alpine.js and Tailwind CSS

### Task Management
- **Section-based organization**: Overdue (auto-expanded), Today, This Week, etc.
- **Persistent state**: Section collapsed/expanded state saved in localStorage
- **Inline editing**: Click-to-edit functionality with immediate API updates
- **Quick actions**: Common operations accessible without modals

## API Endpoints

### Task Operations
- `POST /tasks/<id>/complete` - Mark task as complete
- `POST /tasks/<id>/update` - Update task details
- `POST /tasks/<id>/reschedule` - Reschedule task by X days

### Search
- `GET /api/search?q=query` - Global search across all entities
- `GET /api/autocomplete?q=query&type=entity` - Entity-specific autocomplete

## Sample Data

The `sample_data.py` script creates realistic test data:
- 5 companies with different industries
- 6 contacts across companies
- 5 opportunities in various stages
- 8 tasks (overdue, today, this week, completed)
- 5 notes attached to different entities

## Development Notes

### MVP Principles
- **Simple**: Standard Flask patterns, minimal JavaScript
- **Fast**: Sub-second task operations, no unnecessary abstractions
- **Extensible**: Clean separation of concerns, ready for growth

### Future Extensions
- Mobile app API endpoints already structured
- Modal system ready for complex forms
- Polymorphic relationships support new entity types
- Search infrastructure scales to advanced filtering

## Database Schema

```sql
companies: id, name, industry, website
contacts: id, name, role, email, phone, company_id
opportunities: id, name, company_id, value, probability, close_date, stage
contact_opportunities: contact_id, opportunity_id (junction table)
tasks: id, description, due_date, priority, status, entity_type, entity_id
notes: id, content, is_internal, entity_type, entity_id, created_at
```

## Success Metrics

- ✅ Sub-second task operations (complete, edit, reschedule)
- ✅ Zero full page reloads for common actions
- ✅ Mobile-responsive design
- ✅ Extensible architecture for future features
- ✅ Clean, uncluttered interface focused on productivity