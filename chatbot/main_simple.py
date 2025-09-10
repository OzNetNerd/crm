from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime

from database_simple import get_sync_session
from models import Company, Stakeholder, Task, Opportunity, Meeting, ChatHistory

app = FastAPI(title="CRM Chatbot Service", version="1.0.0")


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
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatbot"}


@app.get("/api/chat/test-db")
def test_database(session: Session = Depends(get_sync_session)):
    """Test database connectivity"""
    try:
        # Test basic query
        companies = session.query(Company).limit(5).all()
        
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
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message.strip():
                continue
            
            # Simple response for now
            bot_response = f"I received: '{user_message}'. Full chatbot functionality coming soon!"
            
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
def get_chat_widget():
    """Serve the chat widget for embedding in CRM"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CRM Chatbot Widget</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #333; text-align: center; }
            .status { text-align: center; margin: 20px 0; padding: 10px; background: #e8f5e8; border-radius: 5px; }
            #chat-container { max-width: 500px; height: 600px; margin: 0 auto; border: 1px solid #ccc; display: flex; flex-direction: column; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            #messages { flex: 1; overflow-y: auto; padding: 20px; background: #f9f9f9; }
            #input-area { display: flex; padding: 15px; border-top: 1px solid #eee; background: white; }
            #message-input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
            #send-button { padding: 12px 20px; margin-left: 10px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 5px; font-size: 14px; }
            #send-button:hover { background: #0056b3; }
            .message { margin: 10px 0; padding: 12px 15px; border-radius: 15px; max-width: 80%; word-wrap: break-word; }
            .user-message { background: #007bff; color: white; margin-left: auto; text-align: right; }
            .bot-message { background: white; border: 1px solid #e0e0e0; margin-right: auto; }
            .timestamp { font-size: 11px; opacity: 0.7; margin-top: 5px; }
            .connection-status { padding: 8px 15px; background: #28a745; color: white; font-size: 12px; text-align: center; }
            .connection-status.disconnected { background: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 CRM Chatbot</h1>
            <div class="status">
                <strong>Status:</strong> Basic WebSocket connection established. Full LLM integration coming in next phases.
            </div>
            
            <div id="chat-container">
                <div id="connection-status" class="connection-status">Connecting...</div>
                <div id="messages"></div>
                <div id="input-area">
                    <input type="text" id="message-input" placeholder="Type your message..." maxlength="500">
                    <button id="send-button">Send</button>
                </div>
            </div>
        </div>

        <script>
            const sessionId = 'test-' + Math.random().toString(36).substr(2, 9);
            const ws = new WebSocket(`ws://localhost:8001/ws/chat/${sessionId}`);
            const messagesDiv = document.getElementById('messages');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const statusDiv = document.getElementById('connection-status');

            function addMessage(content, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                
                const textDiv = document.createElement('div');
                textDiv.textContent = content;
                messageDiv.appendChild(textDiv);
                
                const timestampDiv = document.createElement('div');
                timestampDiv.className = 'timestamp';
                timestampDiv.textContent = new Date().toLocaleTimeString();
                messageDiv.appendChild(timestampDiv);
                
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            function sendMessage() {
                const message = messageInput.value.trim();
                if (!message || ws.readyState !== WebSocket.OPEN) return;

                addMessage(message, true);
                ws.send(JSON.stringify({ message: message }));
                messageInput.value = '';
            }

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data.message);
            };

            ws.onopen = function() {
                statusDiv.textContent = '✓ Connected to CRM Chatbot';
                statusDiv.className = 'connection-status';
                addMessage('Welcome! I can help you with your CRM data. Try typing anything to test the connection.');
            };

            ws.onclose = function() {
                statusDiv.textContent = '✗ Connection Lost';
                statusDiv.className = 'connection-status disconnected';
            };

            ws.onerror = function() {
                statusDiv.textContent = '✗ Connection Error';
                statusDiv.className = 'connection-status disconnected';
            };

            sendButton.addEventListener('click', sendMessage);
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            // Focus on input
            messageInput.focus();
        </script>
    </body>
    </html>
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )