import re
from markupsafe import Markup


def style_task_description(description):
    """
    Parse task descriptions and apply appropriate styling to different components.
    
    Handles patterns like:
    - "Draft contract terms for Training Program - GreenEnergy Solutions"
    - "Draft contract terms for GreenEnergy Solutions"
    - "Schedule meeting with John Smith"
    
    Returns HTML with appropriate color classes applied.
    """
    if not description:
        return ""
    
    # Pattern to match common task formats with opportunity and company
    # e.g., "Draft contract terms for Training Program - GreenEnergy Solutions"
    opportunity_company_pattern = r'^(.+?)\s+for\s+(.+?)\s+-\s+(.+)$'
    
    # Pattern to match tasks with just entity name
    # e.g., "Draft contract terms for GreenEnergy Solutions"
    entity_pattern = r'^(.+?)\s+for\s+(.+)$'
    
    # Pattern to match tasks with "with" keyword (usually contacts)
    # e.g., "Schedule meeting with John Smith"  
    contact_pattern = r'^(.+?)\s+with\s+(.+)$'
    
    # Try opportunity + company pattern first
    match = re.match(opportunity_company_pattern, description)
    if match:
        action = match.group(1)
        opportunity_name = match.group(2)
        company_name = match.group(3)
        
        return Markup(f'{action} for <span class="text-opportunity-name">{opportunity_name}</span> - <span class="text-company-name">{company_name}</span>')
    
    # Try entity pattern (could be company or opportunity)
    match = re.match(entity_pattern, description)
    if match:
        action = match.group(1)
        entity_name = match.group(2)
        
        # Heuristic: if entity name has multiple words and looks like a company name, style as company
        # Otherwise, assume it's an opportunity name
        if any(word in entity_name.lower() for word in ['solutions', 'corp', 'inc', 'ltd', 'llc', 'company', 'technologies']):
            return Markup(f'{action} for <span class="text-company-name">{entity_name}</span>')
        else:
            return Markup(f'{action} for <span class="text-opportunity-name">{entity_name}</span>')
    
    # Try contact pattern
    match = re.match(contact_pattern, description)
    if match:
        action = match.group(1)
        contact_name = match.group(2)
        
        return Markup(f'{action} with <span class="text-stakeholder-name">{contact_name}</span>')
    
    # If no pattern matches, return the original description
    return description


def register_template_filters(app):
    """Register all custom template filters with the Flask app."""
    app.jinja_env.filters['style_task_description'] = style_task_description