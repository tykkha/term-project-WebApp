from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from db.Messages import GatorGuidesMessages
from core.config import settings
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()
messages_instance = None


class SendMessageRequest(BaseModel):
    senderUID: int = Field(..., description="Sender user ID")
    receiverUID: int = Field(..., description="Receiver user ID")
    content: str = Field(..., min_length=1, description="Message content")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                logger.info(f"Sent message to user {user_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                self.disconnect(user_id)
                return False
        return False

    def is_online(self, user_id: int) -> bool:
        return user_id in self.active_connections


manager = ConnectionManager()


def get_messages_manager():
    global messages_instance
    if not messages_instance:
        messages_instance = GatorGuidesMessages(
            host=settings.DATABASE_HOST,
            database=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD
        )
    return messages_instance


# Check if session has been scheduled between tutor and user
@router.get("/messages/can-message/{uid1}/{uid2}")
async def check_messaging_allowed(uid1: int, uid2: int, messages_mgr: GatorGuidesMessages = Depends(get_messages_manager)):
    try:
        allowed = messages_mgr.can_message(uid1, uid2)
        return {
            "allowed": allowed,
            "message": "Messaging allowed" if allowed else "Must have a scheduled session to message"
        }
    except Exception as e:
        logger.error(f"Check messaging error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Send a message
@router.post("/messages", response_model=Dict[str, Any])
async def send_message(request: SendMessageRequest, messages_mgr: GatorGuidesMessages = Depends(get_messages_manager)):
    try:
        # Check if messaging is allowed
        if not messages_mgr.can_message(request.senderUID, request.receiverUID):
            raise HTTPException(
                status_code=403,
                detail="Cannot send message. You must have a scheduled session with this user first."
            )
        
        message = messages_mgr.send_message(
            sender_uid=request.senderUID,
            receiver_uid=request.receiverUID,
            content=request.content
        )
        
        if not message:
            raise HTTPException(status_code=400, detail="Failed to send message")
        
        # If receiver is online, send via WebSocket
        await manager.send_personal_message(message, request.receiverUID)
        
        logger.info(f"Message sent from {request.senderUID} to {request.receiverUID}")
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Get conversation between two users
@router.get("/messages/{uid1}/{uid2}", response_model=List[Dict[str, Any]])
async def get_conversation(uid1: int, uid2: int, limit: int = 50, offset: int = 0, messages_mgr: GatorGuidesMessages = Depends(get_messages_manager)):
    try:
        messages = messages_mgr.get_conversation(uid1, uid2, limit, offset)
        return messages
    except Exception as e:
        logger.error(f"Get conversation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Get message history for recent conversations
@router.get("/users/{uid}/conversations", response_model=List[Dict[str, Any]])
async def get_recent_conversations(uid: int, limit: int = 20, messages_mgr: GatorGuidesMessages = Depends(get_messages_manager)):
    try:
        conversations = messages_mgr.get_recent_conversations(uid, limit)
        return conversations
    except Exception as e:
        logger.error(f"Get conversations error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time messaging
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)