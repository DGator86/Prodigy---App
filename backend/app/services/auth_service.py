"""
Authentication service.
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta

from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, LoginResponse
from ..core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_token_data,
)
from ..core.config import settings


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if email exists
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            name=user_data.name,
            height_in=user_data.height_in,
            weight_lb=user_data.weight_lb,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    def create_token_for_user(self, user: User) -> str:
        """Create JWT token for user."""
        token_data = {
            "sub": user.id,
            "email": user.email,
        }
        
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(token_data, expires)
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        token_data = get_token_data(token)
        
        if not token_data:
            return None
        
        return self.get_user_by_id(token_data.user_id)
