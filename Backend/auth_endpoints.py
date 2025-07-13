from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

from auth import AuthService, get_current_user
from database import User

logger = logging.getLogger(__name__)

# Create router for authentication endpoints
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic models for request/response
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")

class LoginRequest(BaseModel):
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="Password")

class VerifyEmailRequest(BaseModel):
    token: str = Field(..., description="Email verification token")

class AuthResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[dict] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    email_verified: bool
    created_at: str
    last_login: Optional[str] = None

@auth_router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Register a new user
    
    - **username**: Unique username (3-50 characters, alphanumeric + underscore)
    - **email**: Valid email address
    - **password**: Password (min 8 characters, must contain letters and numbers)
    """
    try:
        result = AuthService.register_user(
            username=request.username,
            email=request.email,
            password=request.password
        )
        
        return AuthResponse(
            success=result["success"],
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@auth_router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with username/email and password
    
    - **username_or_email**: Your username or email address
    - **password**: Your password
    
    Returns access token for authenticated requests
    """
    try:
        result = AuthService.login_user(
            username_or_email=request.username_or_email,
            password=request.password
        )
        
        return AuthResponse(
            success=result["success"],
            message="Login successful",
            access_token=result["access_token"],
            token_type=result["token_type"],
            user=result["user"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@auth_router.post("/verify-email", response_model=AuthResponse)
async def verify_email(request: VerifyEmailRequest):
    """
    Verify email address with token
    
    - **token**: Email verification token from email
    """
    try:
        result = AuthService.verify_email(request.token)
        
        return AuthResponse(
            success=result["success"],
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    
    Requires authentication token in Authorization header
    """
    try:
        return UserResponse(
            id=str(current_user.id),
            username=str(current_user.username),
            email=str(current_user.email),
            email_verified=bool(current_user.email_verified),
            created_at=current_user.created_at.isoformat(),
            last_login=current_user.last_login.isoformat() if current_user.last_login is not None else None
        )
        
    except Exception as e:
        logger.error(f"Get user info endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@auth_router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    
    This endpoint invalidates the current session
    """
    try:
        # In a more sophisticated implementation, you might maintain a blacklist of tokens
        # For now, we'll just return success - the frontend should remove the token
        
        logger.info(f"User logged out: {current_user.username}")
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error(f"Logout endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@auth_router.get("/health")
async def auth_health_check():
    """
    Health check for authentication service
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "version": "1.0.0"
    } 