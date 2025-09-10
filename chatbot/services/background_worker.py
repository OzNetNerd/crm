"""
Background worker for async meeting processing.
Simple implementation - can be enhanced with proper queue system later.
"""

import logging
from typing import Optional

from .meeting_analyzer import get_meeting_analyzer
from chatbot.models import Meeting

logger = logging.getLogger(__name__)


class BackgroundWorker:
    """Simple background worker for meeting analysis"""

    def __init__(self):
        self.analyzer = get_meeting_analyzer()
        self.running = False

    async def process_pending_meetings(self, db_session) -> int:
        """Process all pending meetings"""

        pending_meetings = (
            db_session.query(Meeting)
            .filter(Meeting.analysis_status == "pending")
            .limit(5)
            .all()
        )  # Process in small batches

        processed = 0
        for meeting in pending_meetings:
            try:
                result = await self.analyzer.analyze_meeting(meeting, db_session)
                if result.get("status") == "success":
                    processed += 1
                    logger.info(f"Successfully analyzed meeting {meeting.id}")
                else:
                    logger.error(
                        f"Failed to analyze meeting {meeting.id}: {result.get('error_message', 'Unknown error')}"
                    )

            except Exception as e:
                logger.error(f"Error processing meeting {meeting.id}: {e}")

        return processed


# Singleton instance
_worker: Optional[BackgroundWorker] = None


def get_background_worker() -> BackgroundWorker:
    """Get the singleton background worker instance"""
    global _worker
    if _worker is None:
        _worker = BackgroundWorker()
    return _worker
