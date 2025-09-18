"""Enums for model fields - eliminating magic strings."""

from enum import Enum


class TaskStatus(str, Enum):
    """Task status values."""

    TODO = "todo"
    IN_PROGRESS = "in-progress"
    COMPLETE = "complete"


class Priority(str, Enum):
    """Priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskType(str, Enum):
    """Task hierarchy types."""

    SINGLE = "single"
    PARENT = "parent"
    CHILD = "child"


class DependencyType(str, Enum):
    """Task dependency types."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class NextStepType(str, Enum):
    """Next step types for tasks."""

    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    DEMO = "demo"


class OpportunityStage(str, Enum):
    """Opportunity pipeline stages."""

    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed-won"
    CLOSED_LOST = "closed-lost"


class EntityType(str, Enum):
    """Entity types for relationships."""

    COMPANY = "company"
    OPPORTUNITY = "opportunity"
    STAKEHOLDER = "stakeholder"
    CONTACT = "contact"
    TASK = "task"


class MeddpiccRole(str, Enum):
    """MEDDPICC sales methodology roles."""

    METRIC = "metric"
    ECONOMIC_BUYER = "economic_buyer"
    DECISION_CRITERIA = "decision_criteria"
    DECISION_PROCESS = "decision_process"
    PAPER_PROCESS = "paper_process"
    IDENTIFY_PAIN = "identify_pain"
    CHAMPION = "champion"
    COMPETITION = "competition"
