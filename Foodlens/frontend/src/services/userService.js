/**
 * User Service for FoodLens Application
 * Handles all user profile and preferences API calls
 */

import { apiRequest } from './api';
import { getAuthHeaders } from './authService';

/**
 * Get user profile
 * @returns {Promise} - User profile data
 */
export const getUserProfile = async () => {
  return await apiRequest('/api/users/profile', {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Update user profile
 * @param {Object} profileData - Profile data to update
 * @returns {Promise} - Updated profile response
 */
export const updateUserProfile = async (profileData) => {
  return await apiRequest('/api/users/profile', {
    method: 'PUT',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(profileData),
  });
};

/**
 * Setup user profile (initial setup)
 * @param {Object} profileData - Initial profile data
 * @param {number} profileData.height - User height in cm
 * @param {number} profileData.weight - User weight in kg
 * @param {number} profileData.age - User age
 * @param {string} profileData.gender - User gender (male/female/other)
 * @param {string} profileData.activity_level - Activity level
 * @param {Array} profileData.allergen_ids - Array of allergen IDs
 * @param {boolean} profileData.kvkk_approval - KVKK approval status
 * @returns {Promise} - Profile setup response
 */
export const setupUserProfile = async (profileData) => {
  return await apiRequest('/api/users/profile/setup', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(profileData),
  });
};

/**
 * Get user allergens
 * @returns {Promise} - User allergens list
 */
export const getUserAllergens = async () => {
  return await apiRequest('/api/users/allergens', {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Add user allergen
 * @param {string} allergenId - Allergen ID to add
 * @returns {Promise} - Add allergen response
 */
export const addUserAllergen = async (allergenId) => {
  return await apiRequest('/api/users/allergens', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ allergen_id: allergenId }),
  });
};

/**
 * Remove user allergen
 * @param {string} allergenId - Allergen ID to remove
 * @returns {Promise} - Remove allergen response
 */
export const removeUserAllergen = async (allergenId) => {
  return await apiRequest(`/api/users/allergens/${allergenId}`, {
    method: 'DELETE',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get available allergens list
 * @returns {Promise} - Available allergens
 */
export const getAvailableAllergens = async () => {
  return await apiRequest('/api/users/allergens/available', {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get user nutrition goals
 * @returns {Promise} - User nutrition goals
 */
export const getNutritionGoals = async () => {
  return await apiRequest('/api/users/nutrition-goals', {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Create nutrition goal
 * @param {Object} goalData - Nutrition goal data
 * @param {string} goalData.goal_type - Goal type (weight_loss, weight_gain, maintenance)
 * @param {number} goalData.target_calories - Target daily calories
 * @param {number} goalData.target_protein - Target protein (g)
 * @param {number} goalData.target_carbs - Target carbohydrates (g)
 * @param {number} goalData.target_fat - Target fat (g)
 * @param {number} goalData.target_weight - Target weight (kg)
 * @param {Date} goalData.target_date - Target date
 * @returns {Promise} - Create goal response
 */
export const createNutritionGoal = async (goalData) => {
  return await apiRequest('/api/users/nutrition-goals', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(goalData),
  });
};

/**
 * Update nutrition goal
 * @param {string} goalId - Goal ID to update
 * @param {Object} goalData - Updated goal data
 * @returns {Promise} - Update goal response
 */
export const updateNutritionGoal = async (goalId, goalData) => {
  return await apiRequest(`/api/users/nutrition-goals/${goalId}`, {
    method: 'PUT',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(goalData),
  });
};

/**
 * Delete nutrition goal
 * @param {string} goalId - Goal ID to delete
 * @returns {Promise} - Delete goal response
 */
export const deleteNutritionGoal = async (goalId) => {
  return await apiRequest(`/api/users/nutrition-goals/${goalId}`, {
    method: 'DELETE',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get user dashboard data
 * @returns {Promise} - Dashboard data with stats and progress
 */
export const getUserDashboard = async () => {
  return await apiRequest('/api/users/dashboard', {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Update user basic information (name, username, etc.)
 * @param {Object} basicData - Basic user information to update
 * @returns {Promise} - Update response
 */
export const updateUserBasicInfo = async (basicData) => {
  return await apiRequest('/api/users/settings/basic', {
    method: 'PUT',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(basicData),
  });
};

export default {
  getUserProfile,
  updateUserProfile,
  setupUserProfile,
  getUserAllergens,
  addUserAllergen,
  removeUserAllergen,
  getAvailableAllergens,
  getNutritionGoals,
  createNutritionGoal,
  updateNutritionGoal,
  deleteNutritionGoal,
  getUserDashboard,
  updateUserBasicInfo,
};
