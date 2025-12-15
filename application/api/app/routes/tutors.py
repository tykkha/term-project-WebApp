from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from dependencies import get_auth_manager, get_users_manager, get_tutors_manager
from db.Tutors import GatorGuidesTutors
from db.Users import GatorGuidesUsers
from db.Auth import GatorGuidesAuth
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

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

class AddAvailabilityRequest(BaseModel):
    day: str = Field(..., description="Day of week")
    startTime: int = Field(..., ge=0, le=23, description="Start hour (0-23)")
    endTime: int = Field(..., ge=0, le=23, description="End hour (0-23)")

class BulkAvailabilityRequest(BaseModel):
    slots: List[Dict[str, Any]] = Field(..., description="List of availability slots")

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
async def create_tutor(request: CreateTutorRequest, current_admin: int = Depends(get_current_admin), tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        tutor = tutors_mgr.create_tutor(
            uid=request.uid,
            rating=request.rating,
            status=request.status
        )
        
        if tutor:
            logger.info(f"Admin {current_admin} created tutor: tid={tutor['tid']}, uid={tutor['uid']}")
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

# Get tutor availability
@router.get("/tutors/{tid}/availability", response_model=List[Dict[str, Any]])
async def get_tutor_availability(tid: int, tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        from db.Availability import GatorGuidesAvailability
        availability_mgr = GatorGuidesAvailability()
        
        availability = availability_mgr.get_tutor_availability(tid)
        return availability
        
    except Exception as e:
        logger.error(f"Get availability error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Add availability slot
@router.post("/tutors/{tid}/availability", response_model=Dict[str, Any])
async def add_tutor_availability(
    tid: int,
    request: AddAvailabilityRequest,
    current_user: int = Depends(get_current_user),
    tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)
):
    try:
        from db.Availability import GatorGuidesAvailability
        availability_mgr = GatorGuidesAvailability()
        
        # Verify the user owns this tutor profile
        tutor = tutors_mgr.get_tutor_by_uid(current_user)
        if not tutor or tutor['tid'] != tid:
            raise HTTPException(status_code=403, detail="You can only manage your own availability")
        
        availability = availability_mgr.add_availability(
            tid=tid,
            day=request.day,
            start_time=request.startTime,
            end_time=request.endTime
        )
        
        if availability:
            return availability
        else:
            raise HTTPException(status_code=400, detail="Failed to add availability")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add availability error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Set bulk availability (replace all)
@router.put("/tutors/{tid}/availability", response_model=Dict[str, Any])
async def set_bulk_availability(
    tid: int,
    request: BulkAvailabilityRequest,
    current_user: int = Depends(get_current_user),
    tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)
):
    try:
        from db.Availability import GatorGuidesAvailability
        availability_mgr = GatorGuidesAvailability()
        
        # Verify the user owns this tutor profile
        tutor = tutors_mgr.get_tutor_by_uid(current_user)
        if not tutor or tutor['tid'] != tid:
            raise HTTPException(status_code=403, detail="You can only manage your own availability")
        
        success = availability_mgr.set_bulk_availability(tid, request.slots)
        
        if success:
            return {"message": "Availability updated successfully", "tid": tid}
        else:
            raise HTTPException(status_code=400, detail="Failed to update availability")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set bulk availability error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Delete availability slot
@router.delete("/tutors/{tid}/availability/{availability_id}", response_model=Dict[str, Any])
async def delete_availability(
    tid: int,
    availability_id: int,
    current_user: int = Depends(get_current_user),
    tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)
):
    try:
        from db.Availability import GatorGuidesAvailability
        availability_mgr = GatorGuidesAvailability()
        
        # Verify the user owns this tutor profile
        tutor = tutors_mgr.get_tutor_by_uid(current_user)
        if not tutor or tutor['tid'] != tid:
            raise HTTPException(status_code=403, detail="You can only manage your own availability")
        
        success = availability_mgr.remove_availability(availability_id, tid)
        
        if success:
            return {"message": "Availability slot removed", "availabilityID": availability_id}
        else:
            raise HTTPException(status_code=404, detail="Availability slot not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete availability error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Check if time is available
@router.get("/tutors/{tid}/availability/check", response_model=Dict[str, Any])
async def check_time_availability(tid: int, day: str, time: int):
    try:
        from db.Availability import GatorGuidesAvailability
        availability_mgr = GatorGuidesAvailability()
        
        is_available = availability_mgr.check_availability(tid, day, time)
        
        return {
            "tid": tid,
            "day": day,
            "time": time,
            "available": is_available
        }
        
    except Exception as e:
        logger.error(f"Check availability error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Get available times for a specific day
@router.get("/tutors/{tid}/availability/day/{day}", response_model=Dict[str, Any])
async def get_available_times(tid: int, day: str):
    try:
        from db.Availability import GatorGuidesAvailability
        availability_mgr = GatorGuidesAvailability()
        
        available_times = availability_mgr.get_available_times_for_day(tid, day)
        
        return {
            "tid": tid,
            "day": day,
            "availableTimes": available_times
        }
        
    except Exception as e:
        logger.error(f"Get available times error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
# Get all pending tutors
@router.get("/tutors/pending", response_model=List[Dict[str, Any]])
async def get_pending_tutors(
    current_admin: int = Depends(get_current_admin),
    tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)
):
    try:
        results = tutors_mgr.get_pending_tutors()
        logger.info(f"Admin {current_admin} retrieved {len(results)} pending tutors")
        return results
    except Exception as e:
        logger.error(f"Get pending tutors error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Reject tutor application
@router.put("/tutors/{tid}/reject", response_model=Dict[str, Any])
async def reject_tutor(
    tid: int,
    current_admin: int = Depends(get_current_admin),
    tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)
):
    try:
        success = tutors_mgr.reject_tutor(tid)
        
        if success:
            logger.info(f"Admin {current_admin} rejected tutor {tid}")
            return {
                "message": "Tutor application rejected",
                "tid": tid,
                "verificationStatus": "unapproved"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Rejection failed. Tutor may not exist or is not in 'pending' status."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reject tutor error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
# Approve tutor application
@router.put("/tutors/{tid}/approve", response_model=Dict[str, Any])
async def approve_tutor(
    tid: int,
    current_admin: int = Depends(get_current_admin),
    tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)
):
    try:
        success = tutors_mgr.approve_tutor(tid)
        
        if success:
            logger.info(f"Admin {current_admin} accepted tutor {tid}")
            return {
                "message": "Tutor application approved",
                "tid": tid,
                "verificationStatus": "approved"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Approval failed. Tutor may not exist or is not in 'pending' status."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approval tutor error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))