# ADR-009: Zero Duplicate Systems Policy

## Status
**Accepted**

## Date
2025-01-18

## Context
During code review, we discovered **4 duplicate selection systems** across 2 JavaScript files:
1. `app.js:155-171` - `selectEntity()` function
2. `app.js:121-137` - Event delegation with `data-entity-select`
3. `search-widget.js:167-234` - `selectEntity()` (overwrites #1)
4. `search-widget.js:237-304` - `selectChoice()`

These duplicates existed despite our CLAUDE.md mandates stating "NEVER create duplicate systems." This represents a critical failure in our enforcement mechanisms.

## Decision
We will implement a **Zero Duplicate Systems Policy** with mandatory enforcement through the `/compliance-check` slash command in Claude Desk.

### What Constitutes Duplication

**CRITICAL DUPLICATES** (Must be eliminated immediately):
- Functions with identical names in different files
- Event handlers processing the same events
- API endpoints handling similar operations
- Validation logic repeated across files

**HIGH PRIORITY DUPLICATES** (Refactor within sprint):
- Similar function signatures doing comparable work
- Parallel implementations for related entities (e.g., selectEntity vs selectChoice)
- Multiple search/filter implementations
- Repeated DOM manipulation patterns

**PATTERN OVERLAPS** (Consider consolidation):
- Similar UI components with minor variations
- Related business logic in different modules
- Comparable data transformation functions

## Implementation Requirements

### 1. Mandatory Pre-Implementation Check
Before writing ANY code, developers MUST:
```bash
# Run in Claude Desk or equivalent
/compliance-check --duplicate-detection
```

### 2. Detection Criteria
The compliance check MUST detect:
- **Exact Matches**: Functions/classes with same names
- **Pattern Similarity**: >70% code similarity between functions
- **Event Overlap**: Multiple handlers for same events/selectors
- **API Redundancy**: Endpoints with overlapping functionality

### 3. Required Documentation
When creating new patterns, developers MUST document:
- Why existing patterns cannot be extended
- What was searched and where
- Explicit justification for new implementation
- Update to Pattern Registry

### 4. Enforcement Levels

**BLOCK** (Cannot proceed):
- Exact function name duplicates
- Identical event handler patterns
- Same API endpoint paths

**WARNING** (Requires justification):
- Similar function patterns (>70% match)
- Related business logic in multiple files
- Comparable UI component implementations

**NOTICE** (Document decision):
- Potentially related patterns
- Similar naming conventions
- Comparable data structures

## Consequences

### Positive
- **Maintainability**: Single source of truth for each system
- **Reliability**: Fewer bugs from inconsistent implementations
- **Development Speed**: Clear patterns to follow, no confusion
- **Code Quality**: Cleaner, DRY codebase

### Negative
- **Initial Overhead**: Must run compliance checks before coding
- **Learning Curve**: Developers must understand existing patterns
- **Refactoring Time**: Must consolidate existing duplicates

## Examples

### ❌ BAD: Creating Duplicate Selection Systems
```javascript
// app.js
function selectEntity(fieldId, entityId, entityName) {
    // Selection logic
}

// search-widget.js
function selectEntity(fieldId, entityId, entityName) {
    // Different selection logic
}

function selectChoice(fieldId, choiceId, choiceLabel) {
    // Almost identical to selectEntity
}
```

### ✅ GOOD: Single Unified System
```javascript
// selection-handler.js
function selectItem(fieldName, itemId, itemLabel, itemType) {
    // One universal selection function
    // Handles all types through parameters
}
```

## Compliance Verification

Run `/compliance-check` to verify:
1. No duplicate function names across files
2. No similar patterns without justification
3. All new patterns documented in Pattern Registry
4. Existing patterns properly extended

## References
- INCIDENT-001: Duplicate Selection Systems
- Pattern Registry: `/docs/patterns/PATTERN-REGISTRY.md`
- Compliance Check Docs: `/docs/compliance/COMPLIANCE-CHECK-REQUIREMENTS.md`

## Decision Makers
- Will (Project Owner)
- Claude Code (Implementation)

## Notes
This ADR was created in response to finding 4 duplicate selection systems that violated our existing mandates but were not caught by any automated checks. The `/compliance-check` enhancement is critical to preventing future violations.