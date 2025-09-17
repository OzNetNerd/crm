"""Entity-specific forms"""

from .company import CompanyForm
from .stakeholder import StakeholderForm
from .opportunity import OpportunityForm
from .notes import NoteForm

__all__ = ["CompanyForm", "StakeholderForm", "OpportunityForm", "NoteForm"]
