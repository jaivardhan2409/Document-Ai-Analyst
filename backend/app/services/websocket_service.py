from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """Connect a user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, user_id: str, websocket: WebSocket):
        """Disconnect a user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def broadcast(self, user_id: str, data: dict):
        """Send message to all user connections"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    print(f"Error sending message: {e}")
    
    async def send_personal(self, websocket: WebSocket, data: dict):
        """Send message to single connection"""
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f"Error sending message: {e}")

manager = ConnectionManager()

# WebSocket endpoint
from fastapi import APIRouter

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Broadcast to all user's connections
            await manager.broadcast(
                user_id,
                {
                    "type": "message",
                    "content": message,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
