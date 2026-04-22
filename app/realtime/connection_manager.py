"""In-memory WebSocket registry: user_id -> set of connections (1 worker)."""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Iterable, Set

from starlette.websockets import WebSocket, WebSocketState


class ConnectionManager:
    """Quản lý socket theo user. Khi scale nhiều pod, thay bằng Redis pub/sub."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._user_sockets: Dict[int, Set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._user_sockets.setdefault(user_id, set()).add(websocket)

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            bucket = self._user_sockets.get(user_id)
            if not bucket:
                return
            bucket.discard(websocket)
            if not bucket:
                del self._user_sockets[user_id]

    async def send_json_to_user(self, user_id: int, payload: dict[str, Any]) -> None:
        text = json.dumps(payload, default=str)
        async with self._lock:
            sockets = list(self._user_sockets.get(user_id, ()))
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                if ws.client_state != WebSocketState.CONNECTED:
                    dead.append(ws)
                    continue
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(user_id, ws)

    async def send_json_to_users(self, user_ids: Iterable[int], payload_fn) -> None:
        """payload_fn(uid) -> dict — mỗi user có thể khác (vd. unread_count)."""
        for uid in user_ids:
            await self.send_json_to_user(uid, payload_fn(uid))


connection_manager = ConnectionManager()
