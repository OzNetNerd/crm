# Architecture Decision Record (ADR)

## ADR-006: Worktree-Based Development Strategy

**Status:** Accepted  
**Date:** 13-09-25-09h-30m-00s  
**Session:** Current comprehensive ADR review  
**Todo:** Complete architectural documentation  
**Deciders:** Will Robinson, Development Team

### Context

The CRM application required a development strategy that supports parallel feature development, isolated environments, and shared database state. Traditional branch switching creates issues with:

- **Database state loss**: Switching branches loses uncommitted schema changes
- **Development conflicts**: Multiple developers working on same codebase simultaneously 
- **Environment isolation**: Need separate development environments for different features
- **Port conflicts**: Multiple instances competing for same development ports
- **Shared resources**: Database instance needs to be accessible across all development environments

The standard git workflow of branch switching was insufficient for this complex Flask application with shared database state.

### Decision

**We will implement a git worktree-based development strategy with intelligent shared resource management:**

1. **Git Worktrees for Isolation**: Each feature/branch gets dedicated working directory via `git worktree`
2. **Shared Database Strategy**: All worktrees share single database instance in main repo `/instance/crm.db`
3. **Automatic Port Detection**: Each worktree auto-detects free ports starting from 5050
4. **Intelligent Database Path Detection**: Services automatically detect worktree vs main repo context
5. **Service Script Integration**: `run.sh` handles port conflicts and service orchestration

**Implementation Pattern:**
```bash
# Main repo: /home/will/code/crm
# Worktree 1: /home/will/code/crm/.worktrees/feature-branch
# Worktree 2: /home/will/code/crm/.worktrees/bug-fix
# Shared DB: /home/will/code/crm/instance/crm.db
```

### Rationale

**Primary drivers:**

- **Parallel Development**: Multiple developers/features can work simultaneously without conflicts
- **Environment Isolation**: Each worktree is completely independent filesystem-wise
- **Shared State**: Database changes available immediately across all development environments
- **Zero Downtime Switching**: No need to restart or reconfigure when switching contexts
- **Port Management**: Automatic port detection prevents development conflicts

**Technical benefits:**

- Clean separation of development contexts while maintaining shared database
- No git branch switching delays or potential uncommitted work loss
- Automatic conflict resolution for shared resources (ports, database)
- Support for concurrent development without workflow disruption
- Easy testing of cross-feature integration scenarios

### Alternatives Considered

- **Option A: Traditional branch switching** - Rejected due to database state loss and development conflicts
- **Option B: Containerized development** - Rejected as over-complex for current team size and requirements
- **Option C: Separate database per branch** - Rejected due to data inconsistency and integration testing complexity
- **Option D: Feature flags in single environment** - Rejected due to complexity and potential for feature interference

### Consequences

**Positive:**

- ✅ **Parallel Development**: Multiple team members can work simultaneously without blocking
- ✅ **Environment Stability**: Each worktree maintains its own filesystem state
- ✅ **Shared Database Benefits**: All environments see latest schema and seed data immediately
- ✅ **Port Conflict Resolution**: Automatic port detection eliminates development friction
- ✅ **Zero Context Switching Cost**: No branch switching delays or git stash requirements
- ✅ **Integration Testing**: Easy cross-feature testing with shared database state

**Negative:**

- ➖ **Disk Space**: Multiple worktrees consume more disk space than single checkout
- ➖ **Complexity**: Additional setup required for new developers unfamiliar with worktrees
- ➖ **Database Contention**: Potential for database locking conflicts during heavy development
- ➖ **Resource Usage**: Multiple development services consume more system resources

**Neutral:**

- 🔄 **Git Learning Curve**: Team needs understanding of worktree commands and workflow
- 🔄 **IDE Configuration**: Each worktree may require separate IDE workspace configuration
- 🔄 **Cleanup Overhead**: Worktrees require explicit cleanup when branches are merged/deleted

### Implementation Notes

**Database Path Detection Logic:**
```python
def get_database_path():
    """Automatically detect if running in worktree and find shared database."""
    current = Path.cwd()
    while current != current.parent:
        git_path = current / ".git"
        if git_path.is_file():  # Worktree detected
            gitdir_content = git_path.read_text().strip()
            if gitdir_content.startswith("gitdir: "):
                gitdir = gitdir_content[8:]
                git_dir = Path(gitdir)
                main_repo_root = git_dir.parent.parent
                return f"sqlite:///{main_repo_root}/instance/crm.db"
```

**Port Management Strategy:**
- Auto-detect starting from port 5050
- Fall back through range 5050-5060 for CRM service
- Separate ranges for different service types (chatbot: 8020-8070)
- Clear error messaging when no ports available

**Development Workflow:**
1. Create worktree: `git worktree add .worktrees/feature-name feature-branch`
2. Navigate to worktree: `cd .worktrees/feature-name`
3. Start development: `./run.sh` (auto-detects port and database)
4. Develop in isolation with shared database access
5. Test integration: Database changes visible across all worktrees
6. Merge and cleanup: Remove worktree when feature complete

**Service Architecture:**
- **CRM Service**: Flask app with SQLAlchemy, auto-port detection
- **Chatbot Service**: FastAPI app with WebSocket, separate port range
- **Shared Database**: SQLite instance in main repo `/instance/` directory
- **Static Assets**: Each worktree maintains independent static file cache

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 13-09-25-09h-30m-00s | Current | ADR review | Initial creation | Document worktree strategy | Establish development workflow standards |

---

**Impact Assessment:** High - This is a foundational development workflow decision affecting all team members.

**Review Required:** Yes - New team members must understand worktree workflow and setup process.

**Next Steps:**
1. Create team documentation for worktree setup and workflows
2. Establish cleanup procedures for merged branches
3. Monitor resource usage and database contention as team scales
4. Consider automation scripts for common worktree operations