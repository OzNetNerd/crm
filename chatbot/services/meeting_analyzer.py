"""
Meeting analyzer service for processing meeting transcripts with LLM extraction.
This service handles the pipeline from raw transcript to structured CRM data.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from .ollama_client import get_ollama_client, ExtractionResult
from chatbot.models import Meeting, ExtractedInsight, Company, Contact, Task

logger = logging.getLogger(__name__)


class MeetingAnalyzer:
    """Service for analyzing meeting transcripts and extracting structured data"""
    
    def __init__(self):
        self.ollama_client = None
    
    async def _get_client(self):
        """Get the Ollama client instance"""
        if not self.ollama_client:
            self.ollama_client = await get_ollama_client()
        return self.ollama_client
    
    async def analyze_meeting(
        self,
        meeting: Meeting,
        db_session: Session,
        force_reprocess: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a meeting transcript and store extracted insights
        
        Args:
            meeting: Meeting object with transcript
            db_session: Database session
            force_reprocess: Whether to reprocess even if already analyzed
            
        Returns:
            Dictionary with analysis results and metadata
        """
        
        # Check if already processed
        if meeting.analysis_status == "completed" and not force_reprocess:
            return {
                "status": "already_processed",
                "message": "Meeting already analyzed",
                "meeting_id": meeting.id
            }
        
        # Update status to processing
        meeting.analysis_status = "processing"
        db_session.commit()
        
        try:
            client = await self._get_client()
            
            # Extract insights using LLM
            extraction_result = await client.extract_meeting_insights(
                transcript=meeting.transcript,
                meeting_title=meeting.title
            )
            
            if extraction_result.success:
                # Store the extraction results
                await self._store_extraction_results(
                    meeting=meeting,
                    extraction_result=extraction_result,
                    db_session=db_session
                )
                
                # Try to create related CRM entities
                entities_created = await self._create_crm_entities(
                    meeting=meeting,
                    extracted_data=extraction_result.extracted_data,
                    db_session=db_session
                )
                
                # Update meeting status
                meeting.analysis_status = "completed"
                meeting.analyzed_at = datetime.utcnow()
                db_session.commit()
                
                return {
                    "status": "success",
                    "meeting_id": meeting.id,
                    "confidence_score": extraction_result.confidence_score,
                    "processing_time": extraction_result.processing_time,
                    "entities_created": entities_created,
                    "insights_extracted": len(extraction_result.extracted_data.keys()) if extraction_result.extracted_data else 0
                }
                
            else:
                # Extraction failed
                meeting.analysis_status = "failed"
                db_session.commit()
                
                return {
                    "status": "failed",
                    "meeting_id": meeting.id,
                    "error_message": extraction_result.error_message,
                    "processing_time": extraction_result.processing_time
                }
                
        except Exception as e:
            logger.error(f"Meeting analysis failed for meeting {meeting.id}: {e}")
            meeting.analysis_status = "failed"
            db_session.commit()
            
            return {
                "status": "error",
                "meeting_id": meeting.id,
                "error_message": str(e)
            }
    
    async def _store_extraction_results(
        self,
        meeting: Meeting,
        extraction_result: ExtractionResult,
        db_session: Session
    ):
        """Store extraction results as ExtractedInsight records"""
        
        extracted_data = extraction_result.extracted_data
        if not extracted_data:
            return
        
        # Store each type of insight as a separate record for flexibility
        insight_types = {
            'attendees': extracted_data.get('attendees', []),
            'technologies': extracted_data.get('technologies_mentioned', []),
            'action_items': extracted_data.get('action_items', []),
            'decisions': extracted_data.get('key_decisions', []),
            'sentiment': extracted_data.get('sentiment_analysis', {}),
            'topics': extracted_data.get('topics_discussed', []),
            'summary': extracted_data.get('summary', '')
        }
        
        for insight_type, insight_data in insight_types.items():
            if insight_data:  # Only store non-empty insights
                insight = ExtractedInsight(
                    meeting_id=meeting.id,
                    insight_type=insight_type,
                    extracted_data=insight_data,
                    extraction_metadata={
                        "model_used": extraction_result.model_used,
                        "processing_time": extraction_result.processing_time,
                        "extraction_timestamp": datetime.utcnow().isoformat()
                    },
                    confidence_score=extraction_result.confidence_score,
                    review_status="pending"
                )
                
                db_session.add(insight)
        
        db_session.commit()
    
    async def _create_crm_entities(
        self,
        meeting: Meeting,
        extracted_data: Dict[str, Any],
        db_session: Session
    ) -> Dict[str, int]:
        """
        Create CRM entities (tasks, contacts) from extracted data
        
        Returns:
            Dictionary with counts of entities created
        """
        
        entities_created = {
            "tasks": 0,
            "contacts_suggested": 0  # We don't auto-create contacts, just flag for review
        }
        
        # Create tasks from action items
        action_items = extracted_data.get('action_items', [])
        for item in action_items:
            if isinstance(item, dict) and item.get('task'):
                try:
                    # Parse due date if provided
                    due_date = None
                    if item.get('deadline') and item['deadline'] != "null":
                        try:
                            due_date = datetime.strptime(item['deadline'], '%Y-%m-%d').date()
                        except ValueError:
                            pass  # Invalid date format, skip
                    
                    # Create task
                    task = Task(
                        description=f"[From Meeting: {meeting.title}] {item['task']}",
                        due_date=due_date,
                        priority="medium",  # Default priority
                        status="todo",
                        entity_type="company" if meeting.company_id else None,
                        entity_id=meeting.company_id,
                        task_type="single"
                    )
                    
                    db_session.add(task)
                    entities_created["tasks"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to create task from action item: {e}")
        
        # Count suggested contacts (attendees not already in system)
        attendees = extracted_data.get('attendees', [])
        for attendee in attendees:
            if isinstance(attendee, dict) and attendee.get('name'):
                # Check if contact already exists
                existing = db_session.query(Contact).filter(
                    Contact.name.ilike(f"%{attendee['name']}%")
                ).first()
                
                if not existing:
                    entities_created["contacts_suggested"] += 1
        
        if entities_created["tasks"] > 0:
            db_session.commit()
        
        return entities_created
    
    async def get_meeting_insights_summary(
        self,
        meeting_id: int,
        db_session: Session
    ) -> Dict[str, Any]:
        """Get a summary of insights for a specific meeting"""
        
        meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            return {"error": "Meeting not found"}
        
        insights = db_session.query(ExtractedInsight).filter(
            ExtractedInsight.meeting_id == meeting_id
        ).all()
        
        summary = {
            "meeting_id": meeting_id,
            "meeting_title": meeting.title,
            "analysis_status": meeting.analysis_status,
            "analyzed_at": meeting.analyzed_at.isoformat() if meeting.analyzed_at else None,
            "insights_count": len(insights),
            "insights": {}
        }
        
        for insight in insights:
            summary["insights"][insight.insight_type] = {
                "data": insight.extracted_data,
                "confidence_score": insight.confidence_score,
                "review_status": insight.review_status
            }
        
        return summary
    
    async def batch_analyze_meetings(
        self,
        meeting_ids: List[int],
        db_session: Session
    ) -> Dict[str, Any]:
        """Analyze multiple meetings in batch"""
        
        results = []
        
        for meeting_id in meeting_ids:
            meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting:
                result = await self.analyze_meeting(meeting, db_session)
                results.append(result)
            else:
                results.append({
                    "status": "error",
                    "meeting_id": meeting_id,
                    "error_message": "Meeting not found"
                })
        
        return {
            "batch_results": results,
            "total_processed": len(results),
            "successful": len([r for r in results if r.get("status") == "success"]),
            "failed": len([r for r in results if r.get("status") in ["failed", "error"]])
        }


# Singleton instance
_meeting_analyzer: Optional[MeetingAnalyzer] = None


def get_meeting_analyzer() -> MeetingAnalyzer:
    """Get the singleton meeting analyzer instance"""
    global _meeting_analyzer
    if _meeting_analyzer is None:
        _meeting_analyzer = MeetingAnalyzer()
    return _meeting_analyzer