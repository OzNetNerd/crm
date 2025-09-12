# Architecture Decision Record (ADR)

## ADR-005: Restructure Templates/Components to Macros Directory System

**Status:** Implemented  
**Date:** 11-09-25-09h-15m-30s  
**Session:** /home/will/.claude/projects/-home-will-code-crm--worktrees-macros-new/1f165cdd-25ba-4537-aa57-2f591584ea73.jsonl  
**Todo:** N/A (Single comprehensive refactoring)  
**Deciders:** Will, Claude Code Agent

### Context

The CRM application's template system had grown organically with 160 Jinja2 macros scattered across a `templates/components/` directory. Key issues:

- **Misleading naming:** Directory called "components" but contained Jinja2 macros
- **Poor organization:** 39 files with deep nesting (5 levels in modals/)
- **Maintenance burden:** Large monolithic files (ui_elements.html at 1,133 lines)
- **Discovery problems:** Related macros scattered across multiple subdirectories
- **Import complexity:** 5 different import files with overlapping purposes
- **Performance impact:** Large files causing slower template compilation

Analysis showed that while functionally working, the structure hindered developer productivity and future scalability.

### Decision

We will restructure the entire template macro system by:

1. **Rename directory:** `templates/components/` → `templates/macros/`
2. **Implement logical grouping structure:**
   - `base/` - Core foundational macros (buttons, forms, icons, layout)
   - `ui/` - UI controls and interactions (progress, search, navigation)
   - `entities/` - Entity-specific macros (company, opportunity, stakeholder, task, team)
   - `modals/` - Modal components (base functionality, forms, dialogs, configs)
   - `widgets/` - Specialized widgets (chat, filters, metrics, linker)
   - `imports/` - Import aggregators (common, entities, modals)
3. **Split large files:** Break ui_elements.html into focused components
4. **Flatten modal structure:** Reduce from 5 levels to 2 levels deep
5. **Consolidate imports:** Reduce from 5 import files to 3 logical groupings
6. **Update all references:** Maintain 100% backward compatibility

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

**Impact Assessment:** High - This is a foundational change affecting the entire template architecture and developer workflow.

**Review Required:** Yes - Future template organization decisions should reference this ADR.

**Next Steps:**
1. Monitor template performance metrics post-implementation
2. Create developer documentation for new macro organization
3. Establish guidelines for adding new macros to appropriate directories