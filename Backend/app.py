import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import base64
from typing import Optional

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
    description="An AI chatbot with text and image capabilities",
    version="1.0.0"
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
    prompt: str = Field(..., min_length=1, max_length=2000, description="User's message")
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
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
    return HealthResponse(status="healthy", version="1.0.0")

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_request: ChatRequest):
    """
    Endpoint to receive a text prompt and return AI response
    """
    try:
        logger.info(f"Received chat request: {chat_request.prompt[:50]}...")
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and knowledgeable assistant. Provide accurate, concise, and helpful responses."
                },
                {
                    "role": "user",
                    "content": chat_request.prompt
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
    file: Optional[UploadFile] = File(None)
):
    """
    Endpoint to process text with optional image upload
    """
    try:
        logger.info(f"Received image chat request: {prompt[:50]}...")
        
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
async def legacy_chat(chat_request: ChatRequest):
    """Legacy endpoint for backward compatibility"""
    return await chat_with_ai(chat_request)

# Legacy upload endpoint for backward compatibility
@app.post("/uploadfile/", response_model=ChatResponse)
async def legacy_upload(
    prompt: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """Legacy upload endpoint for backward compatibility"""
    return await chat_with_image(prompt, file)
