# Architecture Decision Record (ADR)

## ADR-005: Universal Template Macro Organization and Directory System

**Status:** Implemented  
**Date:** 11-09-25-09h-15m-30s  
**Session:** /home/will/.claude/projects/-home-will-code-crm--worktrees-macros-new/1f165cdd-25ba-4537-aa57-2f591584ea73.jsonl  
**Todo:** N/A (Single comprehensive refactoring)  
**Deciders:** Will, Claude Code Agent

### Context

Web applications using Jinja2 templating consistently face template organization challenges as macro libraries grow beyond initial prototypes. Common issues across all projects include:

- **Misleading naming:** Directories called "components" but containing Jinja2 macros
- **Poor organization:** Files with deep nesting creating navigation difficulties
- **Maintenance burden:** Large monolithic template files hindering readability
- **Discovery problems:** Related macros scattered across multiple subdirectories
- **Import complexity:** Multiple import files with overlapping purposes
- **Performance impact:** Large files causing slower template compilation

This pattern occurs across all web frameworks using Jinja2 templating and significantly impacts developer productivity and project scalability.

### Decision

We will establish universal template macro organization standards that apply to all web projects using Jinja2:

1. **Standardize directory naming:** `templates/components/` → `templates/macros/` for clarity
2. **Implement logical grouping structure:**
   - `base/` - Core foundational macros (buttons, forms, icons, layout)
   - `ui/` - UI controls and interactions (progress, search, navigation)
   - `entities/` - Domain-specific macros (adaptable per project domain)
   - `modals/` - Modal components (base functionality, forms, dialogs, configs)
   - `widgets/` - Specialized widgets (filters, metrics, interactive components)
   - `imports/` - Import aggregators (common, entities, modals)
3. **Split large files:** Break monolithic template files into focused components
4. **Flatten nested structures:** Reduce deep nesting to maximum 2 levels
5. **Consolidate imports:** Reduce multiple import files to logical groupings
6. **Maintain compatibility:** Ensure smooth migration path for existing templates

### Rationale

**Technical Benefits:**
- **Faster template compilation:** Smaller focused files load and compile faster
- **Better caching:** Template engines can cache individual components more efficiently
- **Reduced complexity:** Clear dependency relationships between macros

**Developer Experience:**
- **Intuitive discovery:** Logical grouping makes finding macros obvious
- **Easier maintenance:** Related functionality grouped together
- **Clear responsibilities:** Each directory has a single, well-defined purpose
- **Simpler imports:** Fewer, more focused import files

**Scalability:**
- **Future-ready:** Clear patterns for adding new macros
- **Modular architecture:** Components can be developed independently
- **Testability:** Smaller files enable focused unit testing

### Alternatives Considered

- **Option A: Keep existing structure** - Rejected due to ongoing maintenance burden and developer confusion
- **Option B: Flatten all files to single directory** - Rejected as it would worsen discovery problems
- **Option C: Group by page/feature** - Rejected because macros are reused across multiple pages
- **Option D: Split by size only** - Rejected because it doesn't improve logical organization

### Consequences

**Positive:**
- Improved developer productivity through better organization
- Enhanced template performance via smaller file sizes
- Reduced onboarding time for new developers
- Clear patterns for future macro development
- Better IDE support and autocomplete
- Easier refactoring and code analysis

**Negative:**
- One-time migration effort for all existing templates
- Temporary git history fragmentation for moved files
- Potential IDE configuration updates needed
- Risk of broken imports if not executed carefully

**Neutral:**
- Directory name change requires team communication
- Import statement updates across codebase
- Documentation updates needed

### Implementation Notes

**Migration Strategy:**
- Maintain 100% backward compatibility during transition
- Use systematic find/replace for import updates
- Test application functionality after each major change
- Preserve git history through proper file moves

**File Organization:**
- Group macros by functional responsibility, not file size
- Maintain consistent naming conventions
- Keep related macros physically close
- Use clear, descriptive directory names

**Performance Optimization:**
- Split 1,133-line ui_elements.html into focused components
- Reduce modal nesting from 5 to 2 levels
- Consolidate overlapping import files
- Enable more efficient template caching

**Quality Assurance:**
- Test all major pages after restructuring
- Verify no broken macro imports
- Confirm template compilation performance
- Validate consistent styling and behavior

### Version History
| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 11-09-25-09h-15m-30s | 1f165cdd.jsonl | N/A | 30228a5: refactor: comprehensive templates/components restructure to macros | Initial ADR creation | Document comprehensive restructuring decision |

---

**Impact Assessment:** High - This establishes universal template organization standards affecting all web application development.

**Review Required:** Mandatory - All projects using Jinja2 templating must follow this macro organization system.

**Next Steps:**
1. Apply this organization system to all new projects using Jinja2 templates
2. Create universal developer documentation for macro organization patterns
3. Establish guidelines for adding new macros across all project types
4. Create project templates that implement this structure by default