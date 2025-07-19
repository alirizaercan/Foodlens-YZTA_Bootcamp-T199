/**
 * Analytics Service for FoodLens Application
 * Handles user analytics and tracking
 */

import { apiRequest } from './api';
import { getAuthHeaders } from './authService';

/**
 * Track user activity
 * @param {Object} eventData - Event tracking data
 * @param {string} eventData.event_type - Type of event (page_view, product_scan, analysis_complete, etc.)
 * @param {string} eventData.page - Page or screen name
 * @param {Object} eventData.properties - Additional event properties
 * @returns {Promise} - Tracking response
 */
export const trackUserActivity = async (eventData) => {
  return await apiRequest('/api/analytics/track', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      event_type: eventData.event_type,
      page: eventData.page,
      properties: eventData.properties || {},
      timestamp: new Date().toISOString(),
    }),
  });
};

/**
 * Get user analytics dashboard
 * @param {Object} options - Analytics options
 * @param {string} options.period - Time period (day, week, month, year)
 * @param {Date} options.startDate - Start date
 * @param {Date} options.endDate - End date
 * @returns {Promise} - Analytics data
 */
export const getUserAnalytics = async (options = {}) => {
  const params = new URLSearchParams({
    period: options.period || 'month',
  });
  
  if (options.startDate) {
    params.append('start_date', options.startDate.toISOString().split('T')[0]);
  }
  
  if (options.endDate) {
    params.append('end_date', options.endDate.toISOString().split('T')[0]);
  }

  return await apiRequest(`/api/analytics/user?${params.toString()}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get nutrition progress analytics
 * @param {Object} options - Progress options
 * @param {number} options.days - Number of days to analyze
 * @returns {Promise} - Nutrition progress data
 */
export const getNutritionProgress = async (options = {}) => {
  const params = new URLSearchParams({
    days: options.days || 30,
  });

  return await apiRequest(`/api/analytics/nutrition-progress?${params.toString()}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get scanning statistics
 * @returns {Promise} - Scanning stats
 */
export const getScanningStats = async () => {
  return await apiRequest('/api/analytics/scanning-stats', {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Track product scan
 * @param {Object} scanData - Scan tracking data
 * @param {string} scanData.product_id - Product ID (if found)
 * @param {string} scanData.scan_type - Type of scan (barcode, image, manual)
 * @param {boolean} scanData.successful - Whether scan was successful
 * @param {number} scanData.processing_time - Time taken to process
 * @returns {Promise} - Scan tracking response
 */
export const trackProductScan = async (scanData) => {
  return await apiRequest('/api/analytics/track-scan', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(scanData),
  });
};

/**
 * Get goal progress
 * @param {string} goalId - Goal ID
 * @returns {Promise} - Goal progress data
 */
export const getGoalProgress = async (goalId) => {
  return await apiRequest(`/api/analytics/goal-progress/${goalId}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

export default {
  trackUserActivity,
  getUserAnalytics,
  getNutritionProgress,
  getScanningStats,
  trackProductScan,
  getGoalProgress,
};
