"""
Ollama client for managing dual LLM models:
- Llama 3.1 8B for structured data extraction
- Llama 3.1 70B for conversational AI
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
from datetime import datetime
from ..config import ChatbotConfig

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for an Ollama model"""

    name: str
    purpose: str  # 'extraction' or 'conversation'
    temperature: float = 0.1
    max_tokens: int = 2048
    system_prompt: str = ""


@dataclass
class ExtractionResult:
    """Result from LLM extraction"""

    success: bool
    extracted_data: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    processing_time: float = 0.0
    error_message: Optional[str] = None
    model_used: Optional[str] = None


class OllamaClient:
    """Client for interacting with Ollama API"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or ChatbotConfig.OLLAMA_BASE_URL
        self.client = httpx.AsyncClient(timeout=60.0)

        # Model configurations
        self.models = {
            "extraction": ModelConfig(
                name="llama3.1:8b",
                purpose="extraction",
                temperature=0.1,  # Low temperature for consistent structured output
                max_tokens=2048,
                system_prompt="""You are an expert at extracting structured information from meeting transcripts. 
Always respond with valid JSON only. Extract key information including:
- attendees (names, roles, sentiment)
- technologies mentioned
- action items (task, assignee, deadline)
- key decisions made
- overall sentiment
- topics discussed

Be precise and only extract information that is clearly stated.""",
            ),
            "conversation": ModelConfig(
                name="llama3.1:8b",
                purpose="conversation",
                temperature=0.7,  # Higher temperature for natural conversation
                max_tokens=1024,
                system_prompt="""You are a helpful CRM assistant. You have access to information about companies, contacts, tasks, and opportunities. 

Provide helpful, accurate responses based on the context provided. If you don't have enough information, say so clearly. Be conversational but professional.

Focus on helping users understand their CRM data and providing actionable insights.""",
            ),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check if Ollama service is available"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]

                return {
                    "status": "healthy",
                    "available_models": available_models,
                    "extraction_model_ready": self.models["extraction"].name
                    in available_models,
                    "conversation_model_ready": self.models["conversation"].name
                    in available_models,
                }
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def ensure_model_loaded(self, model_name: str) -> bool:
        """Ensure a model is loaded and ready"""
        try:
            # Send a simple request to warm up the model
            await self._generate(
                model=model_name,
                prompt="Hello",
                system="You are a helpful assistant.",
                temperature=0.1,
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False

    async def generate_chat_response(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Generate conversational response using the larger model"""

        start_time = datetime.now()
        model_config = self.models["conversation"]

        # Build context string
        context_str = ""
        if context:
            context_str = (
                f"\nContext from CRM database:\n{json.dumps(context, indent=2)}\n"
            )

        # Build conversation history
        history_str = ""
        if conversation_history:
            history_str = "\nRecent conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_str += f"{role}: {content}\n"

        prompt = f"""
{history_str}
{context_str}

User: {user_message}        """

        try:
            if stream:
                # For streaming, return an async generator
                return self._generate_stream(
                    model=model_config.name,
                    prompt=prompt,
                    system=model_config.system_prompt,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens,
                    start_time=start_time,
                )
            else:
                response_text = await self._generate(
                    model=model_config.name,
                    prompt=prompt,
                    system=model_config.system_prompt,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens,
                )

            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "response": response_text.strip(),
                "processing_time": processing_time,
                "model_used": model_config.name,
                "context_used": context is not None,
            }

        except Exception as e:
            logger.error(f"Chat response generation failed: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": False,
                "response": "I'm sorry, I encountered an error processing your request.",
                "error_message": str(e),
                "processing_time": processing_time,
                "model_used": model_config.name,
            }

    async def _generate(
        self,
        model: str,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Internal method to generate text using Ollama API"""

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate", json=payload
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Ollama: {e}")
            raise Exception(f"Ollama API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")

    async def _generate_stream(
        self,
        model: str,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        start_time=None,
    ):
        """Stream text generation using Ollama API"""

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with self.client.stream(
                "POST", f"{self.base_url}/api/generate", json=payload
            ) as response:
                response.raise_for_status()

                full_response = ""
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                text_chunk = chunk["response"]
                                full_response += text_chunk

                                # Yield streaming chunk
                                yield {
                                    "type": "chunk",
                                    "text": text_chunk,
                                    "full_text": full_response,
                                }

                            if chunk.get("done", False):
                                processing_time = (
                                    (datetime.now() - start_time).total_seconds()
                                    if start_time
                                    else 0
                                )
                                # Yield final response
                                yield {
                                    "type": "complete",
                                    "success": True,
                                    "response": full_response.strip(),
                                    "processing_time": processing_time,
                                    "model_used": model,
                                }
                                return

                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            processing_time = (
                (datetime.now() - start_time).total_seconds() if start_time else 0
            )
            yield {
                "type": "complete",
                "success": False,
                "response": "I'm sorry, I encountered an error processing your request.",
                "error_message": str(e),
                "processing_time": processing_time,
                "model_used": model,
            }

    def _calculate_extraction_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on extraction completeness"""

        if not extracted_data:
            return 0.0

        score = 0.0
        max_score = 7.0  # Number of expected fields

        # Check for presence and quality of each field
        fields_to_check = [
            "attendees",
            "technologies_mentioned",
            "action_items",
            "key_decisions",
            "sentiment_analysis",
            "topics_discussed",
            "summary",
        ]

        for field in fields_to_check:
            if field in extracted_data:
                value = extracted_data[field]
                if value:  # Non-empty
                    if isinstance(value, list) and len(value) > 0:
                        score += 1.0
                    elif isinstance(value, dict) and value:
                        score += 1.0
                    elif isinstance(value, str) and len(value) > 5:
                        score += 1.0

        return min(score / max_score, 1.0)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Singleton instance
_ollama_client: Optional[OllamaClient] = None


async def get_ollama_client() -> OllamaClient:
    """Get the singleton Ollama client instance"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


async def close_ollama_client():
    """Close the Ollama client"""
    global _ollama_client
    if _ollama_client:
        await _ollama_client.close()
        _ollama_client = None
