#!/usr/bin/env python3
"""
Entry point for the CRM Chatbot Service
"""

import argparse
import uvicorn
import sys
from pathlib import Path

# Add chatbot directory to Python path
chatbot_dir = Path(__file__).parent / "chatbot"
sys.path.insert(0, str(chatbot_dir))

def main():
    parser = argparse.ArgumentParser(description="Run the CRM Chatbot Service")
    parser.add_argument(
        "--port", 
        type=int, 
        default=8001, 
        help="Port number to run the chatbot service on (default: 8001)"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1", 
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()

    print(f"🤖 Starting CRM Chatbot Service on http://{args.host}:{args.port}")
    print(f"💬 Chat widget test: http://{args.host}:{args.port}/chat-widget")
    print(f"🏥 Health check: http://{args.host}:{args.port}/health")
    
    try:
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {args.port} is already in use!")
            print("💡 Try using a different port with --port <number>")
        else:
            raise


if __name__ == "__main__":
    main()