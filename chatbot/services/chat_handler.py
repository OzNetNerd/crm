"""
Chat handler service for processing user messages and generating responses.
This will be enhanced with LLM capabilities in later phases.
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from chatbot.models import Company, Stakeholder, Task
from chatbot.services.ollama_client import get_ollama_client
from chatbot.services.qdrant_service import get_qdrant_service


class ChatHandler:
    def __init__(self):
        self.session_context: Dict[str, Dict] = {}
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        self._setup_common_responses()

    async def process_message(
        self, user_message: str, session_id: str, db_session: AsyncSession
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

        try:
            # Check cache first
            cache_key = self._get_cache_key(user_message)
            if cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                return {
                    "response": cached_response["response"],
                    "context_used": cached_response.get("context", {}),
                    "response_metadata": {
                        "query_type": "cached_response",
                        "processing_time": 0.001,
                        "cached": True,
                    },
                }

            # Get Ollama client - service must be healthy
            ollama_client = await get_ollama_client()

            # Verify Ollama is healthy - fail fast if not available
            health_status = await ollama_client.health_check()
            if health_status.get("status") != "healthy":
                raise RuntimeError(
                    f"Ollama service is not healthy: {health_status}. "
                    "Please ensure Ollama is running and properly configured."
                )

            # Add to conversation history
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []

            self.conversation_history[session_id].append(
                {"role": "user", "content": user_message}
            )

            # Determine query intent and gather context
            context = await self._gather_context(user_message, db_session)

            # Generate response using LLM with streaming
            stream = await ollama_client.generate_chat_response(
                user_message=user_message,
                context=context,
                conversation_history=self.conversation_history[session_id],
                stream=True,
            )

            # Return the stream for the WebSocket to handle
            return {"type": "stream", "stream": stream, "session_id": session_id}

        except Exception as e:
            # Re-raise exceptions instead of hiding them with fallbacks
            raise RuntimeError(f"Chat processing failed: {str(e)}") from e

    async def _gather_context(
        self, user_message: str, db_session: AsyncSession
    ) -> Dict[str, Any]:
        """Gather relevant context using Qdrant semantic search"""

        context = {}

        try:
            # Get Qdrant service
            qdrant_service = get_qdrant_service()

            # Perform semantic search for similar content (optimized parameters)
            similar_docs = qdrant_service.search_similar(
                query_text=user_message,
                limit=5,  # Reduced from 10 - fewer but higher quality results
                score_threshold=0.6,  # Increased from 0.3 - only high-confidence matches
            )

            # Organize results by entity type
            companies = []
            contacts = []
            opportunities = []
            tasks = []
            notes = []

            for doc in similar_docs:
                entity_type = doc.get("entity_type", "")
                entity_data = {
                    "id": doc.get("entity_id", 0),
                    "similarity_score": doc.get("score", 0),
                    "text_snippet": (
                        doc.get("text", "")[:200] + "..."
                        if len(doc.get("text", "")) > 200
                        else doc.get("text", "")
                    ),
                    **doc.get("metadata", {}),
                }

                if entity_type == "company":
                    companies.append(entity_data)
                elif entity_type == "contact":
                    contacts.append(entity_data)
                elif entity_type == "opportunity":
                    opportunities.append(entity_data)
                elif entity_type == "task":
                    tasks.append(entity_data)
                elif entity_type == "note":
                    notes.append(entity_data)

            # Build context with most relevant entities (reduced limits for efficiency)
            if companies:
                context["companies"] = companies[:2]  # Reduced from 3 to 2
            if contacts:
                context["contacts"] = contacts[:2]  # Reduced from 3 to 2
            if opportunities:
                context["opportunities"] = opportunities[:2]  # Reduced from 3 to 2
            if tasks:
                context["tasks"] = tasks[:2]  # Reduced from 3 to 2
            if notes:
                context["notes"] = notes[:1]  # Reduced from 2 to 1

            # Add search metadata
            context["search_metadata"] = {
                "total_matches": len(similar_docs),
                "search_method": "semantic_similarity",
                "query": user_message,
            }

        except Exception as e:
            # Context gathering failure is a critical error
            raise RuntimeError(f"Context gathering failed: {str(e)}") from e

        return context

    def _setup_common_responses(self):
        """Setup pre-cached responses for common queries"""
        self.response_cache = {
            "hello": {
                "response": "Hello! I'm your CRM assistant. I can help you find information about companies, contacts, and tasks. What would you like to know?",
                "context": {},
            },
            "help": {
                "response": "I can help you with:\n• **Companies** - View your business clients and prospects\n• **Contacts** - Find people and their roles\n• **Tasks** - Check pending work and deadlines\n\nJust ask me something like 'show me companies' or 'what tasks are pending?'",
                "context": {},
            },
            "what can you do": {
                "response": "I'm your CRM assistant! I can help you:\n• Find companies by industry or name\n• Look up contacts and their details\n• Show pending tasks and priorities\n\nTry asking: 'What companies do we have?' or 'Show me high priority tasks'",
                "context": {},
            },
        }

    def _get_cache_key(self, message: str) -> str:
        """Generate cache key from user message"""
        message_clean = message.lower().strip()

        # Check for exact matches first
        if message_clean in self.response_cache:
            return message_clean

        # Check for specific patterns that should be cached
        if any(greeting in message_clean for greeting in ["hello", "hi", "hey"]):
            return "hello"
        elif any(
            help_word in message_clean
            for help_word in ["help", "what can you do", "what do you do"]
        ):
            return "help"
        elif message_clean == "what can you do":
            return "what can you do"

        return message_clean  # Return original if no match (will not be cached)

    async def _route_query(
        self, user_message: str, session_id: str, db_session: AsyncSession
    ) -> Dict[str, Any]:
        """Route the query to appropriate handler based on keywords"""

        message_lower = user_message.lower()

        # Simple keyword routing
        if any(word in message_lower for word in ["company", "companies"]):
            return await self._handle_company_query(user_message, db_session)
        elif any(
            word in message_lower
            for word in ["contact", "contacts", "person", "people"]
        ):
            return await self._handle_contact_query(user_message, db_session)
        elif any(word in message_lower for word in ["task", "tasks", "todo"]):
            return await self._handle_task_query(user_message, db_session)
        else:
            return await self._handle_general_query(user_message, db_session)

    async def _handle_company_query(
        self, message: str, db_session: AsyncSession
    ) -> Dict[str, Any]:
        """Handle company-related queries"""
        try:
            result = await db_session.execute(select(Company).limit(5))
            companies = result.scalars().all()

            company_list = [
                f"• {c.name}" + (f" ({c.industry})" if c.industry else "")
                for c in companies
            ]

            response = "Here are some companies in the system:\n" + "\n".join(
                company_list
            )
            if len(companies) == 5:
                response += "\n\n(Showing first 5 results)"

            context_used = {
                "query_type": "company_list",
                "companies_found": len(companies),
            }

        except Exception as e:
            response = f"Sorry, I encountered an error retrieving company information: {str(e)}"
            context_used = {"error": str(e)}

        return {
            "response": response,
            "context_used": context_used,
            "response_metadata": {"query_type": "company", "processing_time": 0.1},
        }

    async def _handle_contact_query(
        self, message: str, db_session: AsyncSession
    ) -> Dict[str, Any]:
        """Handle contact-related queries"""
        try:
            result = await db_session.execute(
                select(Stakeholder).join(Company).limit(5)
            )
            contacts = result.scalars().all()

            contact_list = [
                f"• {c.name}"
                + (f" ({c.job_title})" if c.job_title else "")
                + (f" at {c.company.name}" if c.company else "")
                for c in contacts
            ]

            response = "Here are some contacts in the system:\n" + "\n".join(
                contact_list
            )
            if len(contacts) == 5:
                response += "\n\n(Showing first 5 results)"

            context_used = {
                "query_type": "contact_list",
                "contacts_found": len(contacts),
            }

        except Exception as e:
            response = f"Sorry, I encountered an error retrieving contact information: {str(e)}"
            context_used = {"error": str(e)}

        return {
            "response": response,
            "context_used": context_used,
            "response_metadata": {"query_type": "contact", "processing_time": 0.1},
        }

    async def _handle_task_query(
        self, message: str, db_session: AsyncSession
    ) -> Dict[str, Any]:
        """Handle task-related queries"""
        try:
            result = await db_session.execute(
                select(Task).where(Task.status != "complete").limit(5)
            )
            tasks = result.scalars().all()

            task_list = [
                f"• {t.description}"
                + (f" (Due: {t.due_date})" if t.due_date else "")
                + f" [{t.priority.upper()}]"
                for t in tasks
            ]

            response = "Here are some pending tasks:\n" + "\n".join(task_list)
            if len(tasks) == 5:
                response += "\n\n(Showing first 5 results)"
            elif len(tasks) == 0:
                response = "Great! No pending tasks found."

            context_used = {"query_type": "task_list", "tasks_found": len(tasks)}

        except Exception as e:
            response = (
                f"Sorry, I encountered an error retrieving task information: {str(e)}"
            )
            context_used = {"error": str(e)}

        return {
            "response": response,
            "context_used": context_used,
            "response_metadata": {"query_type": "task", "processing_time": 0.1},
        }


    async def _handle_general_query(
        self, message: str, db_session: AsyncSession
    ) -> Dict[str, Any]:
        """Handle general queries"""

        # Provide helpful guidance
        response = """I can help you with information about:
        
• **Companies** - Ask about companies in your CRM
• **Contacts** - Find people and their roles  
• **Tasks** - View pending tasks and deadlines

Try asking something like:
- "Show me companies"
- "What tasks are pending?"
- "List recent contacts"

What would you like to know?"""

        context_used = {"query_type": "help", "original_message": message}

        return {
            "response": response,
            "context_used": context_used,
            "response_metadata": {"query_type": "general", "processing_time": 0.05},
        }
