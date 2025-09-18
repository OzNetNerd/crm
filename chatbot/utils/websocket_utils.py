"""Simple websocket utilities - single responsibility functions."""

import json
from typing import List, Dict
from fastapi import WebSocket


class WebSocketManager:
    """Manages WebSocket connections only."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))


class SessionManager:
    """Manages session tracking only."""

    def __init__(self):
        self.user_sessions: Dict[str, str] = {}  # websocket_id -> session_id

    def add_session(self, websocket: WebSocket, session_id: str):
        self.user_sessions[str(websocket)] = session_id

    def remove_session(self, websocket: WebSocket):
        websocket_id = str(websocket)
        if websocket_id in self.user_sessions:
            del self.user_sessions[websocket_id]

    def get_session_id(self, websocket: WebSocket) -> str:
        return self.user_sessions.get(str(websocket))
