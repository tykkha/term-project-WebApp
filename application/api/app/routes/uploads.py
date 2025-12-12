from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from pathlib import Path
import logging
import os
from datetime import datetime
from typing import Dict, Any

from dependencies import get_users_manager
from db.Users import GatorGuidesUsers
from db.Auth import GatorGuidesAuth

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = Path("/var/www/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def get_current_user(authorization: str = Header(None)) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication format")
    
    from db.Auth import GatorGuidesAuth
    auth_mgr = GatorGuidesAuth()
    session_id = authorization.replace("Bearer ", "")
    uid = auth_mgr.validate_session(session_id)
    
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return uid

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = UPLOAD_DIR / filename
        
        with open(filepath, "wb") as f:
            f.write(contents)
        
        logger.info(f"File uploaded: {filename}")
        return {
            "filename": filename,
            "url": f"/uploads/{filename}",
            "size": len(contents)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Upload failed")

# Upload profile picture
@router.post("/users/{uid}/profile-picture", response_model=Dict[str, Any])
async def upload_profile_picture(
    uid: int, 
    file: UploadFile = File(...),
    current_user: int = Depends(get_current_user),
    users_mgr: GatorGuidesUsers = Depends(get_users_manager)
):
    try:
        # Verify user is updating their own profile
        if current_user != uid:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own profile picture"
            )
        
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail="File type not allowed. Use jpg, jpeg, png, gif, or webp"
            )
        
        # Read and validate file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail="File too large. Maximum size is 5MB"
            )
        
        # Delete any existing profile pictures for this user
        for ext in ALLOWED_EXTENSIONS:
            old_file = UPLOAD_DIR / f"{uid}{ext}"
            if old_file.exists():
                old_file.unlink()
        
        # Name file as {uid}.{ext} (e.g., 1.png, 35.jpg)
        filename = f"{uid}{file_ext}"
        filepath = UPLOAD_DIR / filename
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(contents)
        
        # Update user profile with new picture URL
        picture_url = f"/uploads/{filename}"
        success = users_mgr.update_user(uid=uid, profile_picture=picture_url)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update profile picture in database"
            )
        
        logger.info(f"Profile picture uploaded for user {uid}: {filename}")
        return {
            "message": "Profile picture uploaded successfully",
            "profilePicture": picture_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile picture upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Upload failed")