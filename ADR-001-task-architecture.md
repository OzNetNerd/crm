# Architecture Decision Record (ADR)

## ADR-001: Task Architecture with Parent/Child Relationships

**Status:** Accepted  
**Date:** 06-09-25-18h-58m-42s  
**Session:** /home/will/.claude/projects/-home-will-code-crm/c2222c23-9799-4bb0-b031-83808c2a47e1.jsonl  
**Todo:** /home/will/.claude/todos/c2222c23-9799-4bb0-b031-83808c2a47e1.json  
**Deciders:** Will Robinson, Development Team

### Context
The CRM system needed a task management system that could handle both simple standalone tasks and complex multi-step workflows. Requirements included:
- Support for hierarchical task relationships (parent/child)
- Polymorphic entity relationships (tasks can link to companies, contacts, opportunities)
- Sequential and parallel task dependencies
- Flexible task organization without overengineering

### Decision
We will implement a hybrid task architecture with these components:
- **Polymorphic Entity Linking**: Tasks connect to any entity via `entity_type` + `entity_id`
- **Parent/Child Relationships**: Tasks can have parent tasks via `parent_task_id` foreign key
- **Task Types**: `single`, `parent`, `child` to categorize task hierarchy
- **Dependency Types**: `sequential` vs `parallel` execution for child tasks
- **Sequence Ordering**: `sequence_order` field for child task organization

### Rationale
This design offers the best balance of:
- **Flexibility**: Can handle both simple and complex task workflows
- **Simplicity**: Uses standard foreign key relationships, not complex graph structures
- **Performance**: Simple queries for common operations (get all tasks for entity)
- **Scalability**: Easy to extend with additional task metadata fields
- **MVP Compliance**: Delivers core functionality without overengineering

### Alternatives Considered
- **Option A: Flat Task Structure** - Simple but can't handle multi-step workflows
- **Option B: Separate TaskTemplate + TaskInstance** - Too complex for MVP, introduces data duplication
- **Option C: Graph Database** - Overkill for requirements, adds technology complexity
- **Option D: JSON-based hierarchy** - Difficult to query, poor referential integrity

### Consequences

**Positive:**
- Supports both simple tasks and complex workflows in single model
- Standard SQL relationships enable efficient queries and joins
- Clear separation between task types simplifies UI logic
- Easy to implement task completion cascading (complete parent when all children done)

**Negative:**
- Slightly more complex database model than flat structure
- Need to handle parent/child logic in application code
- Task deletion requires cascade handling for child tasks

**Neutral:**
- Additional fields in task table (task_type, parent_task_id, sequence_order, dependency_type)
- UI needs to accommodate both simple and hierarchical task views

### Implementation Notes
- Task model includes fields: `task_type`, `parent_task_id`, `sequence_order`, `dependency_type`
- Polymorphic relationships use `entity_type` + `entity_id` pattern
- Seed data creates realistic parent/child task scenarios (8 parent tasks with 3-5 children each)
- Sequential dependencies can enforce order, parallel allows concurrent execution
- Child task completion logic can trigger parent task status updates

### Version History
| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 06-09-25-18h-05m-59s | 2e18b3e2.jsonl | N/A | 0fbeef3: feat | Initial ADR creation | Document parent/child task architecture |
| 06-09-25-18h-41m-28s | 5716644d.jsonl | N/A | f9834d6: feat | Added entity serialization | Enable task-entity relationships in UI |