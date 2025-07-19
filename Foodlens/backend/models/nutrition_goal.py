"""
Nutrition Goal Model for FoodLens Application
User nutrition goals and progress tracking management.
"""

from datetime import datetime, date
from typing import Optional
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, DECIMAL, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from .user import Base

class NutritionGoal(Base):
    """
    Nutrition goal model for user goal setting and tracking.
    """
    __tablename__ = 'nutrition_goals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    goal_type = Column(String(50), nullable=False)  # 'calories', 'protein', 'weight_loss', etc.
    target_value = Column(DECIMAL(10, 2))
    current_value = Column(DECIMAL(10, 2), default=0)
    unit = Column(String(20))  # 'kcal', 'g', 'kg', etc.
    period = Column(String(20), default='daily')  # 'daily', 'weekly', 'monthly'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True, index=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="nutrition_goals")
    
    def __init__(self, user_id: uuid.UUID, goal_type: str, target_value: float,
                 unit: str, start_date: date, period: str = 'daily',
                 end_date: Optional[date] = None, notes: Optional[str] = None):
        self.user_id = user_id
        self.goal_type = goal_type
        self.target_value = target_value
        self.unit = unit
        self.period = period
        self.start_date = start_date
        self.end_date = end_date
        self.notes = notes
    
    def calculate_progress_percentage(self) -> float:
        """Calculate progress as a percentage."""
        if not self.target_value or self.target_value == 0:
            return 0.0
        
        progress = (float(self.current_value or 0) / float(self.target_value)) * 100
        return min(progress, 100.0)  # Cap at 100%
    
    def is_goal_achieved(self) -> bool:
        """Check if the goal has been achieved."""
        if not self.target_value:
            return False
        
        return float(self.current_value or 0) >= float(self.target_value)
    
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining to achieve the goal."""
        if not self.end_date:
            return None
        
        today = date.today()
        if self.end_date <= today:
            return 0
        
        return (self.end_date - today).days
    
    def update_progress(self, new_value: float) -> None:
        """Update the current progress value."""
        self.current_value = new_value
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert nutrition goal to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'goal_type': self.goal_type,
            'target_value': float(self.target_value) if self.target_value else None,
            'current_value': float(self.current_value) if self.current_value else 0,
            'unit': self.unit,
            'period': self.period,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'notes': self.notes,
            'progress_percentage': self.calculate_progress_percentage(),
            'is_achieved': self.is_goal_achieved(),
            'days_remaining': self.days_remaining(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"<NutritionGoal(id={self.id}, type='{self.goal_type}', target={self.target_value})>"
