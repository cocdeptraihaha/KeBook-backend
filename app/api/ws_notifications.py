"""WebSocket: realtime notifications (JWT trong query ?token=)."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from starlette.websockets import WebSocketState

from app.core.config import get_settings
from app.core.security import ALGORITHM
from app.realtime.connection_manager import connection_manager

settings = get_settings()
router = APIRouter()


def decode_ws_user_id(token: str) -> int | None:
    if not token or not token.strip():
        return None
    try:
        payload = jwt.decode(token.strip(), settings.SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        return int(sub) if sub is not None else None
    except (JWTError, ValueError, TypeError):
        return None


@router.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    token = websocket.query_params.get("token") or ""
    user_id = decode_ws_user_id(token)
    if user_id is None:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await connection_manager.connect(user_id, websocket)

    async def server_ping_loop():
        try:
            while True:
                await asyncio.sleep(30)
                if websocket.client_state != WebSocketState.CONNECTED:
                    break
                await websocket.send_text(json.dumps({"type": "ping"}))
        except asyncio.CancelledError:
            raise
        except Exception:
            pass

    ping_task = asyncio.create_task(server_ping_loop())
    try:
        while True:
            raw = await websocket.receive_text()
            if not raw.strip():
                continue
            try:
                data = json.loads(raw)
                if data.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        ping_task.cancel()
        try:
            await ping_task
        except asyncio.CancelledError:
            pass
        await connection_manager.disconnect(user_id, websocket)
