from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from db.Tutors import GatorGuidesTutors
from core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
tutors_instance = None


class CreateTutorRequest(BaseModel):
    uid: int = Field(..., description="User ID to convert to tutor")
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    status: str = Field(default='available', description="'available', 'away', or 'busy'")


class UpdateVerificationRequest(BaseModel):
    status: str = Field(..., description="'unapproved', 'pending', or 'approved'")


class AddTagsRequest(BaseModel):
    tagIds: List[int] = Field(..., description="List of tag IDs for tutor expertise")


def get_tutors_manager():
    global tutors_instance
    if not tutors_instance:
        tutors_instance = GatorGuidesTutors(
            host=settings.DATABASE_HOST,
            database=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD
        )
    return tutors_instance


# Create a tutor from existing user
@router.post("/tutors", response_model=Dict[str, Any])
async def create_tutor(request: CreateTutorRequest, tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
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
            
    except Exception as e:
        logger.error(f"Create tutor error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Get tutor by ID
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


# Returns top 10 tutors based on ratings 
@router.get("/tutors/top", response_model=List[Dict[str, Any]])
async def get_top_tutors(search_db: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        results = search_db.get_top_tutors(limit=10)
        return results
    except Exception as e:
        logger.error(f"Top tutors error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Change tutor verification status
@router.put("/tutors/{tid}/verification", response_model=Dict[str, Any])
async def update_verification(tid: int, request: UpdateVerificationRequest, tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        success = tutors_mgr.update_verification_status(tid, request.status)
        
        if success:
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


# Add expertise tags to tutor
@router.post("/tutors/{tid}/tags", response_model=Dict[str, Any])
async def add_tutor_tags(tid: int, request: AddTagsRequest, tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
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