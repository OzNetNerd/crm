"""
Consolidated Modal Configuration System

Unified configuration for both create and detail/edit modals
to eliminate duplication and provide consistent modal behavior.
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

# Company Detail Modal Configuration
COMPANY_DETAIL_CONFIG = {
    "title": "Company Details",
    "title_singular": "Company",
    "show_notes": True,
    "default_values": {
        "name": "",
        "industry": "",
        "size": "",
        "website": "",
        "phone": "",
        "address": ""
    },
    "fields": [
        {
            "type": "text",
            "name": "name",
            "label": "Company Name",
            "placeholder": "Company name"
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
                    "placeholder": "https://company.com"
                },
                {
                    "type": "text",
                    "name": "phone",
                    "label": "Phone",
                    "placeholder": "Company phone number"
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

# Stakeholder Detail Modal Configuration
STAKEHOLDER_DETAIL_CONFIG = {
    "title": "Stakeholder Details",
    "show_notes": True,
    "default_values": {
        "name": "",
        "email": "",
        "phone": "",
        "job_title": "",
        "company_id": ""
    },
    "fields": [
        {
            "type": "text",
            "name": "name",
            "label": "Full Name",
            "placeholder": "Stakeholder name"
        },
        {
            "type": "grid",
            "columns": 2,
            "fields": [
                {
                    "type": "text",
                    "name": "email",
                    "label": "Email",
                    "placeholder": "Stakeholder email"
                },
                {
                    "type": "text",
                    "name": "phone",
                    "label": "Phone",
                    "placeholder": "Stakeholder phone number"
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

# Opportunity Detail Modal Configuration
OPPORTUNITY_DETAIL_CONFIG = {
    "title": "Opportunity Details",
    "show_notes": True,
    "default_values": {
        "name": "",
        "value": "",
        "stage": "",
        "probability": "",
        "expected_close_date": "",
        "company_id": ""
    },
    "fields": [
        {
            "type": "text",
            "name": "name",
            "label": "Opportunity Name",
            "placeholder": "Opportunity name"
        },
        {
            "type": "grid",
            "columns": 2,
            "fields": [
                {
                    "type": "text",
                    "name": "value",
                    "label": "Value ($)",
                    "placeholder": "Opportunity value"
                },
                {
                    "type": "select",
                    "name": "stage",
                    "label": "Stage",
                    "options": [
                        {"value": "", "label": "Select stage"},
                        {"value": "lead", "label": "Lead"},
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
                    "type": "text",
                    "name": "probability",
                    "label": "Probability (%)",
                    "placeholder": "0-100"
                },
                {
                    "type": "date",
                    "name": "expected_close_date",
                    "label": "Expected Close Date"
                }
            ]
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

# Task Detail Modal Configuration
TASK_DETAIL_CONFIG = {
    "title": "Task Details",
    "default_values": {
        "description": "",
        "due_date": "",
        "priority": "medium",
        "next_step_type": "",
        "status": "pending"
    },
    "tabs": [
        {
            "key": "details",
            "label": "Details"
        },
        {
            "key": "subtasks",
            "label": "Sub-tasks",
            "condition": "task.task_type === 'parent'",
            "badge": "task.child_tasks ? task.child_tasks.length : 0"
        },
        {
            "key": "notes",
            "label": "Notes",
            "badge": "notes.length"
        }
    ],
    "fields": [
        {
            "type": "textarea",
            "name": "description",
            "label": "Description",
            "rows": 3
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
                    "type": "select",
                    "name": "status",
                    "label": "Status",
                    "options": [
                        {"value": "pending", "label": "Pending"},
                        {"value": "in_progress", "label": "In Progress"},
                        {"value": "complete", "label": "Complete"}
                    ]
                }
            ]
        },
        {
            "type": "grid",
            "columns": 2,
            "fields": [
                {
                    "type": "date",
                    "name": "due_date",
                    "label": "Due Date"
                },
                {
                    "type": "text",
                    "name": "next_step_type",
                    "label": "Next Step Type",
                    "placeholder": "e.g., call, email, meeting"
                }
            ]
        }
    ]
}

# Configuration registries for easy access
MODAL_CONFIGS = {
    'company': COMPANY_CREATE_CONFIG,
    'stakeholder': STAKEHOLDER_CREATE_CONFIG,
    'opportunity': OPPORTUNITY_CREATE_CONFIG,
    'task': TASK_CREATE_CONFIG
}

DETAIL_MODAL_CONFIGS = {
    'task': TASK_DETAIL_CONFIG,
    'stakeholder': STAKEHOLDER_DETAIL_CONFIG,
    'company': COMPANY_DETAIL_CONFIG,
    'opportunity': OPPORTUNITY_DETAIL_CONFIG
}

def get_modal_config(entity_type: str):
    """Get modal configuration for a specific entity type"""
    return MODAL_CONFIGS.get(entity_type)

def get_detail_modal_config(entity_type: str):
    """Get detail modal configuration for a specific entity type"""
    return DETAIL_MODAL_CONFIGS.get(entity_type)