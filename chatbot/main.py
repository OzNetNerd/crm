import os
import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import ChatbotConfig
from database import get_async_session
from services.chat_handler import ChatHandler
from logging_config import setup_chatbot_logging, log_request_middleware
from utils.websocket_utils import WebSocketManager, SessionManager
from utils.message_processor import handle_streaming_response, handle_regular_response

app = FastAPI(title="CRM Chatbot Service", version="1.0.0")

# Configure logging
setup_chatbot_logging(
    "chatbot-service", debug=os.environ.get("DEBUG", "False").lower() == "true"
)
app.middleware("http")(log_request_middleware)

# Setup static files and templates
current_dir = os.path.dirname(__file__)
app.mount(
    "/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static"
)
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize managers
chat_handler = ChatHandler()
ws_manager = WebSocketManager()
session_manager = SessionManager()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "chatbot"}


@app.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    """WebSocket endpoint for chat - clean and simple."""
    await ws_manager.connect(websocket)
    session_manager.add_session(websocket, session_id)

    try:
        while True:
            # Receive and parse message
            data = await websocket.receive_text()
            user_message = json.loads(data).get("message", "").strip()

            if not user_message:
                continue

            # Process message
            response_data = await chat_handler.process_message(
                user_message=user_message, session_id=session_id, db_session=session
            )

            # Handle response based on type
            if response_data.get("type") == "stream":
                await handle_streaming_response(response_data, websocket, ws_manager)
            else:
                await handle_regular_response(
                    response_data["response"], websocket, ws_manager
                )

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        session_manager.remove_session(websocket)


@app.get("/chat-widget")
async def get_chat_widget():
    """Serve the chat widget HTML."""
    with open(os.path.join(current_dir, "templates", "chat_widget.html")) as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    config = ChatbotConfig.get_server_config()
    uvicorn.run("main:app", **config)
