# /compliance-check Enhancement Requirements for ClawDebt

## Purpose
Enhance the `/compliance-check` slash command in ClawDebt to detect and prevent duplicate systems, ensuring the 4 duplicate selection systems incident NEVER happens again.

## Implementation Location
`/home/will/code/ClawDebt/hooks/utils/javascript-compliance.sh`

## Required Enhancements

### 1. Duplicate Function Detection

Add these functions to `javascript-compliance.sh`:

```bash
# Duplicate detection functions
detect_duplicate_functions() {
    local current_file="$1"
    local -n violations_ref=$2
    local current_dir=$(dirname "$current_file")
    local project_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

    echo "  🔍 Checking for duplicate functions across codebase..."

    # Extract function names from current file
    local current_functions=()
    while IFS= read -r func_name; do
        if [[ -n "$func_name" ]]; then
            current_functions+=("$func_name")
        fi
    done < <(grep -oE '(function\s+[a-zA-Z_][a-zA-Z0-9_]*|window\.[a-zA-Z_][a-zA-Z0-9_]*\s*=|[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*function)' "$current_file" | \
             sed -E 's/function\s+//; s/window\.//; s/\s*=.*//; s/\s+//g' | sort -u)

    # Check each function against other JS files
    for func_name in "${current_functions[@]}"; do
        local duplicate_count=0
        local duplicate_files=()

        # Search for the same function name in other files
        while IFS= read -r other_file; do
            if [[ "$other_file" != "$current_file" ]]; then
                if grep -qE "(function\s+$func_name[^a-zA-Z0-9_]|window\.$func_name\s*=|$func_name\s*=\s*function)" "$other_file" 2>/dev/null; then
                    ((duplicate_count++))
                    duplicate_files+=("$other_file")
                fi
            fi
        done < <(find "$project_root" -name "*.js" -type f 2>/dev/null)

        if [[ $duplicate_count -gt 0 ]]; then
            violations_ref+=("CRITICAL DUPLICATE: Function '$func_name' exists in ${#duplicate_files[@]} other file(s): ${duplicate_files[*]}")
        fi
    done
}
```

### 2. Pattern Similarity Detection

```bash
# Detect similar selection patterns
detect_selection_patterns() {
    local file_path="$1"
    local -n violations_ref=$2

    echo "  🔍 Checking for duplicate selection patterns..."

    # Common selection pattern signatures
    local patterns=(
        "selectEntity|selectItem|selectChoice|selectOption"
        "data-entity-select|data-item-select|data-choice-select"
        "addEventListener.*click.*select"
        "onclick.*select[A-Z]"
    )

    for pattern in "${patterns[@]}"; do
        local matches=$(grep -cE "$pattern" "$file_path" 2>/dev/null || echo "0")
        if [[ $matches -gt 1 ]]; then
            violations_ref+=("WARNING: Multiple selection handlers detected ($matches occurrences of pattern: $pattern) - consolidate into single system")
        fi
    done

    # Check for both selectEntity AND selectChoice in same file
    if grep -q "selectEntity" "$file_path" && grep -q "selectChoice" "$file_path"; then
        violations_ref+=("CRITICAL: Both selectEntity() and selectChoice() in same file - these should be ONE function")
    fi
}
```

### 3. Event Handler Duplication Detection

```bash
# Detect duplicate event handlers
detect_duplicate_event_handlers() {
    local file_path="$1"
    local -n violations_ref=$2

    echo "  🔍 Checking for duplicate event handlers..."

    # Check for multiple click handlers on similar selectors
    local click_handlers=$(grep -c "addEventListener.*click" "$file_path" 2>/dev/null || echo "0")
    if [[ $click_handlers -gt 5 ]]; then
        violations_ref+=("WARNING: $click_handlers click event listeners - consider event delegation")
    fi

    # Check for both addEventListener and data-attributes for same purpose
    if grep -q "data-entity-select" "$file_path" && grep -q "addEventListener.*entity.*select" "$file_path"; then
        violations_ref+=("CRITICAL: Both data-attribute and addEventListener for entity selection - use ONE approach")
    fi
}
```

### 4. Python Duplicate Detection

For `python-compliance.sh`, add:

```bash
# Detect duplicate Python functions/methods
detect_duplicate_python_functions() {
    local current_file="$1"
    local -n violations_ref=$2
    local project_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

    echo "  🔍 Checking for duplicate Python functions..."

    # Extract function/method names
    local current_functions=()
    while IFS= read -r func_name; do
        if [[ -n "$func_name" ]]; then
            current_functions+=("$func_name")
        fi
    done < <(grep -oE '^\s*def\s+[a-zA-Z_][a-zA-Z0-9_]*' "$current_file" | \
             sed -E 's/^\s*def\s+//; s/\s+//g' | sort -u)

    # Check for duplicates in other Python files
    for func_name in "${current_functions[@]}"; do
        local duplicate_files=()
        while IFS= read -r other_file; do
            if [[ "$other_file" != "$current_file" ]]; then
                if grep -qE "^\s*def\s+$func_name\s*\(" "$other_file" 2>/dev/null; then
                    duplicate_files+=("$other_file")
                fi
            fi
        done < <(find "$project_root" -name "*.py" -type f 2>/dev/null)

        if [[ ${#duplicate_files[@]} -gt 0 ]]; then
            violations_ref+=("CRITICAL DUPLICATE: Function '$func_name' exists in: ${duplicate_files[*]}")
        fi
    done
}

# Detect similar API endpoints
detect_duplicate_endpoints() {
    local file_path="$1"
    local -n violations_ref=$2

    echo "  🔍 Checking for duplicate API endpoints..."

    # Extract route definitions
    local routes=$(grep -E "@.*\.route\(" "$file_path" | sed -E 's/.*route\("([^"]+)".*/\1/' | sort)

    # Check for similar routes
    while IFS= read -r route; do
        if [[ -n "$route" ]]; then
            # Look for routes that differ only by ID parameter
            local base_route=$(echo "$route" | sed -E 's/<[^>]+>//g; s/\/$//')
            local similar_count=$(echo "$routes" | grep -c "^$base_route" || echo "0")
            if [[ $similar_count -gt 2 ]]; then
                violations_ref+=("WARNING: Multiple similar routes for '$base_route' - consider consolidation")
            fi
        fi
    done <<< "$routes"
}
```

## Severity Levels

### CRITICAL (Block Commit)
- Exact duplicate function names across files
- Multiple implementations of same functionality (selectEntity + selectChoice)
- Duplicate API endpoints

### WARNING (Require Justification)
- Similar function patterns (>70% code similarity)
- Multiple event handlers for same purpose
- Excessive number of similar patterns

### NOTICE (Log for Review)
- Potential pattern overlap
- Similar naming conventions
- Related but not duplicate functionality

## Integration with ClawDebt

### Update `run_regex_compliance()` in `javascript-compliance.sh`:

```bash
run_regex_compliance() {
    local file_path="$1"
    local -n violations_ref=$2

    echo "  🔍 Running regex-based checks..."

    # Run duplicate detection FIRST (critical issues)
    detect_duplicate_functions "$file_path" violations_ref
    detect_selection_patterns "$file_path" violations_ref
    detect_duplicate_event_handlers "$file_path" violations_ref

    # Continue with existing checks...
    # [existing code]
}
```

## Expected Output

When duplicates are detected:

```
📜 JavaScript Compliance Check
===============================
Checking: app/static/js/app.js
  🔍 Checking for duplicate functions across codebase...
  🔍 Checking for duplicate selection patterns...
  🔍 Checking for duplicate event handlers...

❌ CRITICAL VIOLATIONS FOUND:
- CRITICAL DUPLICATE: Function 'selectEntity' exists in 1 other file(s): app/static/js/features/search-widget.js
- CRITICAL: Both data-attribute and addEventListener for entity selection - use ONE approach
- WARNING: Multiple selection handlers detected (4 occurrences) - consolidate into single system

🚨 BLOCKING: Cannot proceed with these duplicates. Fix required before commit.
```

## Testing the Enhancement

1. **Test duplicate function detection:**
   ```bash
   # Create test files with duplicate functions
   echo "function selectEntity() {}" > test1.js
   echo "function selectEntity() {}" > test2.js
   /compliance-check javascript
   # Should detect duplicate
   ```

2. **Test pattern detection:**
   ```bash
   # Create file with both selectEntity and selectChoice
   echo "function selectEntity() {} function selectChoice() {}" > test.js
   /compliance-check javascript
   # Should flag as needing consolidation
   ```

3. **Test event handler detection:**
   ```bash
   # Create file with multiple similar handlers
   echo "addEventListener('click', selectEntity)" > test.js
   echo "element.dataset.entitySelect = true" >> test.js
   /compliance-check javascript
   # Should detect both approaches
   ```

## Maintenance

This enhancement should be reviewed and updated when:
- New patterns emerge that could lead to duplication
- False positives occur that need refinement
- New file types need duplicate detection

## Success Criteria

✅ The 4 duplicate selection systems would have been caught immediately
✅ Developers cannot commit code with CRITICAL duplicates
✅ Clear guidance on consolidating similar patterns
✅ Fast detection (< 2 seconds for typical codebase)