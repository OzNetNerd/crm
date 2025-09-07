#!/usr/bin/env python3
"""
Test script for the CRM Chatbot Service (simplified version)
"""

import sys
import uvicorn
from pathlib import Path

# Add chatbot directory to Python path
chatbot_dir = Path(__file__).parent / "chatbot"
sys.path.insert(0, str(chatbot_dir))

def main():
    print("🤖 Starting CRM Chatbot Service (Test Version)")
    print("💬 Chat widget: http://127.0.0.1:8001/chat-widget")
    print("🏥 Health check: http://127.0.0.1:8001/health")
    print("🧪 DB test: http://127.0.0.1:8001/api/chat/test-db")
    
    try:
        uvicorn.run(
            "main_simple:app",
            host="127.0.0.1",
            port=8001,
            reload=True
        )
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port 8001 is already in use!")
            print("💡 Stop any existing chatbot service first")
        else:
            raise


if __name__ == "__main__":
    main()
