"""
User Model for FoodLens Application
User authentication and basic user information management.
"""

from datetime import datetime
from typing import Optional, List
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Boolean, DateTime, Integer, DECIMAL, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

Base = declarative_base()

class User(Base):
    """
    User model for authentication and basic user information.
    """
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    allergens = relationship("UserAllergen", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    nutrition_goals = relationship("NutritionGoal", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, email: str, password: str, username: str, 
                 first_name: Optional[str] = None, last_name: Optional[str] = None):
        self.email = email.lower().strip()
        self.username = username.strip()
        self.first_name = first_name.strip() if first_name else None
        self.last_name = last_name.strip() if last_name else None
        self.set_password(password)
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    def update_last_login(self) -> None:
        """Update the user's last login timestamp."""
        self.last_login = datetime.utcnow()
    
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated (active and verified)."""
        return self.is_active and self.is_verified
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user object to dictionary."""
        user_dict = {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
        
        return user_dict
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
