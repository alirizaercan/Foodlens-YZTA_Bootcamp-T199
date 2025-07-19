"""
Authentication Service for FoodLens Application
Business logic for user authentication and authorization.
"""

from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import current_app
from sqlalchemy.exc import IntegrityError
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from utils.database import Database
from models.user import User
from models.user_profile import UserProfile
from utils.validators import AuthValidator

class AuthService:
    def __init__(self):
        self.db = Database()
        self.validator = AuthValidator()
        
    def _get_serializer(self):
        """Get URLSafeTimedSerializer instance."""
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        return URLSafeTimedSerializer(secret_key)
    
    def register_user(self, email: str, password: str, username: str, 
                     first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new user with validation.
        """
        session = self.db.connect()
        try:
            # Validate input data
            validation_result = self.validator.validate_registration({
                'email': email,
                'password': password,
                'username': username,
                'first_name': first_name,
                'last_name': last_name
            })
            
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }
            
            # Check if user already exists
            existing_user = session.query(User).filter(
                (User.email == email.lower()) | (User.username == username)
            ).first()
            
            if existing_user:
                return {
                    'success': False,
                    'error': 'User already exists with this email or username'
                }
            
            # Create new user
            new_user = User(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            
            session.add(new_user)
            session.commit()
            
            # Generate access token
            access_token = self._generate_token(new_user.id)
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': new_user.to_dict(),
                'access_token': access_token
            }
            
        except IntegrityError:
            session.rollback()
            return {
                'success': False,
                'error': 'User with this email or username already exists'
            }
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': f'Registration failed: {str(e)}'
            }
        finally:
            self.db.close(session)
    
    def login_user(self, email_or_username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user login.
        """
        session = self.db.connect()
        try:
            # Find user by email or username
            user = session.query(User).filter(
                (User.email == email_or_username.lower()) | 
                (User.username == email_or_username)
            ).first()
            
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            if not user.check_password(password):
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            if not user.is_active:
                return {
                    'success': False,
                    'error': 'Account is deactivated'
                }
            
            # Update last login
            user.update_last_login()
            session.commit()
            
            # Generate access token
            access_token = self._generate_token(user.id)
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'access_token': access_token
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Login failed: {str(e)}'
            }
        finally:
            self.db.close(session)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify token using itsdangerous and return user information.
        """
        try:
            serializer = self._get_serializer()
            # Token expires after 24 hours (86400 seconds)
            max_age = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)
            
            # Deserialize token data
            user_id = serializer.loads(token, max_age=max_age)
            
            if not user_id:
                return {'success': False, 'error': 'Invalid token'}
            
            session = self.db.connect()
            try:
                user = session.query(User).filter(User.id == user_id).first()
                if not user or not user.is_active:
                    return {'success': False, 'error': 'User not found or inactive'}
                
                return {
                    'success': True,
                    'user': user.to_dict()
                }
            finally:
                self.db.close(session)
                
        except SignatureExpired:
            return {'success': False, 'error': 'Token has expired'}
        except BadSignature:
            return {'success': False, 'error': 'Invalid token signature'}
        except Exception as e:
            return {'success': False, 'error': f'Token verification failed: {str(e)}'}
    
    def refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Refresh an existing JWT token.
        """
        verification_result = self.verify_token(token)
        if not verification_result['success']:
            return verification_result
        
        user_id = verification_result['user']['id']
        new_token = self._generate_token(user_id)
        
        return {
            'success': True,
            'access_token': new_token
        }
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user password.
        """
        session = self.db.connect()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            if not user.check_password(old_password):
                return {'success': False, 'error': 'Current password is incorrect'}
            
            # Validate new password
            validation_result = self.validator.validate_password(new_password)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': 'New password validation failed',
                    'details': validation_result['errors']
                }
            
            user.set_password(new_password)
            session.commit()
            
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f'Password change failed: {str(e)}'}
        finally:
            self.db.close(session)
    
    def _generate_token(self, user_id: uuid.UUID) -> str:
        """
        Generate secure token using itsdangerous.
        """
        serializer = self._get_serializer()
        return serializer.dumps(str(user_id))

# Global auth service instance
auth_service = AuthService()
