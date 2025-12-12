from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dependencies import get_auth_manager, get_tutors_manager, get_posts_manager
from db.Posts import GatorGuidesPosts
from db.Tutors import GatorGuidesTutors
from db.Auth import GatorGuidesAuth
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CreatePostRequest(BaseModel):
    tid: int = Field(..., description="Tutor ID")
    tagsID: int = Field(..., description="Course tag ID")
    content: str = Field(..., min_length=1, max_length=5000, description="Post content")

class UpdatePostRequest(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="Updated content")
    tagsID: Optional[int] = Field(None, description="Updated course tag ID")

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

# Get single post by ID
@router.get("/posts/{pid}", response_model=Dict[str, Any])
async def get_post(pid: int, posts_mgr: GatorGuidesPosts = Depends(get_posts_manager)):
    try:
        post = posts_mgr.get_post(pid)
        
        if post:
            return post
        else:
            raise HTTPException(status_code=404, detail="Post not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get post error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Get posts by tutor ID
@router.get("/tutors/{tid}/posts", response_model=List[Dict[str, Any]])
async def get_tutor_posts(tid: int, limit: int = 50, posts_mgr: GatorGuidesPosts = Depends(get_posts_manager)):
    try:
        posts = posts_mgr.get_posts_by_tutor(tid, limit=limit)
        return posts
    except Exception as e:
        logger.error(f"Get tutor posts error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Creates post after verifying tutor and tag exist
@router.post("/posts", response_model=Dict[str, Any])
async def create_post(request: CreatePostRequest, current_user: int = Depends(get_current_user), posts_mgr: GatorGuidesPosts = Depends(get_posts_manager), tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        tutor = tutors_mgr.get_tutor(request.tid)
        
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor not found")
        
        # Verify current user owns this profile
        if current_user != tutor['uid']:
            raise HTTPException(
                status_code=403,
                detail="You can only create posts for your own tutor profile"
            )
        
        # Create the post
        post = posts_mgr.create_post(
            tid=request.tid,
            tags_id=request.tagsID,
            content=request.content
        )
        
        if post:
            logger.info(f"Post created: PID {post['pid']} by TID {request.tid}")
            return post
        else:
            raise HTTPException(status_code=400, detail="Failed to create post")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create post error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Update post tags and contents
@router.put("/posts/{pid}", response_model=Dict[str, Any])
async def update_post(pid: int, request: UpdatePostRequest, current_user: int = Depends(get_current_user), posts_mgr: GatorGuidesPosts = Depends(get_posts_manager), tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        tid = posts_mgr.get_tutor_id_from_post(pid)
        
        if not tid:
            raise HTTPException(status_code=404, detail="Post not found")
        
        tutor = tutors_mgr.get_tutor(tid)
        
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor not found")
        
        # Verify current user owns this profile
        if current_user != tutor['uid']:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own posts"
            )
        
        # Update the post
        success = posts_mgr.update_post(
            pid=pid,
            content=request.content,
            tags_id=request.tagsID
        )
        
        if success:
            # Get updated post
            post = posts_mgr.get_post(pid)
            logger.info(f"Post updated: PID {pid}")
            return post
        else:
            raise HTTPException(
                status_code=400,
                detail="Update failed. Post may not exist or no fields were changed."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update post error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Delete post
@router.delete("/posts/{pid}", response_model=Dict[str, Any])
async def delete_post(pid: int, current_user: int = Depends(get_current_user), posts_mgr: GatorGuidesPosts = Depends(get_posts_manager), tutors_mgr: GatorGuidesTutors = Depends(get_tutors_manager)):
    try:
        tid = posts_mgr.get_tutor_id_from_post(pid)
        
        if not tid:
            raise HTTPException(status_code=404, detail="Post not found")
        
        tutor = tutors_mgr.get_tutor(tid)
        
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor not found")
        
        # Verify current user owns this profile
        if current_user != tutor['uid']:
            raise HTTPException(
                status_code=403,
                detail="You can only delete your own posts"
            )
        
        # Delete the post
        success = posts_mgr.delete_post(pid)
        
        if success:
            logger.info(f"Post deleted: PID {pid}")
            return {"message": "Post deleted successfully", "pid": pid}
        else:
            raise HTTPException(status_code=404, detail="Post not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete post error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))