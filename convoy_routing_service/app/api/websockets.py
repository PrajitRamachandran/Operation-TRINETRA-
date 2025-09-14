import uuid
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[uuid.UUID, list[WebSocket]] = {}

    async def connect(self, convoy_id: uuid.UUID, websocket: WebSocket):
        await websocket.accept()
        if convoy_id not in self.active_connections:
            self.active_connections[convoy_id] = []
        self.active_connections[convoy_id].append(websocket)

    def disconnect(self, convoy_id: uuid.UUID, websocket: WebSocket):
        if convoy_id in self.active_connections:
            self.active_connections[convoy_id].remove(websocket)
            if not self.active_connections[convoy_id]:
                del self.active_connections[convoy_id]

    async def push_update(self, convoy_id: uuid.UUID, data: dict):
        if connections := self.active_connections.get(convoy_id):
            for connection in connections:
                await connection.send_json(data)

manager = ConnectionManager()