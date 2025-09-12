"""
RAG (Retrieval-Augmented Generation) engine for the CRM chatbot.
Combines semantic search with database queries to provide relevant context for LLM responses.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .embedding_service import get_embedding_service
from .ollama_client import get_ollama_client
from chatbot.models import (
    Company,
    Stakeholder,
    Task,
)

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine for intelligent context retrieval and response generation"""

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.ollama_client = None

    async def _get_ollama_client(self):
        """Get Ollama client instance"""
        if not self.ollama_client:
            self.ollama_client = await get_ollama_client()
        return self.ollama_client

    async def process_query(
        self,
        user_query: str,
        session_id: str,
        db_session: Session,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Process user query with RAG pipeline

        Args:
            user_query: User's question/message
            session_id: Chat session ID
            db_session: Database session
            conversation_history: Previous conversation context

        Returns:
            Response with generated answer and context metadata
        """

        try:
            # Step 1: Query routing and intent detection
            query_intent = self._analyze_query_intent(user_query)

            # Step 2: Retrieve relevant context
            context = await self._retrieve_context(user_query, query_intent, db_session)

            # Step 3: Generate response using LLM
            client = await self._get_ollama_client()
            response_data = await client.generate_chat_response(
                user_message=user_query,
                context=context,
                conversation_history=conversation_history,
            )

            # Step 4: Enhance response with metadata
            response_data.update(
                {
                    "query_intent": query_intent,
                    "context_sources": context.get("sources", []),
                    "context_confidence": context.get("confidence", 0.0),
                    "retrieval_method": context.get("method", "unknown"),
                }
            )

            return response_data

        except Exception as e:
            logger.error(f"RAG processing failed: {e}")
            return {
                "success": False,
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "error_message": str(e),
            }

    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze user query to determine intent and required information
        Simple keyword-based approach (can be enhanced with ML later)
        """

        query_lower = query.lower()

        # Define intent patterns
        patterns = {
            "company_info": [
                "company",
                "companies",
                "organization",
                "client",
                "business",
            ],
            "contact_info": [
                "contact",
                "contacts",
                "person",
                "people",
                "who",
                "email",
                "phone",
            ],
            "task_management": [
                "task",
                "tasks",
                "todo",
                "deadline",
                "due",
                "complete",
                "finish",
            ],
            "meeting_info": ["meeting", "meetings", "discussed", "agenda", "attendees"],
            "opportunity_info": [
                "opportunity",
                "opportunities",
                "deal",
                "sales",
                "revenue",
                "pipeline",
            ],
            "general_search": [
                "find",
                "search",
                "show",
                "list",
                "get",
                "what",
                "how many",
            ],
            "analytics": [
                "report",
                "summary",
                "statistics",
                "count",
                "total",
                "analysis",
            ],
        }

        # Score each intent
        intent_scores = {}
        for intent, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score

        # Determine primary intent
        primary_intent = (
            max(intent_scores.items(), key=lambda x: x[1])[0]
            if intent_scores
            else "general"
        )

        # Extract entities/keywords
        entities = self._extract_entities(query)

        return {
            "primary_intent": primary_intent,
            "intent_scores": intent_scores,
            "entities": entities,
            "query_complexity": self._assess_query_complexity(query, intent_scores),
        }

    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract potential entity names from query (simple approach)"""

        # This is a basic implementation - in production would use NER
        entities = {"names": [], "dates": [], "technologies": [], "numbers": []}

        # Simple pattern matching for common entities
        words = query.split()
        for word in words:
            if word.capitalize() != word.lower() and len(word) > 2:
                entities["names"].append(word)

        return entities

    def _assess_query_complexity(
        self, query: str, intent_scores: Dict[str, int]
    ) -> str:
        """Assess if query is simple, medium, or complex"""

        word_count = len(query.split())
        intent_count = len(intent_scores)

        if word_count < 5 and intent_count <= 1:
            return "simple"
        elif word_count < 15 and intent_count <= 2:
            return "medium"
        else:
            return "complex"

    async def _retrieve_context(
        self, query: str, intent: Dict[str, Any], db_session: Session
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context using multiple strategies
        """

        primary_intent = intent["primary_intent"]
        query_complexity = intent["query_complexity"]

        context = {"sources": [], "confidence": 0.0, "method": "hybrid"}

        try:
            # Strategy 1: Direct database queries for simple intents
            if query_complexity == "simple":
                direct_results = await self._direct_database_search(
                    query, primary_intent, db_session
                )
                context["sources"].extend(direct_results)
                context["method"] = "direct_query"

            # Strategy 2: Semantic search for complex queries
            if query_complexity in ["medium", "complex"]:
                semantic_results = await self._semantic_search(query, db_session)
                context["sources"].extend(semantic_results)
                context["method"] = (
                    "semantic_search" if query_complexity == "complex" else "hybrid"
                )

            # Strategy 3: Related entity search
            entity_results = await self._related_entity_search(
                intent["entities"], db_session
            )
            context["sources"].extend(entity_results)

            # Rank and limit context
            context = self._rank_and_filter_context(context, query, max_items=10)

            return context

        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            raise RuntimeError(f"RAG context retrieval failed: {str(e)}") from e

    async def _direct_database_search(
        self, query: str, intent: str, db_session: Session
    ) -> List[Dict[str, Any]]:
        """Direct database queries for specific intents"""

        results = []

        try:
            if intent == "company_info":
                companies = (
                    db_session.query(Company)
                    .filter(
                        or_(
                            Company.name.ilike(f"%{query}%"),
                            Company.industry.ilike(f"%{query}%"),
                        )
                    )
                    .limit(5)
                    .all()
                )

                for company in companies:
                    results.append(
                        {
                            "type": "company",
                            "id": company.id,
                            "title": company.name,
                            "content": f"Company: {company.name}, Industry: {company.industry or 'N/A'}",
                            "relevance_score": 0.8,
                        }
                    )

            elif intent == "contact_info":
                contacts = (
                    db_session.query(Stakeholder)
                    .join(Company)
                    .filter(
                        or_(
                            Stakeholder.name.ilike(f"%{query}%"),
                            Stakeholder.job_title.ilike(f"%{query}%"),
                            Company.name.ilike(f"%{query}%"),
                        )
                    )
                    .limit(5)
                    .all()
                )

                for contact in contacts:
                    results.append(
                        {
                            "type": "contact",
                            "id": contact.id,
                            "title": contact.name,
                            "content": f"Contact: {contact.name} ({contact.job_title or 'N/A'}) at {contact.company.name if contact.company else 'Unknown'}",
                            "relevance_score": 0.8,
                        }
                    )

            elif intent == "task_management":
                tasks = (
                    db_session.query(Task)
                    .filter(Task.description.ilike(f"%{query}%"))
                    .limit(5)
                    .all()
                )

                for task in tasks:
                    results.append(
                        {
                            "type": "task",
                            "id": task.id,
                            "title": f"Task: {task.description[:50]}...",
                            "content": f"Task: {task.description}, Status: {task.status}, Priority: {task.priority}",
                            "relevance_score": 0.7,
                        }
                    )


        except Exception as e:
            logger.error(f"Direct database search failed: {e}")

        return results

    async def _semantic_search(
        self, query: str, db_session: Session
    ) -> List[Dict[str, Any]]:
        """Semantic search using embeddings"""

        try:
            similar_content = self.embedding_service.search_similar_content(
                query_text=query,
                db_session=db_session,
                top_k=5,
                similarity_threshold=0.6,
            )

            results = []
            for item in similar_content:
                results.append(
                    {
                        "type": item["content_type"],
                        "id": item["content_id"],
                        "title": f"{item['content_type'].title()}: {item['text_content'][:50]}...",
                        "content": (
                            item["text_content"][:200] + "..."
                            if len(item["text_content"]) > 200
                            else item["text_content"]
                        ),
                        "relevance_score": item["similarity_score"],
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    async def _related_entity_search(
        self, entities: Dict[str, List[str]], db_session: Session
    ) -> List[Dict[str, Any]]:
        """Search for entities related to extracted names/terms"""

        results = []

        try:
            # Search for related companies/contacts based on extracted names
            for name in entities.get("names", [])[
                :3
            ]:  # Limit to avoid too many queries
                # Search companies
                companies = (
                    db_session.query(Company)
                    .filter(Company.name.ilike(f"%{name}%"))
                    .limit(2)
                    .all()
                )

                for company in companies:
                    results.append(
                        {
                            "type": "company_related",
                            "id": company.id,
                            "title": f"Related Company: {company.name}",
                            "content": f"Company: {company.name}, Industry: {company.industry or 'N/A'}",
                            "relevance_score": 0.6,
                        }
                    )

        except Exception as e:
            logger.error(f"Related entity search failed: {e}")

        return results

    def _rank_and_filter_context(
        self, context: Dict[str, Any], query: str, max_items: int = 10
    ) -> Dict[str, Any]:
        """Rank context sources by relevance and filter to top items"""

        # Sort sources by relevance score (descending)
        context["sources"].sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        # Limit to max items
        context["sources"] = context["sources"][:max_items]

        # Calculate overall confidence based on source quality
        if context["sources"]:
            avg_relevance = sum(
                s.get("relevance_score", 0) for s in context["sources"]
            ) / len(context["sources"])
            source_count_factor = min(
                len(context["sources"]) / 5.0, 1.0
            )  # More sources = higher confidence
            context["confidence"] = avg_relevance * source_count_factor
        else:
            context["confidence"] = 0.0

        return context


# Singleton instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get the singleton RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
