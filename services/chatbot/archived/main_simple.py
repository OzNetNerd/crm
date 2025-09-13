from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Dict
import json
import os
from datetime import datetime

from database_simple import get_sync_session
from models import Company

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
            bot_response = (
                f"I received: '{user_message}'. Full chatbot functionality coming soon!"
            )

            # Send response to client
            response_data = {
                "type": "bot_response",
                "message": bot_response,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
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
    return HTMLResponse(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CRM Chatbot Widget</title>
        <link rel="stylesheet" href="/app/static/css/components.css">
        <link rel="stylesheet" href="/app/static/css/chatbot.css">
    </head>
    <body>
        <div class="chatbot-container">
            <h1 class="chatbot-header">🤖 CRM Chatbot</h1>
            <div class="chatbot-status">
                <strong>Status:</strong> Basic WebSocket connection established. Full LLM integration coming in next phases.
            </div>
            
            <div id="chat-container">
                <div id="connection-status" class="chatbot-connection-status">Connecting...</div>
                <div id="messages" class="chatbot-messages"></div>
                <div id="input-area" class="chatbot-input-area">
                    <input type="text" id="message-input" placeholder="Type your message..." maxlength="500">
                    <button id="send-button" class="chatbot-send-button">Send</button>
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
                messageDiv.className = `chatbot-message ${isUser ? 'user-message' : 'bot-message'}`;
                
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
                statusDiv.className = 'chatbot-connection-status';
                addMessage('Welcome! I can help you with your CRM data. Try typing anything to test the connection.');
            };

            ws.onclose = function() {
                statusDiv.textContent = '✗ Connection Lost';
                statusDiv.className = 'chatbot-connection-status disconnected';
            };

            ws.onerror = function() {
                statusDiv.textContent = '✗ Connection Error';
                statusDiv.className = 'chatbot-connection-status disconnected';
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
    """
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main_simple:app", host="127.0.0.1", port=int(os.environ.get('PORT', '8001')), reload=True)
