import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime

from database import get_async_session
from models import Company, Contact, Task, Opportunity, Meeting, ChatHistory
from services.chat_handler import ChatHandler

app = FastAPI(title="CRM Chatbot Service", version="1.0.0")

# Mount static files
import os
current_dir = os.path.dirname(__file__)
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

# Initialize chat handler (will be created when we implement the service)
# chat_handler = ChatHandler()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, str] = {}  # websocket -> session_id mapping

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_sessions[str(websocket)] = session_id

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if str(websocket) in self.user_sessions:
            del self.user_sessions[str(websocket)]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))


manager = ConnectionManager()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatbot"}


@app.get("/api/chat/test-db")
async def test_database(session: AsyncSession = Depends(get_async_session)):
    """Test database connectivity"""
    try:
        # Test basic query
        result = await session.execute(select(Company).limit(5))
        companies = result.scalars().all()
        
        return {
            "status": "success",
            "message": "Database connection working",
            "sample_data": {
                "companies_count": len(companies),
                "companies": [{"id": c.id, "name": c.name} for c in companies]
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }


@app.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message.strip():
                continue
                
            # For now, simple echo response (will be replaced with LLM processing)
            bot_response = f"Echo: {user_message} (Session: {session_id})"
            
            # Save to chat history
            chat_history = ChatHistory(
                session_id=session_id,
                user_message=user_message,
                bot_response=bot_response,
                context_used={"type": "echo", "timestamp": datetime.utcnow().isoformat()},
                response_metadata={"model": "echo", "processing_time": 0.001}
            )
            
            session.add(chat_history)
            await session.commit()
            
            # Send response to client
            response_data = {
                "type": "bot_response",
                "message": bot_response,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id
            }
            
            await manager.send_personal_message(response_data, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.get("/chat-widget")
async def get_chat_widget():
    """Serve the chat widget for embedding in CRM"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat Widget Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #chat-container { max-width: 400px; height: 500px; border: 1px solid #ccc; display: flex; flex-direction: column; }
            #messages { flex: 1; overflow-y: auto; padding: 10px; background: #f5f5f5; }
            #input-area { display: flex; padding: 10px; border-top: 1px solid #ccc; }
            #message-input { flex: 1; padding: 8px; border: 1px solid #ccc; }
            #send-button { padding: 8px 16px; margin-left: 5px; background: #007bff; color: white; border: none; cursor: pointer; }
            .message { margin: 5px 0; padding: 8px; border-radius: 5px; }
            .user-message { background: #007bff; color: white; text-align: right; }
            .bot-message { background: white; border: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <h2>Chatbot Test Interface</h2>
        <div id="chat-container">
            <div id="messages"></div>
            <div id="input-area">
                <input type="text" id="message-input" placeholder="Type your message...">
                <button id="send-button">Send</button>
            </div>
        </div>

        <script>
            const sessionId = 'test-' + Math.random().toString(36).substr(2, 9);
            const ws = new WebSocket(`ws://localhost:8001/ws/chat/${sessionId}`);
            const messagesDiv = document.getElementById('messages');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');

            function addMessage(content, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                messageDiv.textContent = content;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                addMessage(message, true);
                ws.send(JSON.stringify({ message: message }));
                messageInput.value = '';
            }

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data.message);
            };

            ws.onopen = function() {
                addMessage('Connected to chatbot!');
            };

            sendButton.addEventListener('click', sendMessage);
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )