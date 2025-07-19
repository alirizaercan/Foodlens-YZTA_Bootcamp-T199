"""
Recommendation Model for FoodLens Application
AI-powered product and recipe recommendations management.
"""

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, DECIMAL, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .user import Base

class Recommendation(Base):
    """
    Recommendation model for AI-powered product and recipe recommendations.
    """
    __tablename__ = 'recommendations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Recommendation type and content
    type = Column(String(50), nullable=False)  # 'product', 'recipe', 'diet_advice', 'challenge'
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(JSONB)  # Flexible content structure
    
    # Recipe-specific fields
    ingredients = Column(JSONB)  # List of ingredients with quantities
    instructions = Column(JSONB)  # Step-by-step cooking instructions
    prep_time = Column(Integer)  # minutes
    cook_time = Column(Integer)  # minutes
    servings = Column(Integer)
    difficulty = Column(String(20))  # easy, medium, hard
    
    # Nutritional information for recipes
    nutrition_per_serving = Column(JSONB)
    
    # Product recommendation fields
    recommended_products = Column(JSONB)  # Product IDs and reasons
    alternative_to = Column(UUID(as_uuid=True), ForeignKey('products.id'))  # Original product
    
    # Personalization and targeting
    target_audience = Column(JSONB)  # User criteria this recommendation is for
    health_benefits = Column(JSONB)  # Claimed health benefits
    dietary_tags = Column(JSONB)  # vegan, gluten-free, low-carb, etc.
    
    # Quality and engagement
    ai_confidence = Column(DECIMAL(3, 2))  # 0.00 to 1.00
    popularity_score = Column(DECIMAL(3, 2))  # 0.00 to 1.00
    effectiveness_score = Column(DECIMAL(3, 2))  # Based on user feedback
    
    # User interaction
    is_saved = Column(Boolean, default=False)
    is_tried = Column(Boolean, default=False)
    user_rating = Column(Integer)  # 1-5 stars
    user_notes = Column(Text)
    
    # Content metadata
    image_url = Column(String(500))
    source = Column(String(100))  # ai_generated, curated, user_submitted
    category = Column(String(50))
    tags = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_shown = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    
    def __init__(self, user_id: uuid.UUID, type: str, title: str, **kwargs):
        self.user_id = user_id
        self.type = type
        self.title = title
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> dict:
        """Convert recommendation to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'servings': self.servings,
            'difficulty': self.difficulty,
            'nutrition_per_serving': self.nutrition_per_serving,
            'recommended_products': self.recommended_products,
            'alternative_to': str(self.alternative_to) if self.alternative_to else None,
            'target_audience': self.target_audience,
            'health_benefits': self.health_benefits,
            'dietary_tags': self.dietary_tags,
            'ai_confidence': float(self.ai_confidence) if self.ai_confidence else None,
            'popularity_score': float(self.popularity_score) if self.popularity_score else None,
            'effectiveness_score': float(self.effectiveness_score) if self.effectiveness_score else None,
            'is_saved': self.is_saved,
            'is_tried': self.is_tried,
            'user_rating': self.user_rating,
            'user_notes': self.user_notes,
            'image_url': self.image_url,
            'source': self.source,
            'category': self.category,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_shown': self.last_shown.isoformat() if self.last_shown else None
        }
    
    def __repr__(self) -> str:
        return f"<Recommendation(id={self.id}, type='{self.type}', title='{self.title}')>"
