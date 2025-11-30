from typing import Dict, List
from fastapi import WebSocket

class ChatManager:
    def __init__(self):
        self.active_users: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_users:
            self.active_users[user_id] = []
        self.active_users[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        self.active_users[user_id].remove(websocket)
        if not self.active_users[user_id]:
            del self.active_users[user_id]

    async def send_personal_message(self, receiver_id: int, message: dict):
        if receiver_id in self.active_users:
            for ws in self.active_users[receiver_id]:
                await ws.send_json(message)

chat_manager = ChatManager()
