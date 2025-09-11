"""
Detail Modal Configuration System
Configuration for entity detail/edit modals
"""

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

# Configuration registry for easy access
DETAIL_MODAL_CONFIGS = {
    'task': TASK_DETAIL_CONFIG,
    'stakeholder': STAKEHOLDER_DETAIL_CONFIG,
    'company': COMPANY_DETAIL_CONFIG,
    'opportunity': OPPORTUNITY_DETAIL_CONFIG
}

def get_detail_modal_config(entity_type: str):
    """Get detail modal configuration for a specific entity type"""
    return DETAIL_MODAL_CONFIGS.get(entity_type)