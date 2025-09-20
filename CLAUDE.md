# CRM Application - Claude Code Instructions

## 🚨 CRITICAL: FILE LOCATION VERIFICATION

**ALWAYS VERIFY FILE PATHS BEFORE CREATING FILES**

### Static File Location Rules:
1. **JavaScript files:** `/app/static/js/` NOT `/static/js/`
2. **CSS files:** `/app/static/css/` NOT `/static/css/`
3. **Always check existing patterns:** `ls -la app/static/`
4. **Test in browser:** Open developer console to verify files load without 404 errors

### Before Creating ANY Static File:
```bash
# MANDATORY: Check the correct path structure
ls -la app/static/
ls -la app/static/js/
ls -la app/static/css/

# Find similar files to understand the pattern
find . -name "*.js" -path "*/static/*" | head -5
```

**BLOCKING: Files in wrong locations will cause 404 errors**

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

## 🔍 VERIFICATION-FIRST DEVELOPMENT

**NEVER ASSUME - ALWAYS VERIFY**

### Before ANY Implementation:

1. **Verify Database Relationships:**
   ```bash
   # Check if a relationship exists BEFORE using it
   grep -r "relationship(" app/models/company.py
   grep -r "account_team" app/models/

   # Verify actual model attributes
   python -c "from app.models import Company; print(dir(Company))"
   ```

2. **Verify File Locations:**
   ```bash
   # NEVER assume file paths - always find them
   find . -name "*.db" -type f
   find . -name "seed*.py"
   ls -la instance/  # Check what actually exists
   ```

3. **Verify Code Patterns:**
   ```bash
   # Check if similar functions exist before creating new ones
   grep -r "def search" --include="*.py"
   grep -r "selectEntity" --include="*.js"
   ```

4. **Verify Configuration:**
   ```bash
   # Check actual configuration values
   grep -r "DATABASE" --include="*.py"
   cat .env 2>/dev/null || echo "No .env file"
   ```

### ❌ NEVER:
- Assume a relationship exists - CHECK FIRST
- Guess file locations - FIND THEM
- Create new patterns without checking for existing ones
- Make database assumptions - QUERY IT

### ✅ ALWAYS:
- Run verification commands BEFORE coding
- Show the user what you're checking
- Admit when something doesn't exist
- Ask for clarification instead of assuming

**ENFORCEMENT**: Code based on assumptions will fail. Verify first!

## 💾 DATABASE CHANGE WORKFLOW

**ALWAYS ASK THE USER BEFORE DATABASE CHANGES**

### Standard Database Change Process:

1. **ASK FIRST:**
   ```
   "I need to make database changes for [specific reason].
   Should I rebuild the database with updated seed data?"
   ```

2. **If Approved, Use Rebuild Approach:**
   ```bash
   # 1. Verify locations
   ls -la instance/crm.db
   ls -la seed_data.py

   # 2. Update seed_data.py with changes

   # 3. Rebuild database
   rm instance/crm.db
   python seed_data.py

   # 4. Verify success
   ls -la instance/crm.db
   ```

### Database Facts:
- **Location**: `instance/crm.db`
- **Seed File**: `seed_data.py`
- **Approach**: REBUILD, don't migrate (during development)

### ❌ NEVER:
- Use migrations without explicit permission
- Create virtual tables or views
- Modify database without asking
- Assume database structure

### ✅ ALWAYS:
- Ask user before ANY database changes
- Prefer rebuilding over migrating
- Update seed file for all changes
- Verify database works after rebuild

**BLOCKING: Unauthorized database changes will be rejected**
