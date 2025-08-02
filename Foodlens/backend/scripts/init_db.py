"""
Database initialization script for FoodLens Application
This script creates tables and runs initial data seeding.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import Database
from models.user import User
from models.user_profile import UserProfile
from models.allergen import Allergen, UserAllergen
from scripts.seed_allergens import seed_allergens

def init_database():
    """Initialize the database with tables and seed data."""
    try:
        print("Initializing FoodLens database...")
        
        # Create database connection (this automatically creates tables)
        db = Database()
        session = db.connect()
        
        print("Database tables created successfully!")
        
        # Close the session
        db.close(session)
        
        print("Seeding allergen data...")
        # Seed allergens
        seed_allergens()
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
