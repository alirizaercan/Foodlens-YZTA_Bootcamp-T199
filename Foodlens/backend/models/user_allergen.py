"""
UserAllergen model for tracking user-allergen relationships
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class UserAllergen(Base):
    """Model for user-allergen relationships"""
    
    __tablename__ = 'user_allergens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    allergen_id = Column(Integer, ForeignKey('allergens.id'), nullable=False)
    
    # Severity level for this specific user (can override default allergen severity)
    user_severity_level = Column(Text, nullable=True)  # 'mild', 'moderate', 'severe'
    
    # Additional notes from the user about their specific reaction
    notes = Column(Text, nullable=True)
    
    # Whether this allergen is currently active for the user
    is_active = Column(Boolean, default=True, nullable=False)
    
    # When this allergen was added to the user's profile
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_allergens")
    allergen = relationship("Allergen", back_populates="user_allergens")
    
    def __init__(self, user_id, allergen_id, user_severity_level=None, notes=None, is_active=True):
        self.user_id = user_id
        self.allergen_id = allergen_id
        self.user_severity_level = user_severity_level
        self.notes = notes
        self.is_active = is_active
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'allergen_id': self.allergen_id,
            'user_severity_level': self.user_severity_level,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'allergen': self.allergen.to_dict() if self.allergen else None
        }
    
    def update_severity(self, severity_level):
        """Update user-specific severity level"""
        valid_levels = ['mild', 'moderate', 'severe']
        if severity_level in valid_levels:
            self.user_severity_level = severity_level
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError(f"Invalid severity level. Must be one of: {valid_levels}")
    
    def update_notes(self, notes):
        """Update user notes about the allergen"""
        self.notes = notes
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate this allergen for the user"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activate this allergen for the user"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<UserAllergen user_id={self.user_id} allergen_id={self.allergen_id} active={self.is_active}>"
