from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from dependencies import get_auth_manager, get_session_manager
from db.Tutors import GatorGuidesTutors
from db.Users import GatorGuidesUsers
from db.Auth import GatorGuidesAuth
from core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
tutors_instance = None
users_instance = None

class CreateTutorRequest(BaseModel):
    uid: int = Field(..., description="User ID to convert to tutor")
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    status: str = Field(default='available', description="'available', 'away', or 'busy'")

class UpdateVerificationRequest(BaseModel):
    status: str = Field(..., description="'unapproved', 'pending', or 'approved'")

class AddTagsRequest(BaseModel):
    tagIds: List[int] = Field(..., description="List of tag IDs for tutor expertise")

class CreateRatingRequest(BaseModel):
    tid: int = Field(..., description="Tutor ID")
    sid: int = Field(..., description="Session ID")
    rating: float = Field(..., ge=0.0, le=5.0, description="Rating value (0-5)")

def get_tutors_manager():
    global tutors_instance
    if not tutors_instance:
        tutors_instance = GatorGuidesTutors()
    return tutors_instance

def get_users_manager():
    global users_instance
    if not users_instance:
        users_instance = GatorGuidesUsers()
    return users_instance

async def get_current_user(authorization: str = Header(None), auth_mgr: GatorGuidesAuth = Depends(get_auth_manager)) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication format")
    
    session_id = authorization.replace("Bearer ", "")
    uid = auth_mgr.validate_session(session_id)
    
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return uid

async def get_current_admin(current_user: int = Depends(get_current_user), users_mgr: GatorGuidesUsers = Depends(get_users_manager)) -> int:
    user = users_mgr.get_user(current_user)
    
    if not user or user['type'] != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return current_user

# Returns top 10 tutors based on ratings
@router.get("/tutors/top", response_model=List[Dict[str, Any]])
async def get_top_tutors(tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        results = tutors_mgr.get_top_tutors(limit=10)
        return results
    except Exception as e:
        logger.error(f"Top tutors error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Get **ALL** tutors (for student dashboard "Available Tutors" list)
@router.get("/tutors", response_model=List[Dict[str, Any]])
async def get_all_tutors(
        tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)
):
    try:
        results = tutors_mgr.get_all_tutors()
        return results
    except Exception as e:
        logger.error(f"Get all tutors error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Get tutor by tutor ID
@router.get("/tutors/{tid}", response_model=Dict[str, Any])
async def get_tutor(tid: int, tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        tutor = tutors_mgr.get_tutor(tid)
        
        if tutor:
            return tutor
        else:
            raise HTTPException(status_code=404, detail="Tutor not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tutor error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Get tutor by user ID
@router.get("/tutors/by-user/{uid}", response_model=Dict[str, Any])
async def get_tutor_by_user_id(uid: int, tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        tutor = tutors_mgr.get_tutor_by_uid(uid)
        
        if tutor:
            return tutor
        else:
            raise HTTPException(status_code=404, detail="Tutor not found for this user")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tutor by uid error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Create a tutor from existing user
@router.post("/tutors", response_model=Dict[str, Any])
async def create_tutor(request: CreateTutorRequest, current_user: int = Depends(get_current_user), tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        if current_user != request.uid:
            raise HTTPException(
                status_code=403,
                detail="You can only create a tutor profile for yourself"
            )
        
        tutor = tutors_mgr.create_tutor(
            uid=request.uid,
            rating=request.rating,
            status=request.status
        )
        
        if tutor:
            logger.info(f"Tutor created: tid={tutor['tid']}, uid={tutor['uid']}")
            return tutor
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to create tutor. User may not exist or is already a tutor."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create tutor error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Change tutor verification status
@router.put("/tutors/{tid}/verification", response_model=Dict[str, Any])
async def update_verification(tid: int, request: UpdateVerificationRequest, current_admin: int = Depends(get_current_admin), tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        success = tutors_mgr.update_verification_status(tid, request.status)
        
        if success:
            logger.info(f"Admin {current_admin} updated tutor {tid} verification to {request.status}")
            return {
                "message": f"Verification status updated to '{request.status}'",
                "tid": tid
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Update failed. Tutor may not exist or invalid status."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update verification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Add tags to tutor
@router.post("/tutors/{tid}/tags", response_model=Dict[str, Any])
async def add_tutor_tags(tid: int, request: AddTagsRequest, current_user: int = Depends(get_current_user), tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        tutor = tutors_mgr.get_tutor(tid)
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor not found")
        
        if current_user != tutor['uid']:
            raise HTTPException(
                status_code=403,
                detail="You can only add tags to your own tutor profile"
            )
        
        success = tutors_mgr.add_tutor_tags(tid, request.tagIds)
        
        if success:
            return {
                "message": "Tags added successfully",
                "tid": tid,
                "tagIds": request.tagIds
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to add tags. Tutor may not exist."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add tags error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
# Submit tutor rating
@router.post("/tutors/ratings", response_model=Dict[str, Any])
async def create_rating(request: CreateRatingRequest, current_user: int = Depends(get_current_user),tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        if not tutors_mgr.user_can_rate_session(current_user, request.sid):
            raise HTTPException(
                status_code=403,
                detail="Cannot rate this session."
            )
        
        rating = tutors_mgr.create_rating(
            tid=request.tid,
            uid=current_user,
            sid=request.sid,
            rating=request.rating
        )
        
        if rating:
            logger.info(f"Rating submitted: tid={request.tid}, uid={current_user}, rating={request.rating}")
            return rating
        else:
            raise HTTPException(status_code=400, detail="Failed to submit rating")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create rating error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Get count of tutor's ratings
@router.get("/tutors/{tid}/rating-count", response_model=Dict[str, Any])
async def get_rating_count(tid: int, tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        count = tutors_mgr.get_tutor_rating_count(tid)
        return {
            "tid": tid,
            "ratingCount": count
        }
    except Exception as e:
        logger.error(f"Get rating count error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Check if user can still rate a session
@router.get("/sessions/{sid}/can-rate", response_model=Dict[str, Any])
async def check_can_rate(sid: int, current_user: int = Depends(get_current_user), tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        can_rate = tutors_mgr.user_can_rate_session(current_user, sid)
        return {
            "canRate": can_rate,
            "message": "You can rate this session" if can_rate else "Cannot rate this session"
        }
    except Exception as e:
        logger.error(f"Check can rate error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))