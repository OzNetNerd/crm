"""
Modal Configuration System
Replaces template-based modal configs with Python configurations for better maintainability
"""

# Company Create Modal Configuration
COMPANY_CREATE_CONFIG = {
    "title": "Create New Company",
    "save_text": "Save",
    "api_endpoint": "/companies/create",
    "error_message": "Error creating company",
    "default_values": {
        "name": "",
        "industry": "",
        "size": "",
        "website": "",
        "phone": "",
        "address": ""
    },
    "validations": [
        {
            "field": "name",
            "required": True,
            "message": "Company name is required"
        }
    ],
    "fields": [
        {
            "type": "text",
            "name": "name",
            "label": "Company Name",
            "placeholder": "Company name",
            "required": True
        },
        {
            "type": "grid",
            "columns": 2,
            "fields": [
                {
                    "type": "select",
                    "name": "industry",
                    "label": "Industry",
                    "options": [
                        {"value": "", "label": "Select industry"},
                        {"value": "technology", "label": "Technology"},
                        {"value": "finance", "label": "Finance"},
                        {"value": "healthcare", "label": "Healthcare"},
                        {"value": "manufacturing", "label": "Manufacturing"},
                        {"value": "retail", "label": "Retail"},
                        {"value": "education", "label": "Education"},
                        {"value": "consulting", "label": "Consulting"},
                        {"value": "other", "label": "Other"}
                    ]
                },
                {
                    "type": "select",
                    "name": "size",
                    "label": "Company Size",
                    "options": [
                        {"value": "", "label": "Select size"},
                        {"value": "startup", "label": "Startup (1-10)"},
                        {"value": "small", "label": "Small (11-50)"},
                        {"value": "medium", "label": "Medium (51-200)"},
                        {"value": "large", "label": "Large (201-1000)"},
                        {"value": "enterprise", "label": "Enterprise (1000+)"}
                    ]
                }
            ]
        },
        {
            "type": "grid",
            "columns": 2,
            "fields": [
                {
                    "type": "text",
                    "name": "website",
                    "label": "Website",
                    "placeholder": "https://company.com",
                    "input_type": "url"
                },
                {
                    "type": "text",
                    "name": "phone",
                    "label": "Phone",
                    "placeholder": "Company phone number",
                    "input_type": "tel"
                }
            ]
        },
        {
            "type": "textarea",
            "name": "address",
            "label": "Address",
            "rows": 2,
            "placeholder": "Company address"
        }
    ]
}

# Stakeholder Create Modal Configuration
STAKEHOLDER_CREATE_CONFIG = {
    "title": "Create New Stakeholder",
    "save_text": "Save",
    "api_endpoint": "/api/stakeholders",
    "error_message": "Error creating stakeholder",
    "default_values": {
        "name": "",
        "email": "",
        "phone": "",
        "job_title": ""
    },
    "validations": [
        {
            "field": "name",
            "required": True,
            "message": "Name is required"
        }
    ],
    "fields": [
        {
            "type": "text",
            "name": "name",
            "label": "Full Name",
            "placeholder": "Stakeholder name",
            "required": True
        },
        {
            "type": "grid",
            "columns": 2,
            "fields": [
                {
                    "type": "text",
                    "name": "email",
                    "label": "Email",
                    "placeholder": "contact@company.com",
                    "input_type": "email"
                },
                {
                    "type": "text",
                    "name": "phone",
                    "label": "Phone",
                    "placeholder": "Phone number",
                    "input_type": "tel"
                }
            ]
        },
        {
            "type": "text",
            "name": "job_title",
            "label": "Job Title",
            "placeholder": "Job title or role"
        }
    ]
}

# Opportunity Create Modal Configuration
OPPORTUNITY_CREATE_CONFIG = {
    "title": "Create New Opportunity",
    "save_text": "Save",
    "api_endpoint": "/opportunities/create",
    "error_message": "Error creating opportunity",
    "default_values": {
        "name": "",
        "value": "",
        "stage": "prospect",
        "probability": 25,
        "expected_close_date": "",
        "company_id": None,
        "company_name": ""
    },
    "additional_fields": {
        "selectedAccountTeam": [],
        "selectedStakeholders": []
    },
    "validations": [
        {
            "field": "name",
            "required": True,
            "message": "Opportunity name is required"
        },
        {
            "field": "value",
            "required": True,
            "message": "Value is required"
        },
        {
            "field": "company_id",
            "required": True,
            "message": "Company is required"
        }
    ],
    "fields": [
        {
            "type": "text",
            "name": "name",
            "label": "Opportunity Name",
            "placeholder": "Opportunity name",
            "required": True
        },
        {
            "type": "company_autocomplete",
            "name": "company_id",
            "label": "Company",
            "placeholder": "Select company",
            "required": True
        },
        {
            "type": "grid",
            "columns": 2,
            "fields": [
                {
                    "type": "number",
                    "name": "value",
                    "label": "Value ($)",
                    "placeholder": "10000",
                    "required": True
                },
                {
                    "type": "select",
                    "name": "stage",
                    "label": "Stage",
                    "options": [
                        {"value": "prospect", "label": "Prospect"},
                        {"value": "qualified", "label": "Qualified"},
                        {"value": "proposal", "label": "Proposal"},
                        {"value": "negotiation", "label": "Negotiation"},
                        {"value": "closed_won", "label": "Closed Won"},
                        {"value": "closed_lost", "label": "Closed Lost"}
                    ]
                }
            ]
        },
        {
            "type": "grid",
            "columns": 2,
            "fields": [
                {
                    "type": "number",
                    "name": "probability",
                    "label": "Probability (%)",
                    "placeholder": "25",
                    "min": 0,
                    "max": 100
                },
                {
                    "type": "date",
                    "name": "expected_close_date",
                    "label": "Expected Close Date"
                }
            ]
        },
        {
            "type": "account_team_selector",
            "name": "account_team_members",
            "label": "Account Team Members (Optional)"
        },
        {
            "type": "stakeholder_selector", 
            "name": "stakeholders",
            "label": "Stakeholders (Optional)"
        }
    ]
}

# Task Create Modal Configuration
TASK_CREATE_CONFIG = {
    "title": "Create New Task",
    "save_text": "Save",
    "api_endpoint": "/tasks/create",
    "error_message": "Error creating task",
    "default_values": {
        "description": "",
        "due_date": "",
        "priority": "medium",
        "next_step_type": ""
    },
    "validations": [
        {
            "field": "description",
            "required": True,
            "message": "Task description is required"
        }
    ],
    "fields": [
        {
            "type": "textarea",
            "name": "description",
            "label": "Description",
            "placeholder": "Task description",
            "rows": 3,
            "required": True
        },
        {
            "type": "grid",
            "columns": 2,
            "fields": [
                {
                    "type": "select",
                    "name": "priority",
                    "label": "Priority",
                    "options": [
                        {"value": "low", "label": "Low"},
                        {"value": "medium", "label": "Medium"},
                        {"value": "high", "label": "High"}
                    ]
                },
                {
                    "type": "date",
                    "name": "due_date",
                    "label": "Due Date"
                }
            ]
        },
        {
            "type": "text",
            "name": "next_step_type",
            "label": "Next Step Type",
            "placeholder": "e.g., call, email, meeting"
        }
    ]
}

# Configuration registry for easy access
MODAL_CONFIGS = {
    'company': COMPANY_CREATE_CONFIG,
    'stakeholder': STAKEHOLDER_CREATE_CONFIG,
    'opportunity': OPPORTUNITY_CREATE_CONFIG,
    'task': TASK_CREATE_CONFIG
}

def get_modal_config(entity_type: str):
    """Get modal configuration for a specific entity type"""
    return MODAL_CONFIGS.get(entity_type)