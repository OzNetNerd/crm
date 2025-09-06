# Architecture Decision Record (ADR)

## ADR-002: RESTful Resource Hierarchy API Design Pattern

**Status:** Accepted  
**Date:** 06-09-25-19h-02m-15s  
**Session:** /home/will/.claude/projects/-home-will-code-crm/c2222c23-9799-4bb0-b031-83808c2a47e1.jsonl  
**Todo:** /home/will/.claude/todos/c2222c23-9799-4bb0-b031-83808c2a47e1.json  
**Deciders:** Will Robinson, Development Team

### Context
The CRM system needed a consistent API design pattern for handling relationships between entities and their sub-resources (particularly notes). The initial implementation used a generic entity-based approach, but as documented in API_REFACTOR.md, this created inconsistencies with REST conventions. Requirements included:
- Consistent RESTful API patterns
- Clear resource hierarchy representation  
- Scalability for future sub-resources (attachments, comments, etc.)
- Alignment with existing route patterns

### Decision
We will adopt a **RESTful Resource Hierarchy** pattern for API design:
- Sub-resources are accessed through their parent resource path
- Use standard HTTP methods (GET, POST, PUT, DELETE) with resource hierarchy
- Notes API pattern: `/api/{entity_type}/{entity_id}/notes`
- Individual note operations: `/api/notes/{note_id}` for update/delete
- Maintain consistency with existing UI route patterns

### Rationale
Resource hierarchy provides the best balance of:
- **REST Compliance**: Standard REST conventions for sub-resource access
- **Clarity**: URL structure immediately shows entity-sub-resource relationship  
- **Consistency**: Aligns with existing route patterns (`/tasks/123`, `/companies/456`)
- **Scalability**: Easy to extend with other sub-resources (`/tasks/123/attachments`)
- **Developer Experience**: Intuitive API structure for frontend development

### Alternatives Considered
- **Option A: Generic Entity Routes** - Current implementation, violates REST conventions
  - Example: `/api/notes/entity/task/123` 
  - Rejected: Non-standard, doesn't follow REST hierarchy patterns
- **Option B: Flat Note Routes** - All notes managed independently
  - Example: `/api/notes?entity_type=task&entity_id=123`
  - Rejected: Loses clear parent-child relationship in URL structure
- **Option C: Mixed Approach** - Some hierarchical, some flat
  - Rejected: Inconsistent patterns confuse API consumers

### Consequences

**Positive:**
- Standard REST conventions improve API discoverability
- URL structure clearly communicates resource relationships
- Consistent with existing UI route patterns (`/tasks/123`)
- Easy to extend pattern to other sub-resources (attachments, comments)
- Better alignment with OpenAPI/Swagger documentation tools

**Negative:**
- Requires refactoring existing generic entity note routes
- More API endpoints to implement and maintain
- Need to handle entity validation in each endpoint

**Neutral:**
- Change from `/api/notes/entity/{type}/{id}` to `/api/{type}s/{id}/notes`
- Individual note operations remain at `/api/notes/{id}` for simplicity
- Frontend code needs updates to use new endpoint patterns

### Implementation Notes
- New API structure:
  - `GET /api/tasks/123/notes` - Get notes for task 123
  - `POST /api/tasks/123/notes` - Create note for task 123
  - `GET /api/companies/456/notes` - Get notes for company 456  
  - `POST /api/companies/456/notes` - Create note for company 456
  - `PUT /api/notes/789` - Update note 789 (unchanged)
  - `DELETE /api/notes/789` - Delete note 789 (unchanged)
- Entity validation occurs at parent resource level
- Maintains backward compatibility during transition period
- Pattern extends to opportunities, contacts as needed

### Version History
| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 06-09-25-19h-02m-15s | c2222c23.jsonl | N/A | Initial | Initial ADR creation | Document API design pattern decision |