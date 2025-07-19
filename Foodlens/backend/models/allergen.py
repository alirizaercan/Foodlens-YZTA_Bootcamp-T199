"""
Allergen Model for FoodLens Application
Allergen information and user allergen tracking management.
"""

from datetime import datetime, date
from typing import Optional, List
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ARRAY, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from .user import Base

class Allergen(Base):
    """
    Allergen model for common allergen definitions.
    """
    __tablename__ = 'allergens'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    scientific_name = Column(String(200))
    description = Column(Text)
    category = Column(String(50))
    severity_level = Column(String(20), default='moderate')
    common_sources = Column(ARRAY(Text))
    alternative_names = Column(ARRAY(Text))
    is_major_allergen = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user_allergens = relationship("UserAllergen", back_populates="allergen")
    
    def to_dict(self) -> dict:
        """Convert allergen to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'scientific_name': self.scientific_name,
            'description': self.description,
            'category': self.category,
            'severity_level': self.severity_level,
            'common_sources': self.common_sources,
            'alternative_names': self.alternative_names,
            'is_major_allergen': self.is_major_allergen,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f"<Allergen(id={self.id}, name='{self.name}')>"

class UserAllergen(Base):
    """
    User-specific allergen associations (junction table).
    Links users to their specific allergens with additional information.
    """
    __tablename__ = 'user_allergens'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    allergen_id = Column(Integer, ForeignKey('allergens.id'), nullable=False, index=True)
    severity = Column(String(20), default='moderate')
    notes = Column(Text)
    diagnosed_date = Column(Date)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="allergens")
    allergen = relationship("Allergen", back_populates="user_allergens")
    
    def __init__(self, user_id: uuid.UUID, allergen_id: int, 
                 severity: str = 'moderate', notes: Optional[str] = None,
                 diagnosed_date: Optional[date] = None):
        self.user_id = user_id
        self.allergen_id = allergen_id
        self.severity = severity
        self.notes = notes
        self.diagnosed_date = diagnosed_date
    
    def to_dict(self) -> dict:
        """Convert user allergen association to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'allergen_id': self.allergen_id,
            'allergen_name': self.allergen.name if self.allergen else None,
            'severity': self.severity,
            'notes': self.notes,
            'diagnosed_date': self.diagnosed_date.isoformat() if self.diagnosed_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f"<UserAllergen(user_id={self.user_id}, allergen_id={self.allergen_id})>"
