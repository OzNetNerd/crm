# CRM Application - Claude Code Instructions

## 🚨 CRITICAL: MANDATORY DUPLICATE DETECTION BEFORE ANY IMPLEMENTATION

**YOU MUST CHECK FOR DUPLICATES BEFORE WRITING ANY CODE**

### Before Creating ANY New Function/Pattern:

1. **SEARCH for existing implementations:**
   ```bash
   # For JavaScript functions
   grep -r "function.*selectEntity\|selectItem\|selectChoice" --include="*.js"

   # For Python functions
   grep -r "def.*search\|def.*select\|def.*filter" --include="*.py"

   # For API endpoints
   grep -r "@.*route\|@app\." --include="*.py"
   ```

2. **VERIFY no similar patterns exist:**
   - If you find ANYTHING similar, you MUST extend it, not create new
   - Document WHY existing patterns don't work if creating new

3. **RUN compliance check (when in ClawDebt):**
   ```bash
   /compliance-check javascript  # or python, all, etc.
   ```

### ❌ NEVER Create These Duplicates:
- `selectEntity()` AND `selectChoice()` - use ONE universal function
- Multiple event handlers for same action
- Similar API endpoints with slight variations
- Parallel validation systems
- Multiple search implementations

### ✅ ALWAYS:
- Extend existing patterns with parameters
- Use single source of truth
- Consolidate similar functionality
- Check ADR-009 for Zero Duplicate Systems Policy

**BLOCKING: Code with duplicates will be rejected**

## Running the Application

### Auto Port Detection (Recommended)

```bash
./run.sh
```

- Automatically finds the first free port starting from 5000
- Displays the URL Claude should use: `http://127.0.0.1:{port}`
- Perfect for multiple worktrees - no port conflicts!

### Manual Port Selection

```bash
python3 main.py --port 5002
```

- Use when you need a specific port
- If port is busy, will show helpful error message

## For Claude Code

When starting the CRM application:

1. Run `./run.sh` (recommended - auto-detects port)
2. Look for the output: `🚀 Starting CRM application on http://127.0.0.1:{port}`
3. Use that URL to access the application

## Features

- **Automatic Port Detection**: No more port conflicts between worktrees
- **Smart Error Messages**: Clear guidance when ports are busy  
- **Flexible**: Can still specify ports manually when needed
- **Claude-Friendly**: Clear URL output for automated tools

## Development Workflow

### Multiple Worktrees

Each worktree can run simultaneously:

```bash
# Worktree 1
./run.sh  # Uses port 5000

# Worktree 2  
./run.sh  # Uses port 5001 (auto-detected)

# Worktree 3
./run.sh  # Uses port 5002 (auto-detected)
```

### Testing Specific Ports

```bash
python3 main.py --port 8080  # Force specific port
```
