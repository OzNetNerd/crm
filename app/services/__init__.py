"""
Services package for CRM application.

This package contains service classes that implement the business logic
extracted from models to follow single responsibility principle.

Services:
- DisplayService: Handle display names, icons, and UI metadata
- SearchService: Handle search functionality and result formatting
- SerializationService: Handle model serialization and transformations
- MetadataService: Handle field metadata and choices
- EntityRelationshipService: Handle entity linking and relationships
"""

from .display_service import DisplayService
from .search_service import SearchService
from .serialization_service import SerializationService
from .metadata_service import MetadataService
from .query_service import QueryService

__all__ = [
    "DisplayService",
    "SearchService",
    "SerializationService",
    "MetadataService",
    "QueryService",
]