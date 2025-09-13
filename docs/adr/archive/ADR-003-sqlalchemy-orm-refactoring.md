# Architecture Decision Record (ADR)

## ADR-003: SQLAlchemy ORM Relationship Refactoring

**Status:** Accepted  
**Date:** 10-09-25-20h-35m-28s  
**Session:** /home/will/.claude/projects/-home-will-code-crm--worktrees-complaince/9c6d28aa-8bb6-4c88-847e-bd535f6d88c4.jsonl  
**Todo:** /home/will/.claude/todos/9c6d28aa-8bb6-4c88-847e-bd535f6d88c4.json  
**Deciders:** Will Robinson, Claude Code

### Context

The CRM application was using anti-pattern raw SQL queries mixed with SQLAlchemy ORM, creating maintenance issues and violating DRY principles. Key problems identified:

- **Raw SQL in ORM models**: Methods like `get_relationship_owners()`, `get_account_team()`, `get_stakeholders()` used manual SQL
- **Manual serialization duplication**: Templates and routes manually constructed dictionaries instead of using model methods  
- **Inconsistent data access**: Some code used ORM relationships, others bypassed them with raw queries
- **Single source of truth violation**: Data serialization logic scattered across codebase

**Specific anti-patterns found:**

- Stakeholder model: Raw SQL for relationship owners and MEDDPICC role assignment
- Company model: Raw SQL for account team retrieval  
- Opportunity model: Manual dictionary construction for stakeholders and account teams
- Routes: Duplicated serialization logic instead of leveraging model `to_dict()` methods

### Decision

**We will eliminate SQLAlchemy anti-patterns through complete ORM relationship adoption:**

1. **Replace raw SQL with ORM relationships** in all model methods
2. **Implement `to_dict()` standardization** across all models for consistent serialization
3. **Use ORM lazy loading and joins** instead of manual query construction
4. **Centralize data serialization** in model classes as single source of truth
5. **Preserve raw SQL only where necessary** (MEDDPICC string roles, complex utility queries)

**Specific refactoring implemented:**

- **Stakeholder**: `get_relationship_owners()` → use `self.relationship_owners` ORM relationship
- **Company**: `get_account_team()` → use `self.account_team_assignments` relationship  
- **Opportunity**: `get_stakeholders()` and `get_full_account_team()` → use ORM relationships
- **User**: `get_owned_stakeholder_relationships()` → use `self.owned_stakeholder_relationships`
- **Routes**: Replace manual dictionary construction with `model.to_dict()` calls

### Rationale

**Primary drivers:**

- **Maintainability**: Single source of truth for data serialization eliminates duplication
- **SQLAlchemy best practices**: Proper use of ORM relationships as intended
- **Performance**: Lazy loading and relationship optimization handle efficient querying  
- **Code clarity**: ORM relationships are self-documenting vs opaque raw SQL
- **Testing**: ORM relationships easier to mock and test than raw SQL

**Technical benefits:**

- Clean separation between data access and business logic
- Automatic relationship handling (cascade deletes, lazy loading)
- Better IDE support and type hints for ORM relationships
- Consistent JSON serialization across all API endpoints
- Reduced risk of SQL injection through parameterized ORM queries

### Alternatives Considered

- **Option A: Keep mixed approach** - Rejected due to ongoing maintenance burden and anti-pattern propagation
- **Option B: Move to pure raw SQL** - Rejected as loses ORM benefits (relationships, migrations, type safety)
- **Option C: GraphQL with DataLoader** - Rejected as over-engineering for current requirements
- **Option D: Repository pattern abstraction** - Rejected as adds complexity without clear benefit

### Consequences

**Positive:**

- ✅ **Eliminated 85 lines** of redundant manual dictionary construction and raw SQL
- ✅ **Single source of truth** for model serialization via `to_dict()` methods
- ✅ **Cleaner codebase** following SQLAlchemy ORM patterns consistently
- ✅ **Improved maintainability** with centralized data access logic
- ✅ **Better performance** through proper ORM relationship lazy loading
- ✅ **Enhanced testability** with mockable ORM relationships

**Negative:**

- ➖ **Learning curve** for developers unfamiliar with advanced ORM relationships
- ➖ **ORM complexity** - need to understand lazy loading and N+1 query implications  
- ➖ **Less explicit control** over exact SQL queries generated

**Neutral:**

- 🔄 **MEDDPICC roles preserved** as raw SQL (string values in junction table require manual handling)
- 🔄 **Complex utility queries** may still require raw SQL where ORM relationships insufficient
- 🔄 **Performance monitoring** needed to ensure ORM queries remain efficient

### Implementation Notes

**Files Modified (5 total):**

- `app/models/company.py`: Replaced `get_account_team()` raw SQL with `account_team_assignments` relationship
- `app/models/opportunity.py`: Refactored `get_stakeholders()` and `get_full_account_team()` to use ORM relationships  
- `app/models/stakeholder.py`: Updated `get_relationship_owners()` and `assign_relationship_owner()` to use ORM
- `app/models/user.py`: Converted `get_owned_stakeholder_relationships()` to use relationship property
- `app/routes/stakeholders.py`: Replaced manual dictionary construction with `stakeholder.to_dict()`

**Migration Pattern:**

1. Identify raw SQL queries in model methods
2. Replace with equivalent ORM relationship access  
3. Update `to_dict()` methods to use ORM relationships
4. Test lazy loading performance and optimize if needed
5. Update routes to use `model.to_dict()` instead of manual serialization

**Preserved Raw SQL:**

- MEDDPICC role management (string values in junction table)
- Complex reporting queries where ORM relationships don't exist
- Performance-critical queries requiring specific SQL optimization

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 10-09-25-20h-35m-28s | efb83bdc-1fe9-47c1-8640-2f8d9f7d37a5.jsonl | Compliance fixes | 61f8204: refactor: eliminate SQLAlchemy anti-patterns | Complete ORM refactoring | Remove anti-patterns, establish single source of truth |
| 10-09-25-21h-15m-00s | 9c6d28aa-8bb6-4c88-847e-bd535f6d88c4.jsonl | Compliance remediation | ADR documentation | ADR-003 creation | Document architectural decision and rationale |
| 13-09-25 | Recent commits | Technical debt remediation | b787079: fix: centralize model serialization | Model serialization consolidation | Complete single source of truth implementation |
| 13-09-25 | Recent commits | Technical debt remediation | c75b678: refactor: consolidate model configuration access methods | Model config standardization | Unified model metadata access patterns |
