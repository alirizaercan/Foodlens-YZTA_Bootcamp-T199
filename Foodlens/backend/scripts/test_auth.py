"""
Test script for FoodLens authentication system
Tests basic authentication functionality including user registration, login, and profile operations.
"""

import sys
import os
import requests
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER = {
    "email": "test@foodlens.com",
    "password": "TestPassword123!",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User"
}

def test_user_registration():
    """Test user registration endpoint"""
    print("Testing user registration...")
    
    url = f"{BASE_URL}/auth/register"
    response = requests.post(url, json=TEST_USER)
    
    if response.status_code == 201:
        print("✓ User registration successful")
        return response.json()
    else:
        print(f"✗ User registration failed: {response.status_code} - {response.text}")
        return None

def test_user_login():
    """Test user login endpoint"""
    print("Testing user login...")
    
    url = f"{BASE_URL}/auth/login"
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    response = requests.post(url, json=login_data)
    
    if response.status_code == 200:
        print("✓ User login successful")
        data = response.json()
        return data.get("access_token")
    else:
        print(f"✗ User login failed: {response.status_code} - {response.text}")
        return None

def test_protected_route(token):
    """Test accessing a protected route"""
    print("Testing protected route...")
    
    url = f"{BASE_URL}/user/profile"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✓ Protected route access successful")
        return response.json()
    else:
        print(f"✗ Protected route access failed: {response.status_code} - {response.text}")
        return None

def test_allergen_endpoints(token):
    """Test allergen-related endpoints"""
    print("Testing allergen endpoints...")
    
    # Get all allergens
    url = f"{BASE_URL}/allergens"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✓ Get allergens successful")
        allergens = response.json()
        print(f"Found {len(allergens)} allergens")
        
        if allergens:
            # Test adding allergen to user
            headers = {"Authorization": f"Bearer {token}"}
            allergen_id = allergens[0]["id"]
            
            url = f"{BASE_URL}/user/allergens"
            data = {"allergen_id": allergen_id, "severity": "moderate"}
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code in [200, 201]:
                print("✓ Add user allergen successful")
            else:
                print(f"✗ Add user allergen failed: {response.status_code} - {response.text}")
        
        return allergens
    else:
        print(f"✗ Get allergens failed: {response.status_code} - {response.text}")
        return None

def cleanup_test_user():
    """Clean up test user (optional)"""
    print("Note: Test user cleanup not implemented (requires admin endpoint)")

def run_tests():
    """Run all authentication tests"""
    print("Starting FoodLens Authentication System Tests")
    print("=" * 50)
    
    # Test server availability
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("✗ Server is not running or health endpoint not available")
            print("Please start the Flask server first: python app.py")
            return
    except requests.exceptions.RequestException:
        print("✗ Cannot connect to server")
        print("Please start the Flask server first: python app.py")
        return
    
    print("✓ Server is running")
    
    # Run tests
    registration_result = test_user_registration()
    if not registration_result:
        print("Registration failed, trying to log in with existing user...")
    
    token = test_user_login()
    if not token:
        print("Login failed, cannot continue with protected route tests")
        return
    
    profile_data = test_protected_route(token)
    if profile_data:
        print(f"User profile: {json.dumps(profile_data, indent=2)}")
    
    allergens = test_allergen_endpoints(token)
    if allergens:
        print(f"Sample allergens: {json.dumps(allergens[:3], indent=2)}")
    
    print("\n" + "=" * 50)
    print("Authentication system tests completed!")
    print("If all tests passed, your authentication system is working correctly.")

if __name__ == "__main__":
    run_tests()
