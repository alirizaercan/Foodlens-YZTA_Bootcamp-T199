"""
Authentication Controller for FoodLens Application
API endpoints for user authentication and authorization.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import auth_service
from utils.decorators import require_auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        result = auth_service.register_user(
            email=data.get('email'),
            password=data.get('password'),
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Registration failed: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        result = auth_service.login_user(
            email_or_username=data.get('email_or_username'),
            password=data.get('password')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """User logout endpoint."""
    # In a stateless JWT system, logout is handled client-side
    # by removing the token from storage
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT token endpoint."""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'No token provided'
            }), 401
        
        token = auth_header.split(' ')[1]
        result = auth_service.refresh_token(token)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Token refresh failed: {str(e)}'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        user_id = request.current_user['id']
        result = auth_service.change_password(
            user_id=user_id,
            old_password=data.get('old_password'),
            new_password=data.get('new_password')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Password change failed: {str(e)}'
        }), 500

@auth_bp.route('/verify', methods=['GET'])
@require_auth
def verify_token():
    """Verify current token endpoint."""
    return jsonify({
        'success': True,
        'user': request.current_user,
        'message': 'Token is valid'
    })

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    """Google OAuth authentication endpoint."""
    try:
        data = request.get_json()
        if not data or not data.get('token'):
            return jsonify({
                'success': False,
                'error': 'Google token is required'
            }), 400
        
        result = auth_service.google_login(data['token'])
        
        if result['success']:
            status_code = 200 if not result.get('is_new_user') else 201
            return jsonify(result), status_code
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Google authentication failed: {str(e)}'
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email."""
    try:
        data = request.get_json()
        if not data or not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        result = auth_service.request_password_reset(data['email'])
        
        # Always return success to prevent email enumeration
        return jsonify({
            'success': True,
            'message': 'If an account with this email exists, a password reset link has been sent.'
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Password reset request failed: {str(e)}'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token."""
    try:
        data = request.get_json()
        if not data or not data.get('token') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'error': 'Reset token and new password are required'
            }), 400
        
        result = auth_service.reset_password(data['token'], data['new_password'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Password reset failed: {str(e)}'
        }), 500
