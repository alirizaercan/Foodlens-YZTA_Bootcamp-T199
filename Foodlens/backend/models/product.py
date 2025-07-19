"""
Product Model for FoodLens Application
Food product information and nutritional data management.
"""

from datetime import datetime
from typing import Optional, List
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, DECIMAL, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .user import Base

class Product(Base):
    """
    Product model for food product information and nutritional data.
    """
    __tablename__ = 'products'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    barcode = Column(String(50), unique=True, index=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100))
    category = Column(String(100))
    
    # Nutritional information (per 100g)
    energy_kcal = Column(DECIMAL(8, 2))
    energy_kj = Column(DECIMAL(8, 2))
    fat = Column(DECIMAL(6, 2))
    saturated_fat = Column(DECIMAL(6, 2))
    carbohydrates = Column(DECIMAL(6, 2))
    sugars = Column(DECIMAL(6, 2))
    fiber = Column(DECIMAL(6, 2))
    protein = Column(DECIMAL(6, 2))
    salt = Column(DECIMAL(6, 2))
    sodium = Column(DECIMAL(6, 2))
    
    # Additional nutritional data
    nutrition_data = Column(JSONB)  # Flexible storage for other nutrients
    
    # Product classification
    nutri_score = Column(String(1))  # A, B, C, D, E
    nova_group = Column(Integer)  # 1, 2, 3, 4
    
    # Ingredients and allergens
    ingredients = Column(Text)
    allergens = Column(ARRAY(String(50)))
    additives = Column(ARRAY(String(50)))
    
    # Product metadata
    serving_size = Column(DECIMAL(6, 2))  # in grams
    packaging = Column(String(100))
    countries = Column(ARRAY(String(50)))
    data_source = Column(String(50), default='manual')  # openfoodfacts, manual, etc.
    
    # Quality and verification
    is_verified = Column(Boolean, default=False)
    quality_score = Column(DECIMAL(3, 2))  # 0.00 to 1.00
    
    # Images
    image_url = Column(String(500))
    ingredient_image_url = Column(String(500))
    nutrition_image_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="product")
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> dict:
        """Convert product to dictionary."""
        return {
            'id': str(self.id),
            'barcode': self.barcode,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'energy_kcal': float(self.energy_kcal) if self.energy_kcal else None,
            'energy_kj': float(self.energy_kj) if self.energy_kj else None,
            'fat': float(self.fat) if self.fat else None,
            'saturated_fat': float(self.saturated_fat) if self.saturated_fat else None,
            'carbohydrates': float(self.carbohydrates) if self.carbohydrates else None,
            'sugars': float(self.sugars) if self.sugars else None,
            'fiber': float(self.fiber) if self.fiber else None,
            'protein': float(self.protein) if self.protein else None,
            'salt': float(self.salt) if self.salt else None,
            'sodium': float(self.sodium) if self.sodium else None,
            'nutrition_data': self.nutrition_data,
            'nutri_score': self.nutri_score,
            'nova_group': self.nova_group,
            'ingredients': self.ingredients,
            'allergens': self.allergens,
            'additives': self.additives,
            'serving_size': float(self.serving_size) if self.serving_size else None,
            'packaging': self.packaging,
            'countries': self.countries,
            'data_source': self.data_source,
            'is_verified': self.is_verified,
            'quality_score': float(self.quality_score) if self.quality_score else None,
            'image_url': self.image_url,
            'ingredient_image_url': self.ingredient_image_url,
            'nutrition_image_url': self.nutrition_image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', brand='{self.brand}')>"
