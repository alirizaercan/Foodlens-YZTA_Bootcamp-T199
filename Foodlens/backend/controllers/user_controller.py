"""
User Controller for FoodLens Application
User profile management and preferences endpoints.
"""

from flask import Blueprint, request, jsonify
from services.user_service import user_service
from utils.decorators import require_auth, validate_json

user_bp = Blueprint('users', __name__)

@user_bp.route('/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """Get current user's profile."""
    try:
        user_id = request.current_user['id']
        result = user_service.get_user_profile(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve profile: {str(e)}'
        }), 500

@user_bp.route('/profile', methods=['PUT'])
@require_auth
@validate_json
def update_user_profile():
    """Update current user's profile."""
    try:
        user_id = request.current_user['id']
        data = request.get_json()
        
        result = user_service.update_user_profile(user_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update profile: {str(e)}'
        }), 500

@user_bp.route('/profile/setup', methods=['POST'])
@require_auth
@validate_json
def setup_user_profile():
    """Setup user profile during onboarding."""
    try:
        user_id = request.current_user['id']
        data = request.get_json()
        
        result = user_service.setup_user_profile(user_id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to setup profile: {str(e)}'
        }), 500

@user_bp.route('/allergens', methods=['GET'])
@require_auth
def get_user_allergens():
    """Get user's allergen list."""
    try:
        user_id = request.current_user['id']
        result = user_service.get_user_allergens(user_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve allergens: {str(e)}'
        }), 500

@user_bp.route('/allergens', methods=['POST'])
@require_auth
@validate_json
def add_user_allergen():
    """Add allergen to user's profile."""
    try:
        user_id = request.current_user['id']
        data = request.get_json()
        
        result = user_service.add_user_allergen(user_id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to add allergen: {str(e)}'
        }), 500

@user_bp.route('/allergens/<allergen_id>', methods=['DELETE'])
@require_auth
def remove_user_allergen(allergen_id):
    """Remove allergen from user's profile."""
    try:
        user_id = request.current_user['id']
        result = user_service.remove_user_allergen(user_id, allergen_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to remove allergen: {str(e)}'
        }), 500

@user_bp.route('/nutrition-goals', methods=['GET'])
@require_auth
def get_nutrition_goals():
    """Get user's nutrition goals."""
    try:
        user_id = request.current_user['id']
        result = user_service.get_nutrition_goals(user_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve nutrition goals: {str(e)}'
        }), 500

@user_bp.route('/nutrition-goals', methods=['POST'])
@require_auth
@validate_json
def create_nutrition_goal():
    """Create a new nutrition goal."""
    try:
        user_id = request.current_user['id']
        data = request.get_json()
        
        result = user_service.create_nutrition_goal(user_id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create nutrition goal: {str(e)}'
        }), 500

@user_bp.route('/nutrition-goals/<goal_id>', methods=['PUT'])
@require_auth
@validate_json
def update_nutrition_goal(goal_id):
    """Update an existing nutrition goal."""
    try:
        user_id = request.current_user['id']
        data = request.get_json()
        
        result = user_service.update_nutrition_goal(user_id, goal_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update nutrition goal: {str(e)}'
        }), 500

@user_bp.route('/nutrition-goals/<goal_id>', methods=['DELETE'])
@require_auth
def delete_nutrition_goal(goal_id):
    """Delete a nutrition goal."""
    try:
        user_id = request.current_user['id']
        result = user_service.delete_nutrition_goal(user_id, goal_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete nutrition goal: {str(e)}'
        }), 500

@user_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_user_dashboard():
    """Get user dashboard data."""
    try:
        user_id = request.current_user['id']
        result = user_service.get_user_dashboard(user_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve dashboard: {str(e)}'
        }), 500

@user_bp.route('/allergens/available', methods=['GET'])
def get_available_allergens():
    """Get list of all available allergens."""
    try:
        result = user_service.get_available_allergens()
        return jsonify(result), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve available allergens: {str(e)}'
        }), 500

@user_bp.route('/settings/basic', methods=['PUT'])
@require_auth
@validate_json
def update_user_basic_info():
    """Update user's basic information (name, username, etc.)."""
    try:
        user_id = request.current_user['id']
        data = request.get_json()
        
        result = user_service.update_user_basic_info(user_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update basic information: {str(e)}'
        }), 500
