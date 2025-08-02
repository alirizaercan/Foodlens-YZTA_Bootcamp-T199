/**
 * Authentication Service for FoodLens Application
 * Handles all authentication-related API calls
 */

import { apiRequest } from './api';

/**
 * User registration
 * @param {Object} userData - User registration data
 * @param {string} userData.email - User email
 * @param {string} userData.password - User password
 * @param {string} userData.full_name - User full name
 * @returns {Promise} - Registration response
 */
export const register = async (userData) => {
  const response = await apiRequest('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
  
  // Store token if registration successful
  if (response.token) {
    localStorage.setItem('auth_token', response.token);
    localStorage.setItem('user_data', JSON.stringify(response.user));
  }
  
  return response;
};

/**
 * User login
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise} - Login response
 */
export const login = async (email, password) => {
  const response = await apiRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  
  // Store token if login successful
  if (response.token) {
    localStorage.setItem('auth_token', response.token);
    localStorage.setItem('user_data', JSON.stringify(response.user));
  }
  
  return response;
};

/**
 * User logout
 * @returns {Promise} - Logout response
 */
export const logout = async () => {
  const token = getAuthToken();
  
  try {
    await apiRequest('/api/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Clear local storage regardless of API response
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  }
};

/**
 * Refresh authentication token
 * @returns {Promise} - Refresh response
 */
export const refreshToken = async () => {
  const token = getAuthToken();
  
  const response = await apiRequest('/api/auth/refresh', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  // Update stored token
  if (response.token) {
    localStorage.setItem('auth_token', response.token);
  }
  
  return response;
};

/**
 * Change user password
 * @param {string} currentPassword - Current password
 * @param {string} newPassword - New password
 * @returns {Promise} - Change password response
 */
export const changePassword = async (currentPassword, newPassword) => {
  const token = getAuthToken();
  
  return await apiRequest('/api/auth/change-password', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
};

/**
 * Verify authentication token
 * @returns {Promise} - Verification response
 */
export const verifyToken = async () => {
  const token = getAuthToken();
  
  if (!token) {
    throw new Error('No authentication token found');
  }
  
  return await apiRequest('/api/auth/verify', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
};

/**
 * Get stored authentication token
 * @returns {string|null} - Auth token or null
 */
export const getAuthToken = () => {
  return localStorage.getItem('auth_token');
};

/**
 * Get stored user data
 * @returns {Object|null} - User data or null
 */
export const getUserData = () => {
  const userData = localStorage.getItem('user_data');
  return userData ? JSON.parse(userData) : null;
};

/**
 * Check if user is authenticated
 * @returns {boolean} - Authentication status
 */
export const isAuthenticated = () => {
  return !!getAuthToken();
};

/**
 * Get authorization headers for API requests
 * @returns {Object} - Authorization headers
 */
export const getAuthHeaders = () => {
  const token = getAuthToken();
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

/**
 * Google OAuth authentication
 * @param {string} googleToken - Google OAuth token
 * @returns {Promise} - Authentication response
 */
export const googleAuth = async (googleToken) => {
  return await apiRequest('/api/auth/google', {
    method: 'POST',
    body: JSON.stringify({ token: googleToken }),
  });
};

export default {
  register,
  login,
  logout,
  refreshToken,
  changePassword,
  verifyToken,
  getAuthToken,
  getUserData,
  isAuthenticated,
  getAuthHeaders,
  googleAuth,
};
