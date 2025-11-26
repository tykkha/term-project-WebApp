from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from db.Sessions import GatorGuidesSessions
from core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
session_manager_instance = None


class CreateSessionRequest(BaseModel):
    uid: int = Field(..., description="User ID (student)")
    tid: int = Field(..., description="Tutor ID")
    tagsID: int = Field(..., description="Tag ID (course)")
    day: str = Field(..., description="Day of week (Monday-Sunday)")
    time: int = Field(..., ge=0, le=23, description="Hour in military time (0-23)")


def get_session_manager():
    global session_manager_instance
    if not session_manager_instance:
        session_manager_instance = GatorGuidesSessions(
            host=settings.DATABASE_HOST,
            database=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD
        )
    return session_manager_instance

# Creates new tutoring session
@router.post("/sessions", response_model=Dict[str, Any])
async def create_session(request: CreateSessionRequest, session_mgr: GatorGuidesSessions = Depends(get_session_manager)):
    try:
        session = session_mgr.create_session(
            uid=request.uid,
            tid=request.tid,
            tags_id=request.tagsID,
            day=request.day,
            time=request.time
        )
        
        if session:
            logger.info(f"Session created: {session['sid']}")
            return session
        else:
            raise HTTPException(status_code=400, detail="Failed to create session")
            
    except Exception as e:
        logger.error(f"Create session error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Gets session info by session ID
@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: int, session_mgr: GatorGuidesSessions = Depends(get_session_manager)):
    try:
        session = session_mgr.get_session(session_id)
        
        if session:
            return session
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Marks session as started with timestamp
@router.put("/sessions/{session_id}/start")
async def start_session(session_id: int, session_mgr: GatorGuidesSessions = Depends(get_session_manager)):
    try:
        success = session_mgr.start_session(session_id)
        
        if success:
            return {"message": "Session started successfully", "sid": session_id}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to start session. It may have already been started or doesn't exist."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start session error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Marks session as ended with timestamp
@router.put("/sessions/{session_id}/end")
async def end_session(session_id: int, session_mgr: GatorGuidesSessions = Depends(get_session_manager)):
    try:
        success = session_mgr.end_session(session_id)
        
        if success:
            return {"message": "Session ended successfully", "sid": session_id}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to end session. It may have already been ended or doesn't exist."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"End session error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Gets all sessions for a specific user
@router.get("/users/{uid}/sessions", response_model=List[Dict[str, Any]])
async def get_user_sessions(uid: int, session_mgr: GatorGuidesSessions = Depends(get_session_manager)):
    try:
        sessions = session_mgr.get_user_sessions(uid)
        return sessions
            
    except Exception as e:
        logger.error(f"Get user sessions error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Gets all sessions for a specific tutor
@router.get("/tutors/{tid}/sessions", response_model=List[Dict[str, Any]])
async def get_tutor_sessions(tid: int, session_mgr: GatorGuidesSessions = Depends(get_session_manager)):
    try:
        sessions = session_mgr.get_tutor_sessions(tid)
        return sessions
            
    except Exception as e:
        logger.error(f"Get tutor sessions error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))