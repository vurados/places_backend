from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.auth_service import get_current_user_ws
from services.websocket_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    current_user = Depends(get_current_user_ws)
):
    await manager.connect(websocket, current_user.id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle different types of messages
            if data["type"] == "chat_message":
                await manager.send_personal_message(
                    data["message"], 
                    data["receiver_id"],
                    current_user.id
                )
            elif data["type"] == "typing":
                await manager.broadcast_typing(
                    data["receiver_id"],
                    current_user.id,
                    data["is_typing"]
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket, current_user.id)