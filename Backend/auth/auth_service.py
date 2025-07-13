import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from email_validator import validate_email, EmailNotValidError

from database import User, DatabaseService
from .password_utils import hash_password, verify_password, validate_password, validate_username, generate_secure_token
from .jwt_utils import create_access_token, verify_token, verify_email_verification_token, verify_password_reset_token
from .email_utils import send_verification_email, send_password_reset_email, send_welcome_email
from config import settings

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer()

class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def register_user(username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            username: User's chosen username
            email: User's email address
            password: User's password
        
        Returns:
            Dictionary with registration result
        """
        try:
            # Validate input
            username_valid, username_error = validate_username(username)
            if not username_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=username_error
                )
            
            # Validate email
            try:
                email_info = validate_email(email)
                email = email_info.email
            except EmailNotValidError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email address"
                )
            
            # Validate password
            password_valid, password_error = validate_password(password)
            if not password_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=password_error
                )
            
            # Check if username already exists
            existing_user = DatabaseService.get_user_by_username(username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            
            # Check if email already exists
            existing_email = DatabaseService.get_user_by_email(email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user
            hashed_password = hash_password(password)
            verification_token = generate_secure_token()
            verification_expires = datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)
            
            user_id = DatabaseService.create_auth_user(
                username=username,
                email=email,
                password_hash=hashed_password,
                verification_token=verification_token,
                verification_expires=verification_expires
            )
            
            # Send verification email
            email_sent = send_verification_email(email, username)
            
            logger.info(f"User registered successfully: {username} ({email})")
            
            return {
                "success": True,
                "message": "Registration successful. Please check your email to verify your account.",
                "user_id": user_id,
                "email_sent": email_sent
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed. Please try again."
            )
    
    @staticmethod
    def login_user(username_or_email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user login
        
        Args:
            username_or_email: Username or email address
            password: User's password
        
        Returns:
            Dictionary with login result and access token
        """
        try:
            # Find user by username or email
            user = DatabaseService.get_user_by_username_or_email(username_or_email)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Check if account is locked
            if bool(user.is_locked):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is locked. Please contact support."
                )
            
            # Check if account is active
            if not bool(user.is_active):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated. Please contact support."
                )
            
            # Verify password
            if not verify_password(password, str(user.password_hash)):
                # Update failed login attempts
                DatabaseService.update_user_login_failure(str(user.id), settings.MAX_LOGIN_ATTEMPTS)
                
                # Check if account was locked
                updated_user = DatabaseService.get_user_by_id(str(user.id))
                if updated_user and bool(updated_user.is_locked):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Account locked due to too many failed attempts. Please contact support."
                    )
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Check if email is verified
            if not bool(user.email_verified):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Please verify your email address before logging in."
                )
            
            # Update user on successful login
            DatabaseService.update_user_login_success(str(user.id))
            
            # Create access token
            token_data = {
                "sub": user.id,
                "username": user.username,
                "email": user.email,
                "type": "access"
            }
            
            access_token = create_access_token(token_data)
            
            logger.info(f"User logged in successfully: {user.username}")
            
            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "email_verified": user.email_verified
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed. Please try again."
            )
    
    @staticmethod
    def verify_email(token: str) -> Dict[str, Any]:
        """
        Verify user's email address
        
        Args:
            token: Email verification token
        
        Returns:
            Dictionary with verification result
        """
        try:
            # Verify token
            email = verify_email_verification_token(token)
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired verification token"
                )
            
            user = DatabaseService.get_user_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Check if already verified
            if bool(user.email_verified):
                return {
                    "success": True,
                    "message": "Email already verified"
                }
            
            # Verify email using database service
            verification_success = DatabaseService.verify_user_email(email, token)
            if not verification_success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired verification token"
                )
            
            # Send welcome email
            send_welcome_email(email, str(user.username))
            
            logger.info(f"Email verified successfully: {email}")
            
            return {
                "success": True,
                "message": "Email verified successfully. You can now log in."
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Email verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email verification failed. Please try again."
            )
    
    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """
        Get current authenticated user from JWT token
        
        Args:
            credentials: JWT token from Authorization header
        
        Returns:
            Current user object
        """
        try:
            token = credentials.credentials
            payload = verify_token(token)
            
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            user = DatabaseService.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            if not bool(user.is_active):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account deactivated"
                )
            
            if bool(user.is_locked):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account locked"
                )
            
            # Update last active
            DatabaseService.update_user_last_active(str(user.id))
            
            return user
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

# Dependency function for FastAPI
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    return AuthService.get_current_user(credentials) 