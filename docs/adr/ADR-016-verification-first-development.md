# Architecture Decision Record (ADR) Template

## ADR-016: Verification-First Development

**Status:** Accepted
**Date:** 20-09-25-07h-30m-00s
**Session:** /home/will/.claude/projects/crm-worktrees-comp23/194f14e0-e2f1-4c77-a205-70218ca207bf.jsonl
**Deciders:** Will, Claude Code

### Context
We've observed significant time waste and errors caused by making assumptions about code structure, database relationships, and file locations instead of verifying their actual state. Examples include:
- Assuming database relationships exist without checking
- Guessing file locations instead of finding them
- Creating code based on expected patterns that don't exist
- Making database schema assumptions that are incorrect

This has led to debugging sessions, failed implementations, and wasted development time.

### Decision
**ALWAYS verify the actual state of the system before implementing changes.** Never make assumptions about:
- Database relationships and schema
- File locations and structure
- Existing code patterns
- API endpoints and routes
- Configuration values

Instead, use verification commands FIRST before any implementation.

### Rationale
- **Accuracy**: Verification ensures we work with actual system state, not assumptions
- **Efficiency**: Prevents wasted time on incorrect implementations
- **Reliability**: Reduces bugs caused by incorrect assumptions
- **Transparency**: Shows the user exactly what we're checking and why
- **Learning**: Each verification teaches us about the actual codebase

### Alternatives Considered
- **Continue with assumptions**: Rejected - causes too many errors and wastes time
- **Document everything extensively**: Rejected - documentation gets outdated, verification is always current
- **Use type hints only**: Rejected - helpful but insufficient for runtime verification

### Consequences

**Positive:**
- Dramatically reduced debugging time
- Fewer incorrect implementations
- More reliable code changes
- Better understanding of actual system state
- User sees exactly what's being verified

**Negative:**
- Slightly slower initial development (offset by fewer errors)
- More verbose output during development
- Additional commands to run

**Neutral:**
- Changes development rhythm to verify-then-implement
- Requires discipline to always check first

### Implementation Notes

#### Verification Patterns

**Database Relationships:**
```bash
# Check if a relationship exists
grep -r "relationship\(" app/models/company.py
grep -r "account_team" app/models/

# Verify actual database schema
python -c "from app.models import Company; print(dir(Company))"
```

**File Locations:**
```bash
# Never assume - always find
find . -name "*.db" -type f
find . -name "seed*.py"
ls -la instance/  # Check what actually exists
```

**Code Patterns:**
```bash
# Verify existing patterns before creating new ones
grep -r "def search" --include="*.py"
grep -r "selectEntity" --include="*.js"
```

**Configuration:**
```bash
# Check actual configuration values
grep -r "DATABASE" --include="*.py"
cat .env 2>/dev/null || echo "No .env file"
```

#### Required Verification Steps

1. **Before modifying models**: Verify relationships and fields exist
2. **Before creating functions**: Check if similar functions already exist
3. **Before file operations**: Confirm actual file paths
4. **Before database changes**: Verify current schema
5. **Before API calls**: Check endpoint existence

#### Example Workflow

```python
# BAD - Assumption-based
company.account_team_assignments.all()  # Assumes relationship exists

# GOOD - Verification-first
# First: grep -r "account_team" app/models/company.py
# Found: No relationship exists
# Action: Ask user or check alternative approaches
```

### Version History
| Date | Session | Commit | Changes | Rationale |
|------|---------|--------|---------|-----------|
| 20-09-25-07h-30m-00s | 194f14e0.jsonl | Initial | Initial ADR creation | Prevent assumption-based errors |

---

## Enforcement Checklist

Before any implementation, Claude Code MUST:
- [ ] Verify file locations with `find` or `ls`
- [ ] Check relationships with `grep -r "relationship("`
- [ ] Confirm patterns exist with targeted searches
- [ ] Test database structure with actual queries
- [ ] Validate configuration with file checks

**Remember: Trust nothing, verify everything.**