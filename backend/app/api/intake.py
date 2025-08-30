from typing import Dict, Any
import json
from uuid import UUID, uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.intake import WebSocketMessage, TextMessage, AIResponse, RedFlagAlert
from app.services.ai_intake import AIIntakeService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_json(self, session_id: str, data: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)


manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def intake_websocket(
    websocket: WebSocket,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    await manager.connect(websocket, session_id)
    
    try:
        ai_service = AIIntakeService(db)
        
        while True:
            data = await websocket.receive_json()
            message = WebSocketMessage(**data)
            
            if message.type == "text_message":
                text_msg = TextMessage(**data)
                
                response = await ai_service.process_text_input(
                    session_id=session_id,
                    text=text_msg.content,
                    language=text_msg.language,
                )
                
                await websocket.send_json(response.model_dump())
                
                if response.get("type") == "red_flag_alert":
                    await ai_service.escalate_red_flag(
                        session_id=session_id,
                        red_flag=response,
                    )
            
            elif message.type == "audio_chunk":
                pass
            
            elif message.type == "end_session":
                completion = await ai_service.complete_session(session_id)
                await websocket.send_json({
                    "type": "session_complete",
                    "data": completion.model_dump(),
                })
                break
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    
    except Exception as e:
        logger.error(f"Error in WebSocket session {session_id}: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": "An error occurred during the intake session",
        })
        manager.disconnect(session_id)


@router.post("/sessions/{appointment_id}/start")
async def start_intake_session(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    session_id = str(uuid4())
    
    ai_service = AIIntakeService(db)
    session = await ai_service.create_session(
        session_id=session_id,
        appointment_id=appointment_id,
    )
    
    return {
        "session_id": session_id,
        "websocket_url": f"/api/v1/intake/ws/{session_id}",
        "status": "ready",
    }


@router.get("/sessions/{session_id}/status")
async def get_session_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    ai_service = AIIntakeService(db)
    status = await ai_service.get_session_status(session_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return status