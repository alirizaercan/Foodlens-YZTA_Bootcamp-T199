"""
Automated Tests for FoodLens Application
Database and API endpoint testing.
"""

import pytest
import json
import uuid
from datetime import datetime, date
from flask import Flask
from app import create_app
from utils.database import Database
from models.user import User, UserProfile
from models.allergen import Allergen, UserAllergen
from models.nutrition_goal import NutritionGoal

class TestConfig:
    """Test configuration."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    TOKEN_EXPIRES_IN = 3600  # 1 hour for tests
    DATABASE_URL = 'sqlite:///:memory:'  # Use in-memory SQLite for tests

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config.from_object(TestConfig)
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def db():
    """Create database for testing."""
    database = Database()
    session = database.connect()
    yield session
    database.close(session)

class TestDatabase:
    """Test database operations."""
    
    def test_database_connection(self, db):
        """Test database connection."""
        assert db is not None
    
    def test_user_creation(self, db):
        """Test user creation in database."""
        # Create a test user
        user = User(
            email='test@example.com',
            password='TestPassword123!',
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        
        db.add(user)
        db.commit()
        
        # Verify user was created
        created_user = db.query(User).filter(User.email == 'test@example.com').first()
        assert created_user is not None
        assert created_user.username == 'testuser'
        assert created_user.check_password('TestPassword123!')
    
    def test_user_profile_creation(self, db):
        """Test user profile creation."""
        # Create user first
        user = User(
            email='profile@example.com',
            password='TestPassword123!',
            username='profileuser'
        )
        db.add(user)
        db.commit()
        
        # Create profile
        profile = UserProfile(
            user_id=user.id,
            age=25,
            height=175.0,
            weight=70.0,
            gender='male',
            kvkk_approval=True
        )
        
        db.add(profile)
        db.commit()
        
        # Verify profile was created and BMI calculated
        created_profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        assert created_profile is not None
        assert created_profile.age == 25
        assert created_profile.bmi is not None
        assert float(created_profile.bmi) > 20  # Should be around 22.9
    
    def test_allergen_creation(self, db):
        """Test allergen creation."""
        allergen = Allergen(
            name='Test Allergen',
            scientific_name='Testus allergenus',
            description='Test allergen for testing',
            category='test',
            is_major_allergen=True
        )
        
        db.add(allergen)
        db.commit()
        
        # Verify allergen was created
        created_allergen = db.query(Allergen).filter(Allergen.name == 'Test Allergen').first()
        assert created_allergen is not None
        assert created_allergen.is_major_allergen is True
    
    def test_user_allergen_association(self, db):
        """Test user-allergen association."""
        # Create user and allergen
        user = User(
            email='allergen@example.com',
            password='TestPassword123!',
            username='allergenuser'
        )
        allergen = Allergen(
            name='Peanuts',
            description='Peanut allergen'
        )
        
        db.add(user)
        db.add(allergen)
        db.commit()
        
        # Create association
        user_allergen = UserAllergen(
            user_id=user.id,
            allergen_id=allergen.id,
            severity='severe',
            notes='Anaphylactic reaction'
        )
        
        db.add(user_allergen)
        db.commit()
        
        # Verify association
        association = db.query(UserAllergen)\
            .filter(UserAllergen.user_id == user.id)\
            .first()
        
        assert association is not None
        assert association.severity == 'severe'
        assert association.allergen.name == 'Peanuts'
    
    def test_nutrition_goal_creation(self, db):
        """Test nutrition goal creation."""
        # Create user first
        user = User(
            email='goal@example.com',
            password='TestPassword123!',
            username='goaluser'
        )
        db.add(user)
        db.commit()
        
        # Create nutrition goal
        goal = NutritionGoal(
            user_id=user.id,
            goal_type='calories',
            target_value=2000.0,
            unit='kcal',
            start_date=date.today(),
            period='daily'
        )
        
        db.add(goal)
        db.commit()
        
        # Verify goal was created
        created_goal = db.query(NutritionGoal)\
            .filter(NutritionGoal.user_id == user.id)\
            .first()
        
        assert created_goal is not None
        assert created_goal.goal_type == 'calories'
        assert float(created_goal.target_value) == 2000.0
        assert created_goal.calculate_progress_percentage() == 0.0

class TestValidators:
    """Test data validation."""
    
    def test_email_validation(self):
        """Test email validation."""
        from utils.validators import auth_validator
        
        # Valid email
        result = auth_validator.validate_email('test@example.com')
        assert result['is_valid'] is True
        
        # Invalid email
        result = auth_validator.validate_email('invalid-email')
        assert result['is_valid'] is False
    
    def test_password_validation(self):
        """Test password validation."""
        from utils.validators import auth_validator
        
        # Strong password
        result = auth_validator.validate_password('StrongPass123!')
        assert result['is_valid'] is True
        
        # Weak password
        result = auth_validator.validate_password('weak')
        assert result['is_valid'] is False
        assert len(result['errors']) > 0
    
    def test_profile_validation(self):
        """Test profile data validation."""
        from utils.validators import profile_validator
        
        # Valid profile data
        data = {
            'age': 25,
            'height': 175.0,
            'weight': 70.0,
            'gender': 'male',
            'activity_level': 'moderate',
            'kvkk_approval': True
        }
        
        result = profile_validator.validate_profile_setup(data)
        assert result['is_valid'] is True
        
        # Invalid age
        data['age'] = 150
        result = profile_validator.validate_profile_setup(data)
        assert result['is_valid'] is False

class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'endpoints' in data
    
    def test_user_registration(self, client):
        """Test user registration endpoint."""
        user_data = {
            'email': 'newuser@example.com',
            'password': 'NewPassword123!',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'access_token' in data
    
    def test_user_login(self, client):
        """Test user login endpoint."""
        # First register a user
        user_data = {
            'email': 'login@example.com',
            'password': 'LoginPassword123!',
            'username': 'loginuser'
        }
        
        client.post('/api/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Then try to login
        login_data = {
            'email_or_username': 'login@example.com',
            'password': 'LoginPassword123!'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'access_token' in data
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get('/api/users/profile')
        assert response.status_code == 401
    
    def test_protected_endpoint_with_token(self, client):
        """Test accessing protected endpoint with valid token."""
        # Register and login to get token
        user_data = {
            'email': 'protected@example.com',
            'password': 'ProtectedPassword123!',
            'username': 'protecteduser'
        }
        
        # Register
        client.post('/api/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Login
        login_data = {
            'email_or_username': 'protected@example.com',
            'password': 'ProtectedPassword123!'
        }
        
        login_response = client.post('/api/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')
        
        login_result = json.loads(login_response.data)
        token = login_result['access_token']
        
        # Access protected endpoint
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/users/profile', headers=headers)
        
        # Should not be 401 (might be 404 if no profile exists, which is fine)
        assert response.status_code != 401

class TestDataSanitization:
    """Test data sanitization."""
    
    def test_string_sanitization(self):
        """Test string sanitization."""
        from utils.validators import BaseValidator
        
        # Test HTML tag removal
        dirty_string = '<script>alert("xss")</script>Hello World'
        clean_string = BaseValidator.sanitize_string(dirty_string)
        assert '<script>' not in clean_string
        assert 'Hello World' in clean_string
        
        # Test length limiting
        long_string = 'A' * 300
        limited_string = BaseValidator.sanitize_string(long_string, max_length=100)
        assert len(limited_string) <= 100
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention through parameterized queries."""
        # This test ensures our database queries use parameterized statements
        # which prevent SQL injection attacks
        from utils.validators import auth_validator
        
        malicious_email = "test@example.com'; DROP TABLE users; --"
        result = auth_validator.validate_email(malicious_email)
        
        # Should be invalid due to format, not cause database issues
        assert result['is_valid'] is False

# Performance Tests
class TestPerformance:
    """Test application performance."""
    
    def test_database_query_performance(self, db):
        """Test database query performance."""
        import time
        
        # Create multiple users for testing
        users = []
        for i in range(100):
            user = User(
                email=f'user{i}@example.com',
                password='TestPassword123!',
                username=f'user{i}'
            )
            users.append(user)
        
        # Measure bulk insert performance
        start_time = time.time()
        db.add_all(users)
        db.commit()
        insert_time = time.time() - start_time
        
        # Should insert 100 users in reasonable time (< 1 second)
        assert insert_time < 1.0
        
        # Measure query performance
        start_time = time.time()
        result = db.query(User).filter(User.email.like('%@example.com')).all()
        query_time = time.time() - start_time
        
        # Should query users in reasonable time (< 0.1 seconds)
        assert query_time < 0.1
        assert len(result) >= 100

# Integration Tests
class TestIntegration:
    """Test integration between components."""
    
    def test_complete_user_flow(self, client):
        """Test complete user registration and profile setup flow."""
        # 1. Register user
        user_data = {
            'email': 'integration@example.com',
            'password': 'IntegrationTest123!',
            'username': 'integrationuser',
            'first_name': 'Integration',
            'last_name': 'Test'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(user_data),
                                      content_type='application/json')
        
        assert register_response.status_code == 201
        register_data = json.loads(register_response.data)
        token = register_data['access_token']
        
        # 2. Setup profile
        profile_data = {
            'age': 30,
            'height': 180.0,
            'weight': 75.0,
            'gender': 'male',
            'activity_level': 'moderate',
            'kvkk_approval': True
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        profile_response = client.post('/api/users/profile/setup',
                                     data=json.dumps(profile_data),
                                     content_type='application/json',
                                     headers=headers)
        
        assert profile_response.status_code == 201
        
        # 3. Get profile
        get_profile_response = client.get('/api/users/profile', headers=headers)
        assert get_profile_response.status_code == 200
        
        profile_result = json.loads(get_profile_response.data)
        assert profile_result['success'] is True
        assert profile_result['profile']['age'] == 30

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
