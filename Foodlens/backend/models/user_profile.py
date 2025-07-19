"""
User Profile Model for FoodLens Application
Detailed user health and dietary information management.
"""

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, DECIMAL, ARRAY, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .user import Base

class UserProfile(Base):
    """
    User profile model for detailed health and dietary information.
    Based on the form fields shown in the UI mockup.
    """
    __tablename__ = 'user_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True, nullable=False, index=True)
    
    # Physical information from the form
    age = Column(Integer)  # Age field from form
    gender = Column(String(20))
    height = Column(DECIMAL(5, 2))  # Height/Length field from form (in cm)
    weight = Column(DECIMAL(5, 2))  # Weight field from form (in kg)
    
    # Health and lifestyle information
    activity_level = Column(String(20), default='moderate')
    dietary_preferences = Column(ARRAY(String(50)))
    health_conditions = Column(ARRAY(Text))
    medications = Column(ARRAY(Text))
    
    # Calculated fields
    bmi = Column(DECIMAL(4, 2))
    daily_calorie_goal = Column(Integer)
    
    # KVKK approval from form
    kvkk_approval = Column(Boolean, default=False)  # "I approve KVKK" checkbox from form
    
    # Preferences
    notification_preferences = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __init__(self, user_id: uuid.UUID, age: Optional[int] = None, 
                 height: Optional[float] = None, weight: Optional[float] = None,
                 kvkk_approval: bool = False, **kwargs):
        self.user_id = user_id
        self.age = age
        self.height = height
        self.weight = weight
        self.kvkk_approval = kvkk_approval
        
        # Set other optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Calculate BMI if height and weight are provided
        if self.height and self.weight:
            self.calculate_bmi()
    
    def calculate_bmi(self) -> Optional[float]:
        """Calculate and update BMI based on height and weight."""
        if self.height and self.weight and self.height > 0:
            # BMI = weight (kg) / (height (m))^2
            height_m = float(self.height) / 100  # Convert cm to meters
            bmi = float(self.weight) / (height_m ** 2)
            self.bmi = round(bmi, 2)
            return float(self.bmi)
        return None
    
    def get_bmi_category(self) -> Optional[str]:
        """Get BMI category based on WHO standards."""
        if not self.bmi:
            return None
        
        bmi_value = float(self.bmi)
        if bmi_value < 18.5:
            return "Underweight"
        elif 18.5 <= bmi_value < 25:
            return "Normal weight"
        elif 25 <= bmi_value < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def calculate_daily_calories(self) -> Optional[int]:
        """
        Calculate daily calorie needs using Harris-Benedict equation.
        Requires age, weight, height, and gender.
        """
        if not all([self.age, self.weight, self.height, self.gender]):
            return None
        
        # Harris-Benedict equation
        if self.gender.lower() == 'male':
            bmr = 88.362 + (13.397 * float(self.weight)) + (4.799 * float(self.height)) - (5.677 * self.age)
        elif self.gender.lower() == 'female':
            bmr = 447.593 + (9.247 * float(self.weight)) + (3.098 * float(self.height)) - (4.330 * self.age)
        else:
            # Use average if gender is not specified
            bmr_male = 88.362 + (13.397 * float(self.weight)) + (4.799 * float(self.height)) - (5.677 * self.age)
            bmr_female = 447.593 + (9.247 * float(self.weight)) + (3.098 * float(self.height)) - (4.330 * self.age)
            bmr = (bmr_male + bmr_female) / 2
        
        # Activity level multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        multiplier = activity_multipliers.get(self.activity_level, 1.55)
        daily_calories = int(bmr * multiplier)
        self.daily_calorie_goal = daily_calories
        
        return daily_calories
    
    def update_profile(self, **kwargs) -> None:
        """Update profile fields and recalculate derived values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Recalculate BMI if height or weight changed
        if 'height' in kwargs or 'weight' in kwargs:
            self.calculate_bmi()
        
        # Recalculate daily calories if relevant fields changed
        if any(field in kwargs for field in ['age', 'weight', 'height', 'gender', 'activity_level']):
            self.calculate_daily_calories()
        
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert user profile to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'age': self.age,
            'gender': self.gender,
            'height': float(self.height) if self.height else None,
            'weight': float(self.weight) if self.weight else None,
            'bmi': float(self.bmi) if self.bmi else None,
            'bmi_category': self.get_bmi_category(),
            'activity_level': self.activity_level,
            'dietary_preferences': self.dietary_preferences,
            'health_conditions': self.health_conditions,
            'medications': self.medications,
            'daily_calorie_goal': self.daily_calorie_goal,
            'kvkk_approval': self.kvkk_approval,
            'notification_preferences': self.notification_preferences,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, age={self.age})>"
