"""
Configuration management for CRM Chatbot Service
"""
import os
from typing import Optional


class ChatbotConfig:
    """Configuration settings for the chatbot service"""
    
    # Server settings
    HOST: str = os.getenv("CHATBOT_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("CHATBOT_PORT", "8001"))
    RELOAD: bool = os.getenv("CHATBOT_RELOAD", "true").lower() == "true"
    
    # External service URLs
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Qdrant settings
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_PREFER_GRPC: bool = os.getenv("QDRANT_PREFER_GRPC", "false").lower() == "true"
    
    @classmethod
    def get_server_config(cls) -> dict:
        """Get server configuration for uvicorn"""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "reload": cls.RELOAD
        }
    
    @classmethod
    def get_ollama_config(cls) -> dict:
        """Get Ollama client configuration"""
        return {
            "base_url": cls.OLLAMA_BASE_URL
        }
    
    @classmethod
    def get_qdrant_config(cls) -> dict:
        """Get Qdrant service configuration"""
        return {
            "host": cls.QDRANT_HOST,
            "port": cls.QDRANT_PORT,
            "prefer_grpc": cls.QDRANT_PREFER_GRPC
        }