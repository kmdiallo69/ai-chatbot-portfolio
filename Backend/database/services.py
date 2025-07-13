import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from datetime import datetime, timezone, timedelta

from .models import User, Conversation, Message, APIUsage
from .connection import get_db_session

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def create_or_get_user(session_id: str) -> User:
        """Create a new user or get existing user by session_id"""
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.session_id == session_id).first()
                if not user:
                    user = User(session_id=session_id)
                    session.add(user)
                    session.commit()
                    logger.info(f"Created new user with session_id: {session_id}")
                else:
                    # Update last_active timestamp
                    user.last_active = datetime.now(timezone.utc)
                    session.commit()
                    logger.info(f"Updated last_active for user: {session_id}")
                return user
        except Exception as e:
            logger.error(f"Error creating/getting user: {str(e)}")
            raise
    
    @staticmethod
    def create_conversation(user_id: str, title: Optional[str] = None) -> Conversation:
        """Create a new conversation for a user"""
        try:
            with get_db_session() as session:
                conversation = Conversation(
                    user_id=user_id,
                    title=title or f"Chat {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
                )
                session.add(conversation)
                session.commit()
                logger.info(f"Created new conversation for user: {user_id}")
                return conversation
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
    
    @staticmethod
    def get_user_conversations(user_id: str, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a user"""
        try:
            with get_db_session() as session:
                conversations = session.query(Conversation)\
                    .filter(Conversation.user_id == user_id)\
                    .filter(Conversation.is_active == True)\
                    .order_by(desc(Conversation.updated_at))\
                    .limit(limit)\
                    .all()
                return conversations
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            raise
    
    @staticmethod
    def get_conversation_messages(conversation_id: str, limit: int = 100) -> List[Message]:
        """Get all messages in a conversation"""
        try:
            with get_db_session() as session:
                messages = session.query(Message)\
                    .filter(Message.conversation_id == conversation_id)\
                    .order_by(Message.created_at)\
                    .limit(limit)\
                    .all()
                return messages
        except Exception as e:
            logger.error(f"Error getting conversation messages: {str(e)}")
            raise
    
    @staticmethod
    def create_message(
        conversation_id: str,
        role: str,
        content: str,
        model_used: Optional[str] = None,
        has_image: bool = False,
        image_type: Optional[str] = None,
        token_count: Optional[int] = None
    ) -> Message:
        """Create a new message in a conversation"""
        try:
            with get_db_session() as session:
                message = Message(
                    conversation_id=conversation_id,
                    role=role,
                    content=content,
                    model_used=model_used,
                    has_image=has_image,
                    image_type=image_type,
                    token_count=token_count
                )
                session.add(message)
                
                # Update conversation's updated_at timestamp
                conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
                if conversation:
                    conversation.updated_at = datetime.now(timezone.utc)
                
                session.commit()
                logger.info(f"Created new message in conversation: {conversation_id}")
                return message
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise
    
    @staticmethod
    def create_api_usage_record(
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        model_name: str = "",
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        cost_estimate: Optional[str] = None
    ) -> APIUsage:
        """Record API usage for analytics"""
        try:
            with get_db_session() as session:
                usage = APIUsage(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    message_id=message_id,
                    model_name=model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    cost_estimate=cost_estimate
                )
                session.add(usage)
                session.commit()
                logger.info(f"Created API usage record for model: {model_name}")
                return usage
        except Exception as e:
            logger.error(f"Error creating API usage record: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_session_id(session_id: str) -> Optional[User]:
        """Get user by session_id"""
        try:
            with get_db_session() as session:
                return session.query(User).filter(User.session_id == session_id).first()
        except Exception as e:
            logger.error(f"Error getting user by session_id: {str(e)}")
            raise
    
    # Authentication-specific user methods
    
    @staticmethod
    def create_auth_user(username: str, email: str, password_hash: str, 
                        verification_token: str, verification_expires: datetime) -> str:
        """Create a new authenticated user and return user ID"""
        try:
            with get_db_session() as session:
                user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    email_verification_token=verification_token,
                    email_verification_expires=verification_expires
                )
                session.add(user)
                session.commit()
                session.refresh(user)  # Refresh to ensure all attributes are loaded
                user_id = user.id  # Get the ID while session is still active
                logger.info(f"Created auth user: {username} ({email})")
                return user_id
        except Exception as e:
            logger.error(f"Error creating auth user: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_username_or_email(username_or_email: str) -> Optional[User]:
        """Get user by username or email"""
        try:
            with get_db_session() as session:
                return session.query(User).filter(
                    or_(User.username == username_or_email, User.email == username_or_email)
                ).first()
        except Exception as e:
            logger.error(f"Error getting user by username/email: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        try:
            with get_db_session() as session:
                return session.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        try:
            with get_db_session() as session:
                return session.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            with get_db_session() as session:
                return session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise
    
    @staticmethod
    def update_user_login_success(user_id: str) -> bool:
        """Update user after successful login"""
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.failed_login_attempts = 0
                    user.last_failed_login = None
                    user.last_login = datetime.now(timezone.utc)
                    user.last_active = datetime.now(timezone.utc)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating user login success: {str(e)}")
            raise
    
    @staticmethod
    def update_user_login_failure(user_id: str, max_attempts: int = 5) -> bool:
        """Update user after failed login attempt"""
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.failed_login_attempts += 1
                    user.last_failed_login = datetime.now(timezone.utc)
                    
                    # Lock account if max attempts reached
                    if user.failed_login_attempts >= max_attempts:
                        user.is_locked = True
                    
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating user login failure: {str(e)}")
            raise
    
    @staticmethod
    def verify_user_email(email: str, token: str) -> bool:
        """Verify user's email address"""
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.email == email).first()
                if user and user.email_verification_token == token:
                    if user.email_verification_expires and user.email_verification_expires > datetime.now(timezone.utc):
                        user.email_verified = True
                        user.email_verification_token = None
                        user.email_verification_expires = None
                        session.commit()
                        logger.info(f"Email verified for user: {email}")
                        return True
                return False
        except Exception as e:
            logger.error(f"Error verifying user email: {str(e)}")
            raise
    
    @staticmethod
    def update_user_last_active(user_id: str) -> bool:
        """Update user's last active timestamp"""
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.last_active = datetime.now(timezone.utc)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating user last active: {str(e)}")
            raise
    
    @staticmethod
    def get_conversation_by_id(conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        try:
            with get_db_session() as session:
                return session.query(Conversation).filter(Conversation.id == conversation_id).first()
        except Exception as e:
            logger.error(f"Error getting conversation by ID: {str(e)}")
            raise
    
    @staticmethod
    def delete_conversation(conversation_id: str) -> bool:
        """Soft delete a conversation (set is_active to False)"""
        try:
            with get_db_session() as session:
                conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
                if conversation:
                    conversation.is_active = False
                    session.commit()
                    logger.info(f"Soft deleted conversation: {conversation_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            raise
    
    @staticmethod
    def get_chat_statistics(user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get chat statistics for analytics"""
        try:
            with get_db_session() as session:
                stats = {}
                
                # Base queries
                user_query = session.query(User)
                conversation_query = session.query(Conversation)
                message_query = session.query(Message)
                
                # Filter by user if specified
                if user_id:
                    conversation_query = conversation_query.filter(Conversation.user_id == user_id)
                    message_query = message_query.join(Conversation).filter(Conversation.user_id == user_id)
                
                # Count statistics
                stats['total_users'] = user_query.count()
                stats['total_conversations'] = conversation_query.filter(Conversation.is_active == True).count()
                stats['total_messages'] = message_query.count()
                stats['user_messages'] = message_query.filter(Message.role == 'user').count()
                stats['assistant_messages'] = message_query.filter(Message.role == 'assistant').count()
                
                # Recent activity (last 7 days)
                from datetime import timedelta
                week_ago = datetime.now(timezone.utc) - timedelta(days=7)
                stats['recent_conversations'] = conversation_query.filter(Conversation.created_at >= week_ago).count()
                stats['recent_messages'] = message_query.filter(Message.created_at >= week_ago).count()
                
                return stats
        except Exception as e:
            logger.error(f"Error getting chat statistics: {str(e)}")
            raise 