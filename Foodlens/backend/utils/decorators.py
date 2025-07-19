"""
Decorators for FoodLens Application
Authentication, authorization, and utility decorators.
"""

from functools import wraps
from flask import request, jsonify, current_app
from services.auth_service import auth_service

def require_auth(f):
    """
    Decorator to require authentication for API endpoints.
    Validates JWT token and adds user info to request.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'No authorization header provided'
            }), 401
        
        # Extract token from Bearer format
        try:
            token_type, token = auth_header.split(' ', 1)
            if token_type.lower() != 'bearer':
                return jsonify({
                    'success': False,
                    'error': 'Invalid authorization header format. Use Bearer <token>'
                }), 401
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid authorization header format'
            }), 401
        
        # Verify token
        verification_result = auth_service.verify_token(token)
        if not verification_result['success']:
            return jsonify({
                'success': False,
                'error': verification_result['error']
            }), 401
        
        # Add user info to request
        request.current_user = verification_result['user']
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """
    Decorator to require admin privileges.
    Must be used together with @require_auth.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Check if user has admin role (you can extend this logic)
        user = request.current_user
        if not user.get('is_admin', False):
            return jsonify({
                'success': False,
                'error': 'Admin privileges required'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_json(f):
    """
    Decorator to validate that request contains valid JSON.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must contain JSON data'
            }), 400
        
        try:
            request.get_json()
        except Exception:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit(max_requests: int = 100, window_minutes: int = 60):
    """
    Simple rate limiting decorator.
    This is a basic implementation - in production, use Redis or similar.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limiting - in production, implement with Redis
            # For now, just log the request
            current_app.logger.info(f"Rate limit check for {request.remote_addr}")
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
