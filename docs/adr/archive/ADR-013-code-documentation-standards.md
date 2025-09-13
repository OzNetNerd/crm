# Architecture Decision Record (ADR)

## ADR-013: Code Documentation and Style Standards

**Status:** Accepted  
**Date:** 13-09-25-13h-00m-00s  
**Session:** /home/will/.claude/projects/-home-will-code-crm--worktrees-adr-check/afc3ed2f-fdb0-4480-b02c-ea658e7d7589.jsonl  
**Todo:** /home/will/.claude/todos/afc3ed2f-fdb0-4480-b02c-ea658e7d7589-agent-*.json  
**Deciders:** Will Robinson, Development Team

### Context

The CRM codebase lacks comprehensive documentation standards across different technologies and file types. Current issues:

- **Inconsistent Python Documentation**: Some functions have docstrings, others don't; varying formats and quality
- **Missing Type Annotations**: Python functions lack type hints, reducing IDE support and code clarity
- **Undocumented Bash Scripts**: Shell scripts lack comments explaining purpose and usage
- **Jinja Template Documentation**: Templates have no documentation explaining purpose, context, or dependencies
- **JavaScript Documentation**: Frontend code lacks JSDoc comments and function documentation
- **Code Style Enforcement**: No formal standards for comment styles, annotation requirements, or documentation completeness

The lack of documentation standards creates maintenance burden, reduces code understanding, and hinders team collaboration.

### Decision

**We will implement comprehensive documentation standards across all code types with automated enforcement:**

1. **Google-Style Python Docstrings**: Mandatory for all functions, classes, and modules
2. **Python Type Annotations**: Required for all function parameters and return values
3. **Bash Script Documentation**: Header comments and inline explanations for complex logic
4. **Jinja Template Documentation**: Purpose, context variables, and macro documentation
5. **JSDoc JavaScript Standards**: Function documentation for all non-trivial JavaScript
6. **Automated Enforcement**: Pre-commit hooks and CI checks for documentation compliance

**Documentation Hierarchy:**
```
Module Level → Class Level → Function Level → Inline Comments
     ↓             ↓             ↓              ↓
Purpose &     Responsibility  Parameters &   Complex Logic
Architecture      & Usage      Returns       Explanation
```

### Rationale

**Primary drivers:**

- **Code Maintainability**: Clear documentation reduces time to understand and modify code
- **Team Collaboration**: Consistent standards enable effective knowledge sharing
- **IDE Support**: Type annotations improve autocomplete, error detection, and refactoring
- **Onboarding Efficiency**: New developers can understand codebase faster with comprehensive documentation
- **Technical Debt Prevention**: Well-documented code is less likely to become legacy technical debt

**Technical benefits:**

- Type annotations enable static analysis and catch bugs before runtime
- Standardized docstrings support automated documentation generation
- Consistent comment styles improve code readability across entire codebase
- Template documentation clarifies context dependencies and usage patterns
- JavaScript documentation enables better frontend debugging and maintenance

### Alternatives Considered

- **Option A: Optional documentation** - Rejected due to inconsistent adoption and maintenance burden
- **Option B: Generated documentation only** - Rejected as auto-generated docs lack context and usage examples
- **Option C: Wiki-based documentation** - Rejected due to code-documentation synchronization issues
- **Option D: Minimal comment approach** - Rejected due to code complexity and team size requirements

### Consequences

**Positive:**

- ✅ **Enhanced Code Understanding**: Clear documentation reduces time to understand codebase
- ✅ **Improved IDE Support**: Type annotations enable better autocomplete and error detection
- ✅ **Faster Onboarding**: New team members can understand code patterns and usage quickly
- ✅ **Better Debugging**: Well-documented code provides context for troubleshooting issues
- ✅ **Reduced Technical Debt**: Documentation prevents code from becoming unmaintainable legacy
- ✅ **Team Knowledge Sharing**: Consistent standards enable effective collaboration

**Negative:**

- ➖ **Development Overhead**: Writing documentation adds time to development process
- ➖ **Maintenance Burden**: Documentation must be kept synchronized with code changes
- ➖ **Enforcement Complexity**: Need tooling and processes to ensure compliance
- ➖ **Initial Migration**: Existing codebase requires documentation updates

**Neutral:**

- 🔄 **Learning Curve**: Team needs to learn documentation standards and best practices
- 🔄 **Tool Configuration**: Need to set up linting and enforcement tools
- 🔄 **Code Review Focus**: Reviews must include documentation quality assessment

### Implementation Notes

**Python Documentation Standards:**

```python
# app/models/company.py
from typing import List, Optional, Dict, Any
from datetime import datetime

class Company(BaseModel):
    """
    Represents a company entity in the CRM system.
    
    A company can have multiple contacts, opportunities, and stakeholder relationships.
    Companies are the primary organizational unit for business relationship management.
    
    Attributes:
        id: Unique identifier for the company
        name: Company legal or business name
        industry: Industry classification
        size: Company size category (startup, small, medium, large, enterprise)
        created_at: Timestamp of company creation
        
    Example:
        >>> company = Company(name="TechCorp Inc", industry="Software")
        >>> company.get_active_opportunities()
        [<Opportunity 1>, <Opportunity 2>]
    """
    
    def get_active_opportunities(self, status_filter: Optional[str] = None) -> List[Opportunity]:
        """
        Retrieve all active opportunities associated with this company.
        
        Args:
            status_filter: Optional status to filter opportunities by.
                         Valid values: 'qualification', 'proposal', 'negotiation'
                         
        Returns:
            List of Opportunity objects matching the criteria.
            Empty list if no opportunities found.
            
        Raises:
            ValueError: If status_filter contains invalid status value.
            DatabaseError: If database connection fails.
            
        Example:
            >>> opportunities = company.get_active_opportunities(status_filter='proposal')
            >>> len(opportunities)
            3
        """
        if status_filter and status_filter not in ['qualification', 'proposal', 'negotiation']:
            raise ValueError(f"Invalid status filter: {status_filter}")
            
        query = self.opportunities.filter(Opportunity.is_active == True)
        if status_filter:
            query = query.filter(Opportunity.status == status_filter)
            
        return query.all()
    
    def calculate_lifetime_value(self) -> float:
        """
        Calculate total lifetime value from all closed opportunities.
        
        Returns:
            Total monetary value of all won opportunities for this company.
            Returns 0.0 if no won opportunities exist.
        """
        won_opportunities = self.opportunities.filter(
            Opportunity.status == 'won'
        ).all()
        
        return sum(opp.value for opp in won_opportunities)
```

**Bash Script Documentation Standards:**

```bash
#!/bin/bash
#
# CRM Application Startup Script
#
# Purpose: Start CRM and Chatbot services with automatic port detection
# Usage: ./run.sh [--crm-port PORT] [--chatbot-port PORT]
# Dependencies: Python 3.8+, Node.js (for chatbot), nc (netcat)
#
# Author: Development Team
# Created: 2025-09-13
# Last Modified: 2025-09-13
#
# Exit Codes:
#   0 - Success
#   1 - Port detection failure
#   2 - Service startup failure
#   3 - Dependency check failure

set -euo pipefail  # Enable strict error handling

# Global configuration
readonly DEFAULT_CRM_PORT=5050
readonly DEFAULT_CHATBOT_PORT=8020
readonly MAX_PORT_ATTEMPTS=10

# Find the first available port starting from a given port
# Arguments:
#   $1 - Starting port number
#   $2 - Maximum attempts (optional, default: 10)
# Returns:
#   Prints first available port number
#   Exits with code 1 if no port found
find_free_port() {
    local start_port=$1
    local max_attempts=${2:-$MAX_PORT_ATTEMPTS}
    
    # Validate port number is in valid range
    if [[ $start_port -lt 1024 || $start_port -gt 65535 ]]; then
        echo "Error: Port $start_port outside valid range (1024-65535)" >&2
        exit 1
    fi
    
    # Search for available port
    for ((port=start_port; port<start_port+max_attempts; port++)); do
        if ! timeout 1 nc -z localhost $port 2>/dev/null; then
            echo $port
            return 0
        fi
    done
    
    echo "Error: No free port found in range $start_port-$((start_port+max_attempts-1))" >&2
    exit 1
}

# Cleanup background processes on script exit
# Called automatically by trap on SIGINT and SIGTERM
cleanup() {
    echo "🛑 Shutting down services..."
    
    # Stop chatbot service if running
    if [[ -n "${CHATBOT_PID:-}" ]]; then
        if kill $CHATBOT_PID 2>/dev/null; then
            echo "   Stopped chatbot service (PID: $CHATBOT_PID)"
        fi
    fi
    
    echo "   Cleanup completed"
    exit 0
}
```

**Jinja Template Documentation Standards:**

```jinja2
{#
    Company Detail Page Template
    
    Purpose: Display comprehensive company information with related entities
    
    Context Variables:
        company (Company): The company object being displayed
        opportunities (List[Opportunity]): Active opportunities for this company
        contacts (List[Contact]): Company contacts
        user (User): Current authenticated user
        can_edit (bool): Whether user can edit company information
        
    Macros Used:
        - entity_header: Displays entity name, status, and action buttons
        - opportunities_table: Renders opportunities in tabular format
        - contact_list: Shows contact information with communication history
        
    Dependencies:
        - CSS: entities.css for company-specific styling
        - JS: company-detail.js for interactive functionality
        - API: /api/companies/{id}/* endpoints for AJAX operations
        
    Example Usage:
        {% include 'entities/company_detail.html' %}
        
    Author: Development Team
    Created: 2025-09-13
    Last Modified: 2025-09-13
#}

{% extends "base.html" %}
{% from "entities/company_macros.html" import entity_header, opportunities_table %}

{% block title %}{{ company.name }} - Company Details{% endblock %}

{% block content %}
<div class="company-detail-container">
    {# 
        Company Header Section
        Displays company name, industry, and primary action buttons
        Uses dynamic CSS classes: company-header, company-{{company.status}}
    #}
    {{ entity_header(
        entity=company,
        entity_type='company',
        can_edit=can_edit,
        show_status=true
    ) }}
    
    {# Company Information Cards #}
    <div class="company-info-grid">
        {# Basic company information #}
        <div class="company-card company-basic-info">
            <h3>Company Information</h3>
            {# Display key company fields with dynamic styling #}
            <div class="company-field company-industry">
                <strong>Industry:</strong> {{ company.industry or 'Not specified' }}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**JavaScript Documentation Standards:**

```javascript
/**
 * Company Management Module
 * 
 * Handles client-side interactions for company pages including
 * AJAX operations, form validation, and dynamic UI updates.
 * 
 * Dependencies:
 * - jQuery 3.6+
 * - Bootstrap 5.x for modal functionality
 * - Custom logger.js for structured logging
 * 
 * @author Development Team
 * @since 2025-09-13
 * @version 1.0.0
 */

/**
 * Company detail page functionality
 * @namespace CompanyDetail
 */
const CompanyDetail = {
    /**
     * Initialize company detail page interactions
     * Sets up event listeners and loads initial data
     * 
     * @param {Object} config - Configuration object
     * @param {number} config.companyId - ID of the company being displayed
     * @param {boolean} config.canEdit - Whether user can edit company
     * @param {string} config.apiBaseUrl - Base URL for API calls
     * 
     * @throws {Error} If companyId is not provided or invalid
     * 
     * @example
     * CompanyDetail.init({
     *     companyId: 123,
     *     canEdit: true,
     *     apiBaseUrl: '/api'
     * });
     */
    init: function(config) {
        if (!config.companyId || isNaN(config.companyId)) {
            throw new Error('Valid companyId is required for CompanyDetail initialization');
        }
        
        this.config = config;
        this.setupEventListeners();
        this.loadOpportunities();
        
        logger.info('CompanyDetail initialized', {
            company_id: config.companyId,
            can_edit: config.canEdit
        });
    },
    
    /**
     * Load company opportunities via AJAX
     * Updates the opportunities table with fresh data from server
     * 
     * @async
     * @returns {Promise<void>} Resolves when opportunities are loaded
     * @throws {Error} If API request fails
     * 
     * @private
     */
    loadOpportunities: async function() {
        try {
            const response = await fetch(
                `${this.config.apiBaseUrl}/companies/${this.config.companyId}/opportunities`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Request-ID': logger.requestId
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const opportunities = await response.json();
            this.updateOpportunitiesTable(opportunities);
            
            logger.info('Opportunities loaded successfully', {
                company_id: this.config.companyId,
                opportunity_count: opportunities.length
            });
            
        } catch (error) {
            logger.error('Failed to load opportunities', {
                company_id: this.config.companyId,
                error_message: error.message
            });
            
            this.showErrorMessage('Unable to load opportunities. Please refresh the page.');
            throw error;
        }
    }
};
```

**Type Annotation Requirements:**

- All function parameters must have type annotations
- All return values must have type annotations  
- Use `typing` module for complex types (`List`, `Dict`, `Optional`, `Union`)
- Use `Any` sparingly and document why it's necessary
- Import type annotations at module level

**Enforcement Mechanisms:**

```python
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-docstrings
        name: Check Python docstrings
        entry: python scripts/check_docstrings.py
        language: python
        files: \.py$
        
      - id: check-type-annotations
        name: Check type annotations
        entry: mypy
        language: python
        files: \.py$
        
      - id: check-bash-comments
        name: Check bash script documentation
        entry: python scripts/check_bash_docs.py
        language: python
        files: \.sh$
```

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 13-09-25-13h-00m-00s | afc3ed2f-fdb0-4480-b02c-ea658e7d7589.jsonl | ADR gap analysis | Initial creation | Document code documentation standards | Establish comprehensive documentation requirements |

---

**Impact Assessment:** High - This affects all code and establishes fundamental development quality standards.

**Review Required:** Mandatory - All team members must understand documentation standards and enforcement.

**Next Steps:**
1. Create documentation enforcement scripts and pre-commit hooks
2. Update existing codebase to meet documentation standards
3. Integrate documentation checks into CI/CD pipeline
4. Create team training materials for documentation best practices
5. Establish code review checklist including documentation quality