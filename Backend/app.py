import logging
from datetime import datetime
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import base64
from typing import Optional

from config import settings
from auth_endpoints import auth_router
from auth import get_current_user
from database import User, create_tables, health_check as db_health_check
from middleware import RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include authentication router
app.include_router(auth_router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        create_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

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

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        db_healthy = db_health_check()
        if not db_healthy:
            return HealthResponse(status="unhealthy", version="1.0.0")
        return HealthResponse(status="healthy", version="1.0.0")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(status="unhealthy", version="1.0.0")

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_request: ChatRequest, current_user: User = Depends(get_current_user)):
    """
    Endpoint to receive a text prompt and return AI response
    """
    try:
        logger.info(f"Received chat request from user {current_user.username}: {chat_request.message[:50]}...")
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and knowledgeable assistant. Provide accurate, concise, and helpful responses."
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
        
        logger.info("Successfully generated AI response")
        
        return ChatResponse(
            response=response_content,
            model_used="gpt-4o-mini",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, I'm having trouble processing your request. Please try again."
        )

# File upload endpoint with enhanced validation
@app.post("/chat/image", response_model=ChatResponse)
async def chat_with_image(
    prompt: str = Form(..., min_length=1, max_length=2000),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to process text with optional image upload
    """
    try:
        logger.info(f"Received image chat request from user {current_user.username}: {prompt[:50]}...")
        
        # Validate file if provided
        if file:
            # Check file size
            file_content = await file.read()
            if len(file_content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE/1024/1024:.1f}MB"
                )
            
            # Check file type
            if file.content_type not in settings.ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file.content_type} not allowed. Supported types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
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
                        "content": "You are a helpful and knowledgeable assistant. Provide accurate, concise, and helpful responses."
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
        
        logger.info("Successfully generated AI response with image")
        
        return ChatResponse(
            response=response_content,
            model_used=model_used,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in image chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, I'm having trouble processing your request. Please try again."
        )

# Legacy endpoint for backward compatibility
@app.post("/", response_model=ChatResponse)
async def legacy_chat(chat_request: ChatRequest, current_user: User = Depends(get_current_user)):
    """Legacy endpoint for backward compatibility"""
    return await chat_with_ai(chat_request, current_user)

# Legacy upload endpoint for backward compatibility
@app.post("/uploadfile/", response_model=ChatResponse)
async def legacy_upload(
    prompt: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    """Legacy upload endpoint for backward compatibility"""
    return await chat_with_image(prompt, file, current_user)
