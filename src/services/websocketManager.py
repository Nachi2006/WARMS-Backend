from typing import Dict, List
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self._connections: Dict[str, List[WebSocket]] = {
            "admin": [],
            "ranger": [],
        }

    async def connect(self, websocket: WebSocket, role: str):
        await websocket.accept()
        role_key = role.lower()
        if role_key not in self._connections:
            self._connections[role_key] = []
        self._connections[role_key].append(websocket)

    def disconnect(self, websocket: WebSocket, role: str):
        role_key = role.lower()
        if role_key in self._connections:
            self._connections[role_key] = [
                ws for ws in self._connections[role_key] if ws is not websocket
            ]

    async def broadcast_to_roles(self, roles: List[str], message: dict):
        payload = json.dumps(message)
        for role in roles:
            role_key = role.lower()
            dead = []
            for ws in self._connections.get(role_key, []):
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.disconnect(ws, role_key)

manager = ConnectionManager()
