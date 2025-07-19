"""
Data Validation and Sanitization for FoodLens Application
Input validation, data sanitization, and security utilities.
"""

import re
import html
import bleach
from typing import Dict, Any, List, Optional
from email_validator import validate_email, EmailNotValidError

class BaseValidator:
    """Base validator class with common validation methods."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input by removing harmful content."""
        if not value:
            return ""
        
        # Remove HTML tags and escape remaining content
        cleaned = bleach.clean(value, strip=True)
        cleaned = html.escape(cleaned)
        
        # Limit length
        return cleaned[:max_length].strip()
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> Dict[str, Any]:
        """Validate that a field is not empty."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return {
                'is_valid': False,
                'error': f'{field_name} is required'
            }
        return {'is_valid': True}
    
    @staticmethod
    def validate_length(value: str, min_length: int = 0, max_length: int = 255, field_name: str = 'Field') -> Dict[str, Any]:
        """Validate string length."""
        if len(value) < min_length:
            return {
                'is_valid': False,
                'error': f'{field_name} must be at least {min_length} characters long'
            }
        if len(value) > max_length:
            return {
                'is_valid': False,
                'error': f'{field_name} must be no more than {max_length} characters long'
            }
        return {'is_valid': True}
    
    @staticmethod
    def validate_numeric_range(value: float, min_val: float = None, max_val: float = None, field_name: str = 'Value') -> Dict[str, Any]:
        """Validate numeric range."""
        if min_val is not None and value < min_val:
            return {
                'is_valid': False,
                'error': f'{field_name} must be at least {min_val}'
            }
        if max_val is not None and value > max_val:
            return {
                'is_valid': False,
                'error': f'{field_name} must be no more than {max_val}'
            }
        return {'is_valid': True}

class AuthValidator(BaseValidator):
    """Validator for authentication-related data."""
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """Validate email format and deliverability."""
        try:
            # Basic sanitization
            email = self.sanitize_string(email, 255).lower()
            
            # Check if email is provided
            required_check = self.validate_required(email, 'Email')
            if not required_check['is_valid']:
                return required_check
            
            # Validate email format
            valid = validate_email(email)
            return {
                'is_valid': True,
                'sanitized_email': valid.email
            }
            
        except EmailNotValidError as e:
            return {
                'is_valid': False,
                'error': f'Invalid email format: {str(e)}'
            }
        except Exception as e:
            return {
                'is_valid': False,
                'error': f'Email validation failed: {str(e)}'
            }
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength."""
        errors = []
        
        if not password:
            return {
                'is_valid': False,
                'errors': ['Password is required']
            }
        
        # Length check
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if len(password) > 128:
            errors.append('Password must be no more than 128 characters long')
        
        # Complexity checks
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character')
        
        # Common password check
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        
        if password.lower() in common_passwords:
            errors.append('Password is too common, please choose a stronger password')
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_username(self, username: str) -> Dict[str, Any]:
        """Validate username format."""
        username = self.sanitize_string(username, 50)
        
        # Required check
        required_check = self.validate_required(username, 'Username')
        if not required_check['is_valid']:
            return required_check
        
        # Length check
        length_check = self.validate_length(username, 3, 50, 'Username')
        if not length_check['is_valid']:
            return length_check
        
        # Format check (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return {
                'is_valid': False,
                'error': 'Username can only contain letters, numbers, underscores, and hyphens'
            }
        
        # Cannot start or end with underscore or hyphen
        if username.startswith(('_', '-')) or username.endswith(('_', '-')):
            return {
                'is_valid': False,
                'error': 'Username cannot start or end with underscore or hyphen'
            }
        
        return {
            'is_valid': True,
            'sanitized_username': username
        }
    
    def validate_registration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete registration data."""
        errors = []
        sanitized_data = {}
        
        # Validate email
        email_result = self.validate_email(data.get('email', ''))
        if not email_result['is_valid']:
            errors.append(email_result['error'])
        else:
            sanitized_data['email'] = email_result['sanitized_email']
        
        # Validate password
        password_result = self.validate_password(data.get('password', ''))
        if not password_result['is_valid']:
            errors.extend(password_result['errors'])
        
        # Validate username
        username_result = self.validate_username(data.get('username', ''))
        if not username_result['is_valid']:
            errors.append(username_result['error'])
        else:
            sanitized_data['username'] = username_result['sanitized_username']
        
        # Validate optional name fields
        if data.get('first_name'):
            first_name = self.sanitize_string(data['first_name'], 100)
            if first_name:
                sanitized_data['first_name'] = first_name
        
        if data.get('last_name'):
            last_name = self.sanitize_string(data['last_name'], 100)
            if last_name:
                sanitized_data['last_name'] = last_name
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': sanitized_data
        }

class UserProfileValidator(BaseValidator):
    """Validator for user profile data."""
    
    def validate_age(self, age: int) -> Dict[str, Any]:
        """Validate age value."""
        if not isinstance(age, int):
            try:
                age = int(age)
            except (ValueError, TypeError):
                return {
                    'is_valid': False,
                    'error': 'Age must be a valid number'
                }
        
        return self.validate_numeric_range(age, 13, 120, 'Age')
    
    def validate_height(self, height: float) -> Dict[str, Any]:
        """Validate height in centimeters."""
        if not isinstance(height, (int, float)):
            try:
                height = float(height)
            except (ValueError, TypeError):
                return {
                    'is_valid': False,
                    'error': 'Height must be a valid number'
                }
        
        return self.validate_numeric_range(height, 50, 300, 'Height')
    
    def validate_weight(self, weight: float) -> Dict[str, Any]:
        """Validate weight in kilograms."""
        if not isinstance(weight, (int, float)):
            try:
                weight = float(weight)
            except (ValueError, TypeError):
                return {
                    'is_valid': False,
                    'error': 'Weight must be a valid number'
                }
        
        return self.validate_numeric_range(weight, 20, 500, 'Weight')
    
    def validate_gender(self, gender: str) -> Dict[str, Any]:
        """Validate gender selection."""
        valid_genders = ['male', 'female', 'other', 'prefer_not_to_say']
        gender = gender.lower().strip() if gender else ''
        
        if gender and gender not in valid_genders:
            return {
                'is_valid': False,
                'error': f'Gender must be one of: {", ".join(valid_genders)}'
            }
        
        return {'is_valid': True, 'sanitized_gender': gender}
    
    def validate_activity_level(self, activity_level: str) -> Dict[str, Any]:
        """Validate activity level selection."""
        valid_levels = ['sedentary', 'light', 'moderate', 'active', 'very_active']
        activity_level = activity_level.lower().strip() if activity_level else ''
        
        if activity_level and activity_level not in valid_levels:
            return {
                'is_valid': False,
                'error': f'Activity level must be one of: {", ".join(valid_levels)}'
            }
        
        return {'is_valid': True, 'sanitized_activity_level': activity_level}
    
    def validate_profile_setup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete profile setup data."""
        errors = []
        sanitized_data = {}
        
        # Validate age
        if 'age' in data and data['age'] is not None:
            age_result = self.validate_age(data['age'])
            if not age_result['is_valid']:
                errors.append(age_result['error'])
            else:
                sanitized_data['age'] = int(data['age'])
        
        # Validate height
        if 'height' in data and data['height'] is not None:
            height_result = self.validate_height(data['height'])
            if not height_result['is_valid']:
                errors.append(height_result['error'])
            else:
                sanitized_data['height'] = float(data['height'])
        
        # Validate weight
        if 'weight' in data and data['weight'] is not None:
            weight_result = self.validate_weight(data['weight'])
            if not weight_result['is_valid']:
                errors.append(weight_result['error'])
            else:
                sanitized_data['weight'] = float(data['weight'])
        
        # Validate gender
        if 'gender' in data:
            gender_result = self.validate_gender(data['gender'])
            if not gender_result['is_valid']:
                errors.append(gender_result['error'])
            else:
                sanitized_data['gender'] = gender_result['sanitized_gender']
        
        # Validate activity level
        if 'activity_level' in data:
            activity_result = self.validate_activity_level(data['activity_level'])
            if not activity_result['is_valid']:
                errors.append(activity_result['error'])
            else:
                sanitized_data['activity_level'] = activity_result['sanitized_activity_level']
        
        # Validate KVKK approval
        if 'kvkk_approval' in data:
            sanitized_data['kvkk_approval'] = bool(data['kvkk_approval'])
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': sanitized_data
        }

class ProductValidator(BaseValidator):
    """Validator for product data."""
    
    def validate_barcode(self, barcode: str) -> Dict[str, Any]:
        """Validate product barcode."""
        if not barcode:
            return {'is_valid': True}  # Barcode is optional
        
        barcode = self.sanitize_string(barcode, 50)
        
        # Check if barcode contains only digits
        if not re.match(r'^\d+$', barcode):
            return {
                'is_valid': False,
                'error': 'Barcode must contain only numbers'
            }
        
        # Check barcode length (most common formats)
        valid_lengths = [8, 12, 13, 14]  # EAN-8, UPC-A, EAN-13, ITF-14
        if len(barcode) not in valid_lengths:
            return {
                'is_valid': False,
                'error': f'Barcode must be {" or ".join(map(str, valid_lengths))} digits long'
            }
        
        return {'is_valid': True, 'sanitized_barcode': barcode}
    
    def validate_product_name(self, name: str) -> Dict[str, Any]:
        """Validate product name."""
        name = self.sanitize_string(name, 255)
        
        required_check = self.validate_required(name, 'Product name')
        if not required_check['is_valid']:
            return required_check
        
        length_check = self.validate_length(name, 2, 255, 'Product name')
        if not length_check['is_valid']:
            return length_check
        
        return {'is_valid': True, 'sanitized_name': name}

class NutritionValidator(BaseValidator):
    """Validator for nutrition analysis data."""
    
    def validate_calories(self, calories: int) -> Dict[str, Any]:
        """Validate calorie value."""
        if not isinstance(calories, int):
            try:
                calories = int(calories)
            except (ValueError, TypeError):
                return {
                    'is_valid': False,
                    'error': 'Calories must be a valid number'
                }
        
        return self.validate_numeric_range(calories, 0, 10000, 'Calories')
    
    def validate_nutritional_values(self, nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate nutritional values."""
        errors = []
        sanitized_data = {}
        
        # Define expected nutrition fields with their ranges
        nutrition_fields = {
            'calories': (0, 10000),
            'protein': (0, 200),
            'carbohydrates': (0, 500),
            'fat': (0, 200),
            'fiber': (0, 100),
            'sugar': (0, 200),
            'sodium': (0, 10000)  # mg
        }
        
        for field, (min_val, max_val) in nutrition_fields.items():
            if field in nutrition_data and nutrition_data[field] is not None:
                try:
                    value = float(nutrition_data[field])
                    validation_result = self.validate_numeric_range(
                        value, min_val, max_val, field.capitalize()
                    )
                    if not validation_result['is_valid']:
                        errors.append(validation_result['error'])
                    else:
                        sanitized_data[field] = value
                except (ValueError, TypeError):
                    errors.append(f'{field.capitalize()} must be a valid number')
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': sanitized_data
        }

# Global validator instances
auth_validator = AuthValidator()
profile_validator = UserProfileValidator()
product_validator = ProductValidator()
nutrition_validator = NutritionValidator()
