"""
Analysis Model for FoodLens Application
Product analysis results and AI-generated insights management.
"""

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, DECIMAL, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .user import Base

class Analysis(Base):
    """
    Analysis model for product analysis results and AI-generated insights.
    """
    __tablename__ = 'analyses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    
    # Analysis input and source
    input_type = Column(String(20), nullable=False)  # 'ocr', 'manual', 'barcode'
    input_data = Column(JSONB)  # Raw OCR data, manual input, etc.
    image_url = Column(String(500))  # Original image if from OCR
    
    # Analysis results
    health_score = Column(DECIMAL(3, 2))  # 0.00 to 10.00
    analysis_summary = Column(Text)
    detailed_analysis = Column(JSONB)
    
    # Personalized warnings and insights
    allergen_warnings = Column(JSONB)  # User-specific allergen alerts
    health_insights = Column(JSONB)  # Personalized health recommendations
    nutritional_assessment = Column(JSONB)  # Detailed nutritional breakdown
    
    # AI processing metadata
    ai_model_version = Column(String(50))
    confidence_score = Column(DECIMAL(3, 2))  # 0.00 to 1.00
    processing_time = Column(DECIMAL(6, 3))  # seconds
    
    # Status and quality
    status = Column(String(20), default='completed')  # pending, completed, failed, manual_review
    is_bookmarked = Column(Boolean, default=False)
    user_rating = Column(Integer)  # 1-5 stars
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    product = relationship("Product", back_populates="analyses")
    
    def __init__(self, user_id: uuid.UUID, product_id: uuid.UUID, input_type: str, **kwargs):
        self.user_id = user_id
        self.product_id = product_id
        self.input_type = input_type
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> dict:
        """Convert analysis to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'product_id': str(self.product_id),
            'input_type': self.input_type,
            'input_data': self.input_data,
            'image_url': self.image_url,
            'health_score': float(self.health_score) if self.health_score else None,
            'analysis_summary': self.analysis_summary,
            'detailed_analysis': self.detailed_analysis,
            'allergen_warnings': self.allergen_warnings,
            'health_insights': self.health_insights,
            'nutritional_assessment': self.nutritional_assessment,
            'ai_model_version': self.ai_model_version,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'processing_time': float(self.processing_time) if self.processing_time else None,
            'status': self.status,
            'is_bookmarked': self.is_bookmarked,
            'user_rating': self.user_rating,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
