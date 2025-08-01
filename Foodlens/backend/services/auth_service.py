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
from google.auth.transport import requests
from google.oauth2 import id_token
import secrets
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
            print(f"Registration attempt - Email: {email}, Username: {username}, Password length: {len(password) if password else 0}")
            
            # Validate input data
            validation_result = self.validator.validate_registration({
                'email': email,
                'password': password,
                'username': username,
                'first_name': first_name,
                'last_name': last_name
            })
            
            print(f"Validation result: {validation_result}")
            
            if not validation_result['is_valid']:
                print(f"Validation failed: {validation_result['errors']}")
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

    def verify_google_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Google OAuth token and return user information.
        """
        try:
            # For development/demo purposes - check for demo tokens
            if token.startswith('demo-google-token'):
                return {
                    'success': True,
                    'user_info': {
                        'email': f'demo_{token.split("-")[-1]}@gmail.com',
                        'name': 'Demo User',
                        'first_name': 'Demo',
                        'last_name': 'User',
                        'picture': '',
                        'google_id': f'demo_{token.split("-")[-1]}'
                    }
                }
            
            # Verify the token with Google
            google_client_id = current_app.config.get('GOOGLE_CLIENT_ID')
            if not google_client_id:
                return {'success': False, 'error': 'Google OAuth not configured'}
            
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), google_client_id
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return {'success': False, 'error': 'Invalid token issuer'}
            
            return {
                'success': True,
                'user_info': {
                    'email': idinfo['email'],
                    'name': idinfo.get('name', ''),
                    'first_name': idinfo.get('given_name', ''),
                    'last_name': idinfo.get('family_name', ''),
                    'picture': idinfo.get('picture', ''),
                    'google_id': idinfo['sub']
                }
            }
            
        except ValueError as e:
            return {'success': False, 'error': f'Invalid token: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Token verification failed: {str(e)}'}
    
    def google_login(self, token: str) -> Dict[str, Any]:
        """
        Login or register user via Google OAuth.
        """
        session = self.db.connect()
        try:
            # Verify Google token
            verification_result = self.verify_google_token(token)
            if not verification_result['success']:
                return verification_result
            
            user_info = verification_result['user_info']
            email = user_info['email']
            
            # Check if user exists
            user = session.query(User).filter(User.email == email.lower()).first()
            
            if user:
                # Update last login
                user.update_last_login()
                session.commit()
                
                # Generate access token
                access_token = self._generate_token(user.id)
                
                return {
                    'success': True,
                    'message': 'Login successful',
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'is_new_user': False
                }
            else:
                # Create new user
                username = self._generate_unique_username(user_info['name'], email, session)
                
                # Generate a random password for Google users (they won't use it)
                random_password = secrets.token_urlsafe(32)
                
                new_user = User(
                    email=email,
                    password=random_password,
                    username=username,
                    first_name=user_info.get('first_name', ''),
                    last_name=user_info.get('last_name', '')
                )
                
                session.add(new_user)
                session.commit()
                
                # Generate access token
                access_token = self._generate_token(new_user.id)
                
                return {
                    'success': True,
                    'message': 'User registered and logged in successfully',
                    'user': new_user.to_dict(),
                    'access_token': access_token,
                    'is_new_user': True
                }
                
        except IntegrityError:
            session.rollback()
            return {
                'success': False,
                'error': 'User registration failed due to data conflict'
            }
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': f'Google login failed: {str(e)}'
            }
        finally:
            self.db.close(session)

    def _generate_unique_username(self, name: str, email: str, session) -> str:
        """
        Generate a unique username from name or email.
        """
        # Try to use name first, then email prefix
        base_username = name.lower().replace(' ', '') if name else email.split('@')[0]
        base_username = ''.join(c for c in base_username if c.isalnum())
        
        if not base_username:
            base_username = 'user'
        
        username = base_username
        counter = 1
        
        while session.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username

    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Request password reset for user.
        """
        session = self.db.connect()
        try:
            user = session.query(User).filter(User.email == email.lower()).first()
            
            # Always return success to prevent email enumeration
            # But only send email if user exists
            if user and user.is_active:
                # Generate reset token (expires in 1 hour)
                serializer = self._get_serializer()
                reset_token = serializer.dumps({
                    'user_id': str(user.id),
                    'purpose': 'password_reset'
                })
                
                # In a real app, you would send an email here
                # For now, we'll just log the token
                print(f"Password reset token for {email}: {reset_token}")
                
                # Store the token with user (in real app, you might store in Redis/cache)
                # For now, we'll just return success
                
            return {
                'success': True,
                'message': 'If an account with this email exists, a password reset link has been sent.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Password reset request failed: {str(e)}'
            }
        finally:
            self.db.close(session)

    def reset_password(self, reset_token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user password using reset token.
        """
        session = self.db.connect()
        try:
            # Verify reset token (expires in 1 hour)
            serializer = self._get_serializer()
            token_data = serializer.loads(reset_token, max_age=3600)  # 1 hour
            
            if not token_data or token_data.get('purpose') != 'password_reset':
                return {
                    'success': False,
                    'error': 'Invalid reset token'
                }
            
            user_id = token_data.get('user_id')
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            if not user.is_active:
                return {
                    'success': False,
                    'error': 'Account is deactivated'
                }
            
            # Validate new password
            if len(new_password) < 8:
                return {
                    'success': False,
                    'error': 'Password must be at least 8 characters long'
                }
            
            # Update password
            user.set_password(new_password)
            session.commit()
            
            return {
                'success': True,
                'message': 'Password has been reset successfully'
            }
            
        except SignatureExpired:
            return {
                'success': False,
                'error': 'Reset token has expired. Please request a new one.'
            }
        except BadSignature:
            return {
                'success': False,
                'error': 'Invalid reset token'
            }
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': f'Password reset failed: {str(e)}'
            }
        finally:
            self.db.close(session)

# Global auth service instance
auth_service = AuthService()
