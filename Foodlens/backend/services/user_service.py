"""
User Service for FoodLens Application
Business logic for user profile and preference management.
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
import uuid
from sqlalchemy.exc import IntegrityError
from utils.database import Database
from models.user import User
from models.user_profile import UserProfile
from models.allergen import Allergen, UserAllergen
from models.nutrition_goal import NutritionGoal
from utils.validators import profile_validator

class UserService:
    def __init__(self):
        self.db = Database()
        self.validator = profile_validator
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information."""
        session = self.db.connect()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            return {
                'success': True,
                'user': user.to_dict(),
                'profile': profile.to_dict() if profile else None
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve profile: {str(e)}'}
        finally:
            self.db.close(session)
    
    def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile information."""
        session = self.db.connect()
        try:
            # Validate input data
            validation_result = self.validator.validate_profile_setup(data)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }
            
            sanitized_data = validation_result['sanitized_data']
            
            # Get or create profile
            profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if not profile:
                profile = UserProfile(user_id=user_id)
                session.add(profile)
            
            # Update profile fields
            profile.update_profile(**sanitized_data)
            session.commit()
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'profile': profile.to_dict()
            }
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f'Failed to update profile: {str(e)}'}
        finally:
            self.db.close(session)
    
    def setup_user_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup user profile during onboarding."""
        session = self.db.connect()
        try:
            # Check if profile already exists
            existing_profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if existing_profile:
                return {'success': False, 'error': 'Profile already exists'}
            
            # Validate input data
            validation_result = self.validator.validate_profile_setup(data)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }
            
            sanitized_data = validation_result['sanitized_data']
            
            # Create new profile
            profile = UserProfile(user_id=user_id, **sanitized_data)
            session.add(profile)
            session.commit()
            
            return {
                'success': True,
                'message': 'Profile setup completed successfully',
                'profile': profile.to_dict()
            }
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f'Failed to setup profile: {str(e)}'}
        finally:
            self.db.close(session)
    
    def get_user_allergens(self, user_id: str) -> Dict[str, Any]:
        """Get user's allergen list."""
        session = self.db.connect()
        try:
            user_allergens = session.query(UserAllergen)\
                .filter(UserAllergen.user_id == user_id)\
                .all()
            
            allergens_data = [ua.to_dict() for ua in user_allergens]
            
            return {
                'success': True,
                'allergens': allergens_data
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve allergens: {str(e)}'}
        finally:
            self.db.close(session)
    
    def add_user_allergen(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add allergen to user's profile."""
        session = self.db.connect()
        try:
            allergen_id = data.get('allergen_id')
            severity = data.get('severity', 'moderate')
            notes = data.get('notes', '')
            diagnosed_date = data.get('diagnosed_date')
            
            # Check if allergen exists
            allergen = session.query(Allergen).filter(Allergen.id == allergen_id).first()
            if not allergen:
                return {'success': False, 'error': 'Allergen not found'}
            
            # Check if user already has this allergen
            existing = session.query(UserAllergen)\
                .filter(UserAllergen.user_id == user_id, UserAllergen.allergen_id == allergen_id)\
                .first()
            
            if existing:
                return {'success': False, 'error': 'Allergen already added to profile'}
            
            # Parse diagnosed_date if provided
            parsed_date = None
            if diagnosed_date:
                try:
                    parsed_date = datetime.strptime(diagnosed_date, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}
            
            # Create new user allergen
            user_allergen = UserAllergen(
                user_id=user_id,
                allergen_id=allergen_id,
                severity=severity,
                notes=notes,
                diagnosed_date=parsed_date
            )
            
            session.add(user_allergen)
            session.commit()
            
            return {
                'success': True,
                'message': 'Allergen added successfully',
                'allergen': user_allergen.to_dict()
            }
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f'Failed to add allergen: {str(e)}'}
        finally:
            self.db.close(session)
    
    def remove_user_allergen(self, user_id: str, allergen_id: str) -> Dict[str, Any]:
        """Remove allergen from user's profile."""
        session = self.db.connect()
        try:
            user_allergen = session.query(UserAllergen)\
                .filter(UserAllergen.id == allergen_id, UserAllergen.user_id == user_id)\
                .first()
            
            if not user_allergen:
                return {'success': False, 'error': 'Allergen not found in user profile'}
            
            session.delete(user_allergen)
            session.commit()
            
            return {
                'success': True,
                'message': 'Allergen removed successfully'
            }
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f'Failed to remove allergen: {str(e)}'}
        finally:
            self.db.close(session)
    
    def get_available_allergens(self) -> Dict[str, Any]:
        """Get list of all available allergens."""
        session = self.db.connect()
        try:
            allergens = session.query(Allergen).order_by(Allergen.name).all()
            allergens_data = [allergen.to_dict() for allergen in allergens]
            
            return {
                'success': True,
                'allergens': allergens_data
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve allergens: {str(e)}'}
        finally:
            self.db.close(session)
    
    def get_nutrition_goals(self, user_id: str) -> Dict[str, Any]:
        """Get user's nutrition goals."""
        session = self.db.connect()
        try:
            goals = session.query(NutritionGoal)\
                .filter(NutritionGoal.user_id == user_id)\
                .order_by(NutritionGoal.created_at.desc())\
                .all()
            
            goals_data = [goal.to_dict() for goal in goals]
            
            return {
                'success': True,
                'goals': goals_data
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve nutrition goals: {str(e)}'}
        finally:
            self.db.close(session)
    
    def create_nutrition_goal(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new nutrition goal."""
        session = self.db.connect()
        try:
            # Extract and validate data
            goal_type = data.get('goal_type')
            target_value = data.get('target_value')
            unit = data.get('unit')
            period = data.get('period', 'daily')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            notes = data.get('notes', '')
            
            # Basic validation
            if not all([goal_type, target_value, unit]):
                return {'success': False, 'error': 'goal_type, target_value, and unit are required'}
            
            # Parse dates
            parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else date.today()
            parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            # Create nutrition goal
            goal = NutritionGoal(
                user_id=user_id,
                goal_type=goal_type,
                target_value=float(target_value),
                unit=unit,
                period=period,
                start_date=parsed_start_date,
                end_date=parsed_end_date,
                notes=notes
            )
            
            session.add(goal)
            session.commit()
            
            return {
                'success': True,
                'message': 'Nutrition goal created successfully',
                'goal': goal.to_dict()
            }
            
        except ValueError as e:
            return {'success': False, 'error': f'Invalid data format: {str(e)}'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f'Failed to create nutrition goal: {str(e)}'}
        finally:
            self.db.close(session)
    
    def update_nutrition_goal(self, user_id: str, goal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing nutrition goal."""
        session = self.db.connect()
        try:
            goal = session.query(NutritionGoal)\
                .filter(NutritionGoal.id == goal_id, NutritionGoal.user_id == user_id)\
                .first()
            
            if not goal:
                return {'success': False, 'error': 'Nutrition goal not found'}
            
            # Update fields
            for field in ['target_value', 'current_value', 'unit', 'period', 'notes', 'is_active']:
                if field in data:
                    setattr(goal, field, data[field])
            
            # Handle date fields
            if 'end_date' in data and data['end_date']:
                goal.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            
            goal.updated_at = datetime.utcnow()
            session.commit()
            
            return {
                'success': True,
                'message': 'Nutrition goal updated successfully',
                'goal': goal.to_dict()
            }
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f'Failed to update nutrition goal: {str(e)}'}
        finally:
            self.db.close(session)
    
    def delete_nutrition_goal(self, user_id: str, goal_id: str) -> Dict[str, Any]:
        """Delete a nutrition goal."""
        session = self.db.connect()
        try:
            goal = session.query(NutritionGoal)\
                .filter(NutritionGoal.id == goal_id, NutritionGoal.user_id == user_id)\
                .first()
            
            if not goal:
                return {'success': False, 'error': 'Nutrition goal not found'}
            
            session.delete(goal)
            session.commit()
            
            return {
                'success': True,
                'message': 'Nutrition goal deleted successfully'
            }
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f'Failed to delete nutrition goal: {str(e)}'}
        finally:
            self.db.close(session)
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get user dashboard data."""
        session = self.db.connect()
        try:
            from models.analysis import Analysis
            from models.recommendation import Recommendation
            
            # Get recent analyses
            recent_analyses = session.query(Analysis)\
                .filter(Analysis.user_id == user_id)\
                .order_by(Analysis.created_at.desc())\
                .limit(5)\
                .all()
            
            # Get unread recommendations
            unread_recommendations = session.query(Recommendation)\
                .filter(Recommendation.user_id == user_id, Recommendation.is_read == False)\
                .order_by(Recommendation.created_at.desc())\
                .limit(10)\
                .all()
            
            # Get active nutrition goals
            active_goals = session.query(NutritionGoal)\
                .filter(NutritionGoal.user_id == user_id, NutritionGoal.is_active == True)\
                .all()
            
            return {
                'success': True,
                'dashboard': {
                    'recent_analyses': [analysis.to_dict() for analysis in recent_analyses],
                    'unread_recommendations': [rec.to_dict() for rec in unread_recommendations],
                    'active_goals': [goal.to_dict() for goal in active_goals],
                    'stats': {
                        'total_analyses': len(recent_analyses),
                        'unread_recommendations_count': len(unread_recommendations),
                        'active_goals_count': len(active_goals)
                    }
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve dashboard: {str(e)}'}
        finally:
            self.db.close(session)

# Global user service instance
user_service = UserService()
