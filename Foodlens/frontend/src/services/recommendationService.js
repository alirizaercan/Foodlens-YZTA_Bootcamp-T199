/**
 * Recommendation Service for FoodLens Application
 * Handles all recommendation and suggestion API calls
 */

import { apiRequest } from './api';
import { getAuthHeaders } from './authService';

/**
 * Get personalized food recommendations
 * @param {Object} options - Recommendation options
 * @param {string} options.mealType - Meal type (breakfast, lunch, dinner, snack)
 * @param {number} options.maxCalories - Maximum calories
 * @param {Array} options.excludeAllergens - Allergens to exclude
 * @param {string} options.preferredCuisine - Preferred cuisine type
 * @param {number} options.limit - Number of recommendations (default: 10)
 * @returns {Promise} - Personalized recommendations
 */
export const getPersonalizedRecommendations = async (options = {}) => {
  const params = new URLSearchParams();
  
  if (options.mealType) params.append('meal_type', options.mealType);
  if (options.maxCalories) params.append('max_calories', options.maxCalories);
  if (options.excludeAllergens && options.excludeAllergens.length > 0) {
    params.append('exclude_allergens', options.excludeAllergens.join(','));
  }
  if (options.preferredCuisine) params.append('preferred_cuisine', options.preferredCuisine);
  if (options.limit) params.append('limit', options.limit);

  return await apiRequest(`/api/recommendations/personalized?${params.toString()}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get recommendations based on analyzed product
 * @param {string} productId - Product ID or analysis ID
 * @param {Object} options - Recommendation options
 * @param {string} options.recommendationType - Type of recommendation (alternatives, complements, meals)
 * @param {number} options.limit - Number of recommendations
 * @returns {Promise} - Product-based recommendations
 */
export const getProductBasedRecommendations = async (productId, options = {}) => {
  const params = new URLSearchParams({
    type: options.recommendationType || 'alternatives',
    limit: options.limit || 5,
  });

  return await apiRequest(`/api/recommendations/product/${productId}?${params.toString()}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get meal planning recommendations
 * @param {Object} options - Meal planning options
 * @param {number} options.days - Number of days to plan (default: 7)
 * @param {number} options.targetCalories - Target daily calories
 * @param {Array} options.mealTypes - Meal types to include
 * @param {Object} options.macroTargets - Macro nutrient targets
 * @returns {Promise} - Meal plan recommendations
 */
export const getMealPlanRecommendations = async (options = {}) => {
  return await apiRequest('/api/recommendations/meal-plan', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      days: options.days || 7,
      target_calories: options.targetCalories,
      meal_types: options.mealTypes || ['breakfast', 'lunch', 'dinner'],
      macro_targets: options.macroTargets || {},
    }),
  });
};

/**
 * Get healthy alternatives for a product
 * @param {string} productId - Product ID
 * @param {Object} criteria - Criteria for alternatives
 * @param {boolean} criteria.lowerCalories - Find lower calorie options
 * @param {boolean} criteria.lowerSugar - Find lower sugar options
 * @param {boolean} criteria.lowerSodium - Find lower sodium options
 * @param {boolean} criteria.higherProtein - Find higher protein options
 * @param {number} criteria.limit - Number of alternatives
 * @returns {Promise} - Healthy alternatives
 */
export const getHealthyAlternatives = async (productId, criteria = {}) => {
  return await apiRequest(`/api/recommendations/alternatives/${productId}`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(criteria),
  });
};

/**
 * Get recipe recommendations based on ingredients
 * @param {Array} ingredients - List of ingredient names
 * @param {Object} options - Recipe options
 * @param {string} options.cuisine - Cuisine type
 * @param {number} options.maxPrepTime - Maximum preparation time (minutes)
 * @param {string} options.difficulty - Difficulty level (easy, medium, hard)
 * @param {number} options.servings - Number of servings
 * @returns {Promise} - Recipe recommendations
 */
export const getRecipeRecommendations = async (ingredients, options = {}) => {
  return await apiRequest('/api/recommendations/recipes', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      ingredients,
      cuisine: options.cuisine,
      max_prep_time: options.maxPrepTime,
      difficulty: options.difficulty,
      servings: options.servings,
    }),
  });
};

/**
 * Get shopping list recommendations
 * @param {Object} preferences - Shopping preferences
 * @param {Array} preferences.goals - Nutrition goals
 * @param {number} preferences.budget - Budget limit
 * @param {string} preferences.store - Preferred store
 * @param {Array} preferences.excludeCategories - Categories to exclude
 * @returns {Promise} - Shopping list recommendations
 */
export const getShoppingListRecommendations = async (preferences = {}) => {
  return await apiRequest('/api/recommendations/shopping-list', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(preferences),
  });
};

/**
 * Save user feedback on recommendations
 * @param {string} recommendationId - Recommendation ID
 * @param {Object} feedback - User feedback
 * @param {number} feedback.rating - Rating (1-5)
 * @param {boolean} feedback.helpful - Whether recommendation was helpful
 * @param {string} feedback.comment - Optional comment
 * @returns {Promise} - Feedback response
 */
export const saveRecommendationFeedback = async (recommendationId, feedback) => {
  return await apiRequest(`/api/recommendations/${recommendationId}/feedback`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(feedback),
  });
};

/**
 * Get recommendation history
 * @param {Object} options - Query options
 * @param {number} options.page - Page number
 * @param {number} options.limit - Items per page
 * @param {string} options.type - Recommendation type filter
 * @returns {Promise} - Recommendation history
 */
export const getRecommendationHistory = async (options = {}) => {
  const params = new URLSearchParams({
    page: options.page || 1,
    limit: options.limit || 20,
  });
  
  if (options.type) params.append('type', options.type);

  return await apiRequest(`/api/recommendations/history?${params.toString()}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

export default {
  getPersonalizedRecommendations,
  getProductBasedRecommendations,
  getMealPlanRecommendations,
  getHealthyAlternatives,
  getRecipeRecommendations,
  getShoppingListRecommendations,
  saveRecommendationFeedback,
  getRecommendationHistory,
};
