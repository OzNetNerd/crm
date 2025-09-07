"""
Chat handler service for processing user messages and generating responses.
This will be enhanced with LLM capabilities in later phases.
"""

from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from chatbot.models import Company, Contact, Task, Opportunity, Meeting, ChatHistory


class ChatHandler:
    def __init__(self):
        self.session_context: Dict[str, Dict] = {}
    
    async def process_message(
        self, 
        user_message: str, 
        session_id: str,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: The user's input message
            session_id: Unique session identifier
            db_session: Database session for queries
            
        Returns:
            Dictionary containing the response and metadata
        """
        
        # Simple keyword-based routing (will be replaced with LLM routing)
        response_data = await self._route_query(user_message, session_id, db_session)
        
        return response_data
    
    async def _route_query(
        self, 
        user_message: str, 
        session_id: str,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """Route the query to appropriate handler based on keywords"""
        
        message_lower = user_message.lower()
        
        # Simple keyword routing
        if any(word in message_lower for word in ['company', 'companies']):
            return await self._handle_company_query(user_message, db_session)
        elif any(word in message_lower for word in ['contact', 'contacts', 'person', 'people']):
            return await self._handle_contact_query(user_message, db_session)
        elif any(word in message_lower for word in ['task', 'tasks', 'todo']):
            return await self._handle_task_query(user_message, db_session)
        elif any(word in message_lower for word in ['meeting', 'meetings']):
            return await self._handle_meeting_query(user_message, db_session)
        else:
            return await self._handle_general_query(user_message, db_session)
    
    async def _handle_company_query(self, message: str, db_session: AsyncSession) -> Dict[str, Any]:
        """Handle company-related queries"""
        try:
            result = await db_session.execute(select(Company).limit(5))
            companies = result.scalars().all()
            
            company_list = [f"• {c.name}" + (f" ({c.industry})" if c.industry else "") for c in companies]
            
            response = f"Here are some companies in the system:\n" + "\n".join(company_list)
            if len(companies) == 5:
                response += "\n\n(Showing first 5 results)"
                
            context_used = {
                "query_type": "company_list",
                "companies_found": len(companies)
            }
            
        except Exception as e:
            response = f"Sorry, I encountered an error retrieving company information: {str(e)}"
            context_used = {"error": str(e)}
        
        return {
            "response": response,
            "context_used": context_used,
            "response_metadata": {
                "query_type": "company",
                "processing_time": 0.1
            }
        }
    
    async def _handle_contact_query(self, message: str, db_session: AsyncSession) -> Dict[str, Any]:
        """Handle contact-related queries"""
        try:
            result = await db_session.execute(
                select(Contact).join(Company).limit(5)
            )
            contacts = result.scalars().all()
            
            contact_list = [
                f"• {c.name}" + 
                (f" ({c.role})" if c.role else "") + 
                (f" at {c.company.name}" if c.company else "")
                for c in contacts
            ]
            
            response = f"Here are some contacts in the system:\n" + "\n".join(contact_list)
            if len(contacts) == 5:
                response += "\n\n(Showing first 5 results)"
                
            context_used = {
                "query_type": "contact_list",
                "contacts_found": len(contacts)
            }
            
        except Exception as e:
            response = f"Sorry, I encountered an error retrieving contact information: {str(e)}"
            context_used = {"error": str(e)}
        
        return {
            "response": response,
            "context_used": context_used,
            "response_metadata": {
                "query_type": "contact",
                "processing_time": 0.1
            }
        }
    
    async def _handle_task_query(self, message: str, db_session: AsyncSession) -> Dict[str, Any]:
        """Handle task-related queries"""
        try:
            result = await db_session.execute(
                select(Task)
                .where(Task.status != 'complete')
                .limit(5)
            )
            tasks = result.scalars().all()
            
            task_list = [
                f"• {t.description}" + 
                (f" (Due: {t.due_date})" if t.due_date else "") +
                f" [{t.priority.upper()}]"
                for t in tasks
            ]
            
            response = f"Here are some pending tasks:\n" + "\n".join(task_list)
            if len(tasks) == 5:
                response += "\n\n(Showing first 5 results)"
            elif len(tasks) == 0:
                response = "Great! No pending tasks found."
                
            context_used = {
                "query_type": "task_list",
                "tasks_found": len(tasks)
            }
            
        except Exception as e:
            response = f"Sorry, I encountered an error retrieving task information: {str(e)}"
            context_used = {"error": str(e)}
        
        return {
            "response": response,
            "context_used": context_used,
            "response_metadata": {
                "query_type": "task",
                "processing_time": 0.1
            }
        }
    
    async def _handle_meeting_query(self, message: str, db_session: AsyncSession) -> Dict[str, Any]:
        """Handle meeting-related queries"""
        try:
            result = await db_session.execute(select(Meeting).limit(5))
            meetings = result.scalars().all()
            
            if meetings:
                meeting_list = [
                    f"• {m.title}" + 
                    (f" with {m.company.name}" if m.company else "") +
                    f" ({m.analysis_status})"
                    for m in meetings
                ]
                
                response = f"Here are recent meetings:\n" + "\n".join(meeting_list)
                if len(meetings) == 5:
                    response += "\n\n(Showing first 5 results)"
            else:
                response = "No meetings found in the system yet."
                
            context_used = {
                "query_type": "meeting_list", 
                "meetings_found": len(meetings)
            }
            
        except Exception as e:
            response = f"Sorry, I encountered an error retrieving meeting information: {str(e)}"
            context_used = {"error": str(e)}
        
        return {
            "response": response,
            "context_used": context_used,
            "response_metadata": {
                "query_type": "meeting",
                "processing_time": 0.1
            }
        }
    
    async def _handle_general_query(self, message: str, db_session: AsyncSession) -> Dict[str, Any]:
        """Handle general queries"""
        
        # Provide helpful guidance
        response = """I can help you with information about:
        
• **Companies** - Ask about companies in your CRM
• **Contacts** - Find people and their roles  
• **Tasks** - View pending tasks and deadlines
• **Meetings** - Check recent meetings and analysis

Try asking something like:
- "Show me companies"
- "What tasks are pending?"
- "List recent contacts"
- "Any meetings this week?"

What would you like to know?"""
        
        context_used = {
            "query_type": "help",
            "original_message": message
        }
        
        return {
            "response": response,
            "context_used": context_used,
            "response_metadata": {
                "query_type": "general",
                "processing_time": 0.05
            }
        }