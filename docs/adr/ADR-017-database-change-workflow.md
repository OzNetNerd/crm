# Architecture Decision Record (ADR) Template

## ADR-017: Database Change Workflow

**Status:** Accepted
**Date:** 20-09-25-07h-35m-00s
**Session:** /home/will/.claude/projects/crm-worktrees-comp23/194f14e0-e2f1-4c77-a205-70218ca207bf.jsonl
**Deciders:** Will, Claude Code

### Context
Database changes during development have been handled inconsistently:
- Sometimes using migrations (Alembic)
- Sometimes creating virtual tables or views
- Sometimes modifying the database directly
- Uncertainty about database file location

This inconsistency causes:
- Complex migration histories for simple development changes
- Database state confusion
- Time wasted on migration debugging
- Unnecessary complexity for development iterations

The user has expressed a clear preference: **rebuild the database from seed data** rather than using migrations during development.

### Decision
For all database schema changes during development:

1. **ALWAYS ASK THE USER FIRST** before making any database changes
2. **When approved, use the rebuild approach**:
   - Delete the existing database file
   - Update the seed data script
   - Rebuild from the updated seed
3. **NEVER use migrations or virtual tables** without explicit user permission
4. **Database location is fixed**: `instance/crm.db`
5. **Seed file location is fixed**: `seed_data.py`

### Rationale
- **Simplicity**: No migration complexity during rapid development
- **Clean State**: Each rebuild ensures a fresh, consistent state
- **Faster Iteration**: No debugging migration issues
- **User Preference**: Explicitly requested approach
- **Predictability**: Same process every time
- **Version Control**: Seed file changes are tracked in git

### Alternatives Considered
- **Always use migrations**: Rejected - too complex for development phase
- **Mix approaches**: Rejected - inconsistency causes confusion
- **Virtual tables/views**: Rejected - adds unnecessary abstraction
- **Direct SQL modifications**: Rejected - changes aren't tracked

### Consequences

**Positive:**
- Clean database state every rebuild
- Simple, predictable workflow
- No migration debt accumulation
- Easy to reproduce issues
- Seed file serves as documentation
- Fast iteration on schema changes

**Negative:**
- Development data is lost on rebuild (mitigated by good seed data)
- Must maintain comprehensive seed data
- Not suitable for production (production needs real migrations)

**Neutral:**
- Requires discipline to update seed file
- Development workflow differs from production

### Implementation Notes

#### Standard Workflow

```bash
# 1. ALWAYS ASK FIRST
echo "Database schema changes needed. Should I rebuild the database with updated seed data?"

# 2. If approved, verify current state
ls -la instance/crm.db
ls -la seed_data.py

# 3. Make seed file changes
# Edit seed_data.py to include new schema/data

# 4. Rebuild database
rm instance/crm.db
python seed_data.py

# 5. Verify success
ls -la instance/crm.db
# Test that application starts correctly
```

#### Required User Confirmation

Before ANY database changes, Claude Code MUST ask:
```
"I need to make database changes for [specific reason].
Should I:
1. Rebuild the database with updated seed data (recommended)
2. Use a different approach?

This will delete instance/crm.db and recreate it from seed_data.py."
```

#### Seed File Best Practices

1. **Comprehensive test data**: Include all entity types
2. **Relationship examples**: Show all relationships working
3. **Edge cases**: Include boundary conditions
4. **Comments**: Document why specific data exists
5. **Idempotent**: Can be run multiple times safely

#### When Migrations ARE Appropriate

Migrations should ONLY be used when:
- Moving to staging/production
- User explicitly requests migration approach
- Preserving existing data is critical
- Multiple developers need synchronized changes

### Example Scenarios

**Adding a new field:**
```python
# 1. Ask user first
# 2. Update model in app/models/company.py
# 3. Update seed_data.py to populate new field
# 4. rm instance/crm.db && python seed_data.py
```

**Adding a relationship:**
```python
# 1. Ask user first
# 2. Update models with relationship
# 3. Update seed_data.py with relationship examples
# 4. Rebuild database
```

**Changing field type:**
```python
# 1. Ask user first
# 2. Update model definition
# 3. Update seed data to match new type
# 4. Rebuild database
```

### Version History
| Date | Session | Commit | Changes | Rationale |
|------|---------|--------|---------|-----------|
| 20-09-25-07h-35m-00s | 194f14e0.jsonl | Initial | Initial ADR creation | Standardize database change approach |

---

## Enforcement Checklist

Before database changes, Claude Code MUST:
- [ ] Ask user for permission to rebuild database
- [ ] Verify database location: `instance/crm.db`
- [ ] Verify seed file exists: `seed_data.py`
- [ ] Update seed file with changes
- [ ] Delete old database file
- [ ] Run seed script
- [ ] Verify new database works

**Remember: Always ask first, never migrate without permission, prefer rebuild.**