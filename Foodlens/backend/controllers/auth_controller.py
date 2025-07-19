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
