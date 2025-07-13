import os
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from .jwt_utils import create_email_verification_token, create_password_reset_token

logger = logging.getLogger(__name__)

# Email configuration from centralized settings
from config import settings
SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = settings.SMTP_PORT
SMTP_USERNAME = settings.SMTP_USERNAME
SMTP_PASSWORD = settings.SMTP_PASSWORD
FROM_EMAIL = settings.FROM_EMAIL
FRONTEND_URL = settings.FRONTEND_URL

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send an email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # If SMTP is not configured, just log the email (for development)
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.info(f"Email would be sent to {to_email}:")
            logger.info(f"Subject: {subject}")
            logger.info(f"Content: {html_content}")
            return True
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = FROM_EMAIL
        message["To"] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_verification_email(email: str, username: str) -> bool:
    """
    Send email verification message
    
    Args:
        email: User's email address
        username: User's username
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create verification token
        token = create_email_verification_token(email)
        verification_url = f"{FRONTEND_URL}/verify-email?token={token}"
        
        # Email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
            <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #333; text-align: center; margin-bottom: 30px;">Welcome to Chatbot!</h1>
                
                <p style="color: #666; font-size: 16px; line-height: 1.6;">
                    Hi {username},
                </p>
                
                <p style="color: #666; font-size: 16px; line-height: 1.6;">
                    Thank you for creating an account! To complete your registration and start using the chatbot, 
                    please verify your email address by clicking the button below:
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px; line-height: 1.6;">
                    If you can't click the button above, copy and paste this link into your browser:
                </p>
                
                <p style="color: #007bff; font-size: 14px; word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                    {verification_url}
                </p>
                
                <p style="color: #666; font-size: 14px; line-height: 1.6; margin-top: 30px;">
                    This verification link will expire in 24 hours. If you didn't create an account, please ignore this email.
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    This is an automated email. Please do not reply to this message.
                </p>
            </div>
        </body>
        </html>
        """
        
        subject = "Verify Your Email Address - Chatbot"
        return send_email(email, subject, html_content)
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False

def send_password_reset_email(email: str, username: str) -> bool:
    """
    Send password reset email
    
    Args:
        email: User's email address
        username: User's username
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create password reset token
        token = create_password_reset_token(email)
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        
        # Email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
            <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #333; text-align: center; margin-bottom: 30px;">Reset Your Password</h1>
                
                <p style="color: #666; font-size: 16px; line-height: 1.6;">
                    Hi {username},
                </p>
                
                <p style="color: #666; font-size: 16px; line-height: 1.6;">
                    We received a request to reset your password for your Chatbot account. 
                    Click the button below to create a new password:
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px; line-height: 1.6;">
                    If you can't click the button above, copy and paste this link into your browser:
                </p>
                
                <p style="color: #dc3545; font-size: 14px; word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                    {reset_url}
                </p>
                
                <p style="color: #666; font-size: 14px; line-height: 1.6; margin-top: 30px;">
                    This password reset link will expire in 1 hour. If you didn't request a password reset, please ignore this email.
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    This is an automated email. Please do not reply to this message.
                </p>
            </div>
        </body>
        </html>
        """
        
        subject = "Reset Your Password - Chatbot"
        return send_email(email, subject, html_content)
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False

def send_welcome_email(email: str, username: str) -> bool:
    """
    Send welcome email after successful email verification
    
    Args:
        email: User's email address
        username: User's username
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Chatbot!</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
            <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #28a745; text-align: center; margin-bottom: 30px;">Welcome to Chatbot!</h1>
                
                <p style="color: #666; font-size: 16px; line-height: 1.6;">
                    Hi {username},
                </p>
                
                <p style="color: #666; font-size: 16px; line-height: 1.6;">
                    Your email has been successfully verified! You can now log in and start using the chatbot.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{FRONTEND_URL}/login" 
                       style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block;">
                        Start Chatting
                    </a>
                </div>
                
                <p style="color: #666; font-size: 16px; line-height: 1.6;">
                    Enjoy exploring the power of AI conversation!
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    This is an automated email. Please do not reply to this message.
                </p>
            </div>
        </body>
        </html>
        """
        
        subject = "Welcome to Chatbot! Your account is ready"
        return send_email(email, subject, html_content)
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False 