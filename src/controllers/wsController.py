from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
import os
from src.services.websocketManager import manager

router = APIRouter(tags=["WebSocket Alerts"])

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role", "")
        if role not in ("admin", "ranger"):
            await websocket.close(code=4003)
            return
    except JWTError:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, role)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, role)
