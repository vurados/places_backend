from fastapi import WebSocket
from typing import Dict, List
import json
from uuid import UUID

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}
        self.typing_users: Dict[UUID, List[UUID]] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: UUID):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        # Remove from typing users
        for receiver_id, typing_list in self.typing_users.items():
            if user_id in typing_list:
                typing_list.remove(user_id)

    async def send_personal_message(self, message: str, receiver_id: UUID, sender_id: UUID):
        if receiver_id in self.active_connections:
            websocket = self.active_connections[receiver_id]
            await websocket.send_json({
                "type": "chat_message",
                "message": message,
                "sender_id": str(sender_id),
                "timestamp": "now"  # You might want to use actual timestamp
            })

    async def broadcast_typing(self, receiver_id: UUID, sender_id: UUID, is_typing: bool):
        if receiver_id in self.active_connections:
            websocket = self.active_connections[receiver_id]
            
            if is_typing:
                if receiver_id not in self.typing_users:
                    self.typing_users[receiver_id] = []
                if sender_id not in self.typing_users[receiver_id]:
                    self.typing_users[receiver_id].append(sender_id)
            else:
                if receiver_id in self.typing_users and sender_id in self.typing_users[receiver_id]:
                    self.typing_users[receiver_id].remove(sender_id)
            
            await websocket.send_json({
                "type": "typing",
                "user_id": str(sender_id),
                "is_typing": is_typing,
                "typing_users": [str(uid) for uid in self.typing_users.get(receiver_id, [])]
            })