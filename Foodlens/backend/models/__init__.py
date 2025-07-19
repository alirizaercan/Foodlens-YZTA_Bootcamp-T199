"""
Models package for FoodLens Application
Exports all database models and the Base class.
"""

from .user import User, Base
from .user_profile import UserProfile
from .allergen import Allergen, UserAllergen
from .nutrition_goal import NutritionGoal
from .product import Product
from .analysis import Analysis
from .recommendation import Recommendation

# Export Base for database initialization
__all__ = [
    'Base',
    'User',
    'UserProfile', 
    'Allergen',
    'UserAllergen',
    'NutritionGoal',
    'Product',
    'Analysis',
    'Recommendation'
]
