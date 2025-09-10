#!/usr/bin/env python3
"""
Script to index all CRM entities into Qdrant for semantic search.
This script extracts text from companies, contacts, opportunities, tasks, and notes.
"""

import sys
import logging
from pathlib import Path

# Add project paths to Python path BEFORE importing modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))
sys.path.insert(0, str(project_root / "chatbot"))

# Now safe to import after path setup
from flask import Flask  # noqa: E402
from app.models import (  # noqa: E402
    db,
    Company,
    Stakeholder,
    Opportunity,
    Task,
    Note,
)
from chatbot.services.qdrant_service import get_qdrant_service  # noqa: E402
from main import get_database_path  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app():
    """Create Flask app for database access"""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_path()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def extract_company_text(company: Company) -> str:
    """Extract searchable text from a company"""
    parts = [company.name]

    if company.industry:
        parts.append(f"Industry: {company.industry}")
    if company.website:
        parts.append(f"Website: {company.website}")

    return " ".join(parts)


def extract_contact_text(contact: Contact) -> str:
    """Extract searchable text from a contact"""
    parts = [contact.name]

    if contact.email:
        parts.append(f"Email: {contact.email}")
    if contact.phone:
        parts.append(f"Phone: {contact.phone}")
    if contact.role:
        parts.append(f"Role: {contact.role}")
    if contact.company:
        parts.append(f"Company: {contact.company.name}")

    return " ".join(parts)


def extract_opportunity_text(opportunity: Opportunity) -> str:
    """Extract searchable text from an opportunity"""
    parts = [opportunity.name]

    if opportunity.stage:
        parts.append(f"Stage: {opportunity.stage}")
    if opportunity.value:
        parts.append(f"Value: ${opportunity.value}")
    if opportunity.company:
        parts.append(f"Company: {opportunity.company.name}")

    return " ".join(parts)


def extract_task_text(task: Task) -> str:
    """Extract searchable text from a task"""
    parts = [task.description]

    if task.status:
        parts.append(f"Status: {task.status}")
    if task.priority:
        parts.append(f"Priority: {task.priority}")
    if task.next_step_type:
        parts.append(f"Next Step: {task.next_step_type}")

    return " ".join(parts)


def extract_meeting_text(meeting: Meeting) -> str:
    """Extract searchable text from a meeting"""
    parts = [meeting.title]

    if meeting.description:
        parts.append(meeting.description)
    if meeting.transcript:
        parts.append(meeting.transcript)
    if meeting.summary:
        parts.append(meeting.summary)

    return " ".join(parts)


def extract_note_text(note: Note) -> str:
    """Extract searchable text from a note"""
    parts = [note.content]

    if note.entity_type:
        parts.append(f"Type: {note.entity_type}")

    return " ".join(parts)


def index_companies(qdrant_service, db_session) -> int:
    """Index all companies"""
    logger.info("Indexing companies...")
    count = 0

    companies = db_session.query(Company).all()

    for company in companies:
        try:
            text = extract_company_text(company)
            doc_id = f"company_{company.id}"

            metadata = {
                "name": company.name,
                "industry": company.industry,
                "website": company.website,
            }

            success = qdrant_service.index_document(
                doc_id=doc_id,
                text=text,
                entity_type="company",
                entity_id=company.id,
                metadata=metadata,
            )

            if success:
                count += 1

        except Exception as e:
            logger.error(f"Failed to index company {company.id}: {e}")

    logger.info(f"Indexed {count} companies")
    return count


def index_contacts(qdrant_service, db_session) -> int:
    """Index all contacts"""
    logger.info("Indexing contacts...")
    count = 0

    contacts = db_session.query(Contact).all()

    for contact in contacts:
        try:
            text = extract_contact_text(contact)
            doc_id = f"contact_{contact.id}"

            metadata = {
                "name": contact.name,
                "email": contact.email,
                "role": contact.role,
                "phone": contact.phone,
                "company_name": contact.company.name if contact.company else None,
            }

            success = qdrant_service.index_document(
                doc_id=doc_id,
                text=text,
                entity_type="contact",
                entity_id=contact.id,
                metadata=metadata,
            )

            if success:
                count += 1

        except Exception as e:
            logger.error(f"Failed to index contact {contact.id}: {e}")

    logger.info(f"Indexed {count} contacts")
    return count


def index_opportunities(qdrant_service, db_session) -> int:
    """Index all opportunities"""
    logger.info("Indexing opportunities...")
    count = 0

    opportunities = db_session.query(Opportunity).all()

    for opp in opportunities:
        try:
            text = extract_opportunity_text(opp)
            doc_id = f"opportunity_{opp.id}"

            metadata = {
                "name": opp.name,
                "stage": opp.stage,
                "value": float(opp.value) if opp.value else None,
                "company_name": opp.company.name if opp.company else None,
                "expected_close_date": (
                    opp.expected_close_date.isoformat()
                    if opp.expected_close_date
                    else None
                ),
                "created_at": opp.created_at.isoformat() if opp.created_at else None,
            }

            success = qdrant_service.index_document(
                doc_id=doc_id,
                text=text,
                entity_type="opportunity",
                entity_id=opp.id,
                metadata=metadata,
            )

            if success:
                count += 1

        except Exception as e:
            logger.error(f"Failed to index opportunity {opp.id}: {e}")

    logger.info(f"Indexed {count} opportunities")
    return count


def index_tasks(qdrant_service, db_session) -> int:
    """Index all tasks"""
    logger.info("Indexing tasks...")
    count = 0

    tasks = db_session.query(Task).all()

    for task in tasks:
        try:
            text = extract_task_text(task)
            doc_id = f"task_{task.id}"

            metadata = {
                "description": task.description[:100],  # Truncate for metadata
                "status": task.status,
                "priority": task.priority,
                "entity_type": task.entity_type,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
            }

            success = qdrant_service.index_document(
                doc_id=doc_id,
                text=text,
                entity_type="task",
                entity_id=task.id,
                metadata=metadata,
            )

            if success:
                count += 1

        except Exception as e:
            logger.error(f"Failed to index task {task.id}: {e}")

    logger.info(f"Indexed {count} tasks")
    return count


def index_meetings(qdrant_service, db_session) -> int:
    """Index all meetings"""
    logger.info("Indexing meetings...")
    count = 0

    meetings = db_session.query(Meeting).all()

    for meeting in meetings:
        try:
            text = extract_meeting_text(meeting)
            doc_id = f"meeting_{meeting.id}"

            metadata = {
                "title": meeting.title,
                "meeting_date": (
                    meeting.meeting_date.isoformat() if meeting.meeting_date else None
                ),
                "duration_minutes": meeting.duration_minutes,
                "created_at": (
                    meeting.created_at.isoformat() if meeting.created_at else None
                ),
            }

            success = qdrant_service.index_document(
                doc_id=doc_id,
                text=text,
                entity_type="meeting",
                entity_id=meeting.id,
                metadata=metadata,
            )

            if success:
                count += 1

        except Exception as e:
            logger.error(f"Failed to index meeting {meeting.id}: {e}")

    logger.info(f"Indexed {count} meetings")
    return count


def index_notes(qdrant_service, db_session) -> int:
    """Index all notes"""
    logger.info("Indexing notes...")
    count = 0

    notes = db_session.query(Note).all()

    for note in notes:
        try:
            text = extract_note_text(note)
            doc_id = f"note_{note.id}"

            metadata = {
                "content": note.content[:100],  # Truncate for metadata
                "entity_type": note.entity_type,
                "entity_id": note.entity_id,
                "is_internal": note.is_internal,
                "created_at": note.created_at.isoformat() if note.created_at else None,
            }

            success = qdrant_service.index_document(
                doc_id=doc_id,
                text=text,
                entity_type="note",
                entity_id=note.id,
                metadata=metadata,
            )

            if success:
                count += 1

        except Exception as e:
            logger.error(f"Failed to index note {note.id}: {e}")

    logger.info(f"Indexed {count} notes")
    return count


def main():
    """Main indexing function"""
    logger.info("Starting CRM entity indexing...")

    # Create Flask app and database session
    app = create_app()

    with app.app_context():
        # Get Qdrant service
        qdrant_service = get_qdrant_service()

        # Ensure collection exists
        qdrant_service.ensure_collection()

        # Get database session
        db_session = db.session

        # Index all entity types
        total_indexed = 0

        total_indexed += index_companies(qdrant_service, db_session)
        total_indexed += index_contacts(qdrant_service, db_session)
        total_indexed += index_opportunities(qdrant_service, db_session)
        total_indexed += index_tasks(qdrant_service, db_session)
        total_indexed += index_meetings(qdrant_service, db_session)
        total_indexed += index_notes(qdrant_service, db_session)

        logger.info(f"Indexing complete! Total documents indexed: {total_indexed}")

        # Get collection info
        collection_info = qdrant_service.get_collection_info()
        if collection_info:
            logger.info(f"Collection info: {collection_info}")


if __name__ == "__main__":
    main()
