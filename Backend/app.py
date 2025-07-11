import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import base64
from typing import Optional

# Import authentication modules
from auth import (
    User, UserRegister, UserLogin, UserResponse, Token,
    get_db, create_user, authenticate_user, create_access_token,
    verify_user_email, get_current_verified_user, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize FastAPI app
app = FastAPI(
    title="AI Chatbot API",
    description="An AI chatbot with text and image capabilities and user authentication",
    version="2.0.0"
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    model_used: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str

# Authentication endpoints
@app.post("/auth/register", response_model=dict)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = create_user(db, user_data)
        return {
            "message": "User registered successfully. Please check your email to verify your account.",
            "user_id": user.id,
            "username": user.username
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    try:
        user = authenticate_user(db, user_data.username, user_data.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        
        if not user.is_verified:
            raise HTTPException(
                status_code=401,
                detail="Please verify your email before logging in"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/verify-email")
async def verify_email(verification_token: str, db: Session = Depends(get_db)):
    """Verify user email with token"""
    try:
        user = verify_user_email(db, verification_token)
        return {
            "message": "Email verified successfully. You can now log in.",
            "username": user.username
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=500, detail="Email verification failed")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(status="healthy", version="2.0.0")

# Protected chat endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_verified_user)
):
    """
    Endpoint to receive a text prompt and return AI response (requires authentication)
    """
    try:
        logger.info(f"User {current_user.username} sent chat request: {chat_request.message[:50]}...")
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and knowledgeable assistant. Provide accurate, concise, and helpful responses using markdown formatting when appropriate."
                },
                {
                    "role": "user",
                    "content": chat_request.message
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        response_content = completion.choices[0].message.content or "I apologize, but I couldn't generate a response."
        
        logger.info(f"Successfully generated AI response for user {current_user.username}")
        
        return ChatResponse(
            response=response_content,
            model_used="gpt-4o-mini",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, I'm having trouble processing your request. Please try again."
        )

@app.post("/chat/image", response_model=ChatResponse)
async def chat_with_image(
    prompt: str = Form(..., min_length=1, max_length=2000),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Endpoint to process text with optional image upload (requires authentication)
    """
    try:
        logger.info(f"User {current_user.username} sent image chat request: {prompt[:50]}...")
        
        # Validate file if provided
        if file:
            # Check file size
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE/1024/1024:.1f}MB"
                )
            
            # Check file type
            if file.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file.content_type} not allowed. Supported types: {', '.join(ALLOWED_FILE_TYPES)}"
                )
            
            # Encode image to base64
            base64_image = base64.b64encode(file_content).decode("utf-8")
            
            # Create completion with image
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{file.content_type};base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            model_used = "gpt-4o"
            
        else:
            # Text-only completion
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful and knowledgeable assistant. Provide accurate, concise, and helpful responses using markdown formatting when appropriate."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            model_used = "gpt-4o-mini"
        
        response_content = completion.choices[0].message.content or "I apologize, but I couldn't generate a response."
        
        logger.info(f"Successfully generated AI response with image for user {current_user.username}")
        
        return ChatResponse(
            response=response_content,
            model_used=model_used,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in image chat endpoint for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, I'm having trouble processing your request. Please try again."
        )

# Legacy endpoint for backward compatibility (now protected)
@app.post("/", response_model=ChatResponse)
async def legacy_chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_verified_user)
):
    """Legacy endpoint for backward compatibility (now protected)"""
    return await chat_with_ai(chat_request, current_user)

# Legacy upload endpoint for backward compatibility (now protected)
@app.post("/uploadfile/", response_model=ChatResponse)
async def legacy_upload(
    prompt: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_verified_user)
):
    """Legacy upload endpoint for backward compatibility (now protected)"""
    return await chat_with_image(prompt, file, current_user)
