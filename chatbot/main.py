import os
import json
import uvicorn
from datetime import datetime
from typing import List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_async_session
from models import Company, ChatHistory
from services.chat_handler import ChatHandler

app = FastAPI(title="CRM Chatbot Service", version="1.0.0")

current_dir = os.path.dirname(__file__)
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

# Initialize chat handler
chat_handler = ChatHandler()


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
                "companies": [{"id": c.id, "name": c.name} for c in companies],
            },
        }
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}


@app.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    session: AsyncSession = Depends(get_async_session),
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

            # Process message through ChatHandler
            try:
                response_data = await chat_handler.process_message(
                    user_message=user_message, session_id=session_id, db_session=session
                )

                if response_data.get("type") == "stream":
                    # Handle streaming response
                    stream = response_data["stream"]
                    full_response = ""

                    async for chunk in stream:
                        if chunk["type"] == "chunk":
                            # Send streaming chunk to client
                            await manager.send_personal_message(
                                {
                                    "type": "streaming_chunk",
                                    "text": chunk["text"],
                                    "timestamp": datetime.utcnow().isoformat(),
                                },
                                websocket,
                            )

                        elif chunk["type"] == "complete":
                            full_response = chunk.get("response", "")

                            # Add to conversation history
                            if (
                                hasattr(chat_handler, "conversation_history")
                                and session_id in chat_handler.conversation_history
                            ):
                                chat_handler.conversation_history[session_id].append(
                                    {"role": "assistant", "content": full_response}
                                )
                                # Keep only last 10 messages
                                chat_handler.conversation_history[session_id] = (
                                    chat_handler.conversation_history[session_id][-10:]
                                )

                            # Send completion signal
                            await manager.send_personal_message(
                                {
                                    "type": "streaming_complete",
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "processing_time": chunk.get("processing_time", 0),
                                },
                                websocket,
                            )

                            # Save to chat history
                            chat_history = ChatHistory(
                                session_id=session_id,
                                user_message=user_message,
                                bot_response=full_response,
                                context_used=response_data.get("context_used", {}),
                                response_metadata={
                                    "query_type": "llm_streaming",
                                    "processing_time": chunk.get("processing_time", 0),
                                    "model_used": chunk.get("model_used", "unknown"),
                                },
                            )

                            session.add(chat_history)
                            await session.commit()
                            break

                else:
                    # Invalid response type - this should not happen
                    raise RuntimeError(
                        f"Invalid response type received: {response_data}"
                    )

            except Exception as e:
                # Close the websocket connection on errors instead of sending fallback responses
                print(f"Chat processing failed: {e}")
                manager.disconnect(websocket)
                raise

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.get("/chat-widget")
async def get_chat_widget():
    """Serve the chat widget for embedding in CRM"""
    return HTMLResponse(
        """
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
            
            .typing-indicator {
                display: flex;
                align-items: center;
            }
            
            .typing-indicator span:not(:last-child) {
                height: 8px;
                width: 8px;
                background-color: #007bff;
                border-radius: 50%;
                display: inline-block;
                margin-right: 3px;
                animation: typing 1.4s infinite ease-in-out;
            }
            
            .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
            .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
            .typing-indicator span:nth-child(3) { animation-delay: 0s; }
            
            @keyframes typing {
                0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
                40% { transform: scale(1); opacity: 1; }
            }
            
            input:disabled, button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
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
            const ws = new WebSocket(`ws://${window.location.host}/ws/chat/${sessionId}`);
            const messagesDiv = document.getElementById('messages');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');

            function addMessage(content, isUser = false, isTyping = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                
                if (isTyping) {
                    messageDiv.innerHTML = `
                        <div class="typing-indicator">
                            <span></span><span></span><span></span>
                            <span style="margin-left: 10px;">Assistant is thinking...</span>
                        </div>
                    `;
                    messageDiv.id = 'typing-message';
                } else {
                    messageDiv.textContent = content;
                }
                
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                return messageDiv;
            }

            function removeTypingIndicator() {
                const typingMessage = document.getElementById('typing-message');
                if (typingMessage) {
                    typingMessage.remove();
                }
            }

            function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                addMessage(message, true);
                addMessage('', false, true); // Add typing indicator
                ws.send(JSON.stringify({ message: message }));
                messageInput.value = '';
                
                // Disable input while waiting for response
                messageInput.disabled = true;
                sendButton.disabled = true;
            }

            let currentStreamingMessage = null;
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'streaming_chunk') {
                    // Handle streaming text chunks
                    if (!currentStreamingMessage) {
                        removeTypingIndicator();
                        currentStreamingMessage = addMessage('', false, false); // Create empty message div
                    }
                    // Append text to the current streaming message
                    currentStreamingMessage.textContent += data.text;
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    
                } else if (data.type === 'streaming_complete') {
                    // Streaming finished
                    currentStreamingMessage = null;
                    
                    // Re-enable input after response
                    messageInput.disabled = false;
                    sendButton.disabled = false;
                    messageInput.focus();
                    
                } else if (data.type === 'bot_response') {
                    // Handle non-streaming response
                    removeTypingIndicator();
                    addMessage(data.message);
                    
                    // Re-enable input after response
                    messageInput.disabled = false;
                    sendButton.disabled = false;
                    messageInput.focus();
                }
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
    """
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
