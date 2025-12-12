from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from dependencies import get_auth_manager, get_session_manager
import re
from pathlib import Path
from datetime import datetime
from db.Users import GatorGuidesUsers
from db.Auth import GatorGuidesAuth
from core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Upload configuration
UPLOAD_DIR = Path("/var/www/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
users_instance = None

class RegisterRequest(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=255)
    lastName: str = Field(..., min_length=1, max_length=255)
    email: str
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    profilePicture: Optional[str] = None
    bio: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Simple email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

class LoginRequest(BaseModel):
    email: str
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

class LogoutRequest(BaseModel):
    sessionID: str = Field(..., description="Session ID to logout")

class UpdateUserRequest(BaseModel):
    firstName: Optional[str] = Field(None, min_length=1, max_length=255)
    lastName: Optional[str] = Field(None, min_length=1, max_length=255)
    profilePicture: Optional[str] = None
    bio: Optional[str] = None

def get_users_manager():
    global users_instance
    if not users_instance:
        users_instance = GatorGuidesUsers()
    return users_instance

async def get_current_user(authorization: str = Header(None), auth_mgr: GatorGuidesAuth = Depends(get_auth_manager)) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # "Bearer <sessionID>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication format")
    
    session_id = authorization.replace("Bearer ", "")
    uid = auth_mgr.validate_session(session_id)
    
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return uid

# Register a new user
@router.post("/register", response_model=Dict[str, Any])
async def register_user(request: RegisterRequest, users_mgr: GatorGuidesUsers = Depends(get_users_manager)):
    try:
        user = users_mgr.create_user(
            first_name=request.firstName,
            last_name=request.lastName,
            email=request.email,
            password=request.password,
            user_type='user',
            profile_picture=request.profilePicture,
            bio=request.bio
        )
        
        if user:
            logger.info(f"User registered: {user['email']}")
            return {
                "message": "User registered successfully",
                "user": user
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Registration failed. Email may already be in use."
            )
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Login user
@router.post("/login", response_model=Dict[str, Any])
async def login_user(request: LoginRequest, users_mgr: GatorGuidesUsers = Depends(get_users_manager), auth_mgr: GatorGuidesAuth = Depends(get_auth_manager)):
    try:
        user = users_mgr.authenticate_user(request.email, request.password)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Create session
        session_id = auth_mgr.create_session(user['uid'])
        
        if not session_id:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        logger.info(f"User logged in: {user['email']}")
        return {
            "message": "Login successful",
            "user": user,
            "sessionID": session_id
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Logout user
@router.post("/logout", response_model=Dict[str, Any])
async def logout_user(request: LogoutRequest, auth_mgr: GatorGuidesAuth = Depends(get_auth_manager)):
    try:
        success = auth_mgr.delete_session(request.sessionID)
        
        if success:
            logger.info("User logged out successfully")
            return {"message": "Logout successful"}
        else:
            return {"message": "Logout successful"}
            
    except Exception as e:
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Get user by ID (profile)
@router.get("/users/{uid}", response_model=Dict[str, Any])
async def get_user(uid: int, users_mgr: GatorGuidesUsers = Depends(get_users_manager)):
    try:
        user = users_mgr.get_user(uid)
        
        if user:
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Update user information (profile)
@router.put("/users/{uid}", response_model=Dict[str, Any])
async def update_user(uid: int, request: UpdateUserRequest, current_user: int = Depends(get_current_user), users_mgr: GatorGuidesUsers = Depends(get_users_manager)):
    try:
        if current_user != uid:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own profile"
            )
        
        success = users_mgr.update_user(
            uid=uid,
            first_name=request.firstName,
            last_name=request.lastName,
            profile_picture=request.profilePicture,
            bio=request.bio
        )
        
        if success:
            return {"message": "User updated successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Update failed. User may not exist or no fields were changed."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

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
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"profile_{uid}_{timestamp}{file_ext}"
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