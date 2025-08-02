/**
 * API Service for FoodLens Application
 * Handles all API requests to the backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

/**
 * Get auth token from localStorage
 * @returns {string|null} - Auth token
 */
const getAuthToken = () => {
  return localStorage.getItem('auth_token'); // Changed from 'authToken' to 'auth_token'
};

/**
 * Generic API request function
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Request options
 * @returns {Promise} - Response data
 */
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log('API Request to:', url);
  console.log('API Request options:', options);
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  // Add auth token if available
  const token = getAuthToken();
  if (token) {
    defaultOptions.headers['Authorization'] = `Bearer ${token}`;
  }

  // Remove Content-Type header for FormData
  if (options.body instanceof FormData) {
    delete defaultOptions.headers['Content-Type'];
  }

  const config = { ...defaultOptions, ...options };
  console.log('Final request config:', config);

  try {
    const response = await fetch(url, config);
    console.log('Response status:', response.status);
    console.log('Response ok:', response.ok);
    
    const responseData = await response.json();
    console.log('Response data:', responseData);
    
    if (!response.ok) {
      console.log('Error response data:', responseData);
      // Return the error response instead of throwing, so we can handle validation errors
      return responseData;
    }

    return responseData;
  } catch (error) {
    console.error('API Request Error:', error);
    // Return a structured error response
    return {
      success: false,
      error: 'Network error occurred',
      details: [error.message]
    };
  }
};

/**
 * Upload image for OCR and Nutri-Score analysis
 * @param {File} imageFile - Image file to analyze
 * @param {string} language - Language code (tr/en)
 * @param {string} productName - Optional product name
 * @param {string} brand - Optional brand name
 * @returns {Promise} - Analysis results
 */
export const analyzeImage = async (imageFile, language = 'tr', productName = '', brand = '') => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('language', language);
  
  if (productName) {
    formData.append('product_name', productName);
  }
  
  if (brand) {
    formData.append('brand', brand);
  }

  return await apiRequest('/api/analysis/analyze', {
    method: 'POST',
    body: formData,
  });
};

/**
 * Get health check
 * @returns {Promise} - Health status
 */
export const getHealthCheck = async () => {
  return await apiRequest('/api/health');
};

/**
 * Search products
 * @param {string} query - Search query
 * @param {number} limit - Number of results
 * @returns {Promise} - Search results
 */
export const searchProducts = async (query, limit = 10) => {
  return await apiRequest(`/api/products/search?q=${encodeURIComponent(query)}&limit=${limit}`);
};

/**
 * Get application statistics
 * @returns {Promise} - App statistics
 */
export const getAppStats = async () => {
  return await apiRequest('/api/stats');
};

/**
 * Contact support
 * @param {Object} contactData - Contact form data
 * @param {string} contactData.name - User name
 * @param {string} contactData.email - User email
 * @param {string} contactData.subject - Message subject
 * @param {string} contactData.message - Message content
 * @returns {Promise} - Contact response
 */
export const contactSupport = async (contactData) => {
  return await apiRequest('/api/contact', {
    method: 'POST',
    body: JSON.stringify(contactData),
  });
};

/**
 * Check server status
 * @returns {Promise} - Server status
 */
export const getServerStatus = async () => {
  return await apiRequest('/api/status');
};

// Auth Service Functions
export const authService = {
  /**
   * Login user with email_or_username and password
   * @param {string} email_or_username - User email or username
   * @param {string} password - User password
   * @returns {Promise} - Login response
   */
  login: async (email_or_username, password) => {
    return await apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email_or_username, password }),
    });
  },

  /**
   * Register new user
   * @param {Object} userData - User registration data
   * @returns {Promise} - Registration response
   */
  register: async (userData) => {
    return await apiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  /**
   * Google OAuth login
   * @param {string} token - Google OAuth token
   * @returns {Promise} - Login response
   */
  googleAuth: async (token) => {
    return await apiRequest('/api/auth/google', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  },

  /**
   * Logout user
   * @returns {Promise} - Logout response
   */
  logout: async () => {
    return await apiRequest('/api/auth/logout', {
      method: 'POST',
    });
  },

  /**
   * Get current user profile
   * @returns {Promise} - User profile data
   */
  getCurrentUser: async () => {
    return await apiRequest('/api/auth/me');
  },

  /**
   * Change user password
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @returns {Promise} - Change password response
   */
  changePassword: async (currentPassword, newPassword) => {
    return await apiRequest('/api/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
  },

  /**
   * Request password reset
   * @param {string} email - User email
   * @returns {Promise} - Forgot password response
   */
  forgotPassword: async (email) => {
    return await apiRequest('/api/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  /**
   * Reset password with token
   * @param {string} token - Reset token
   * @param {string} newPassword - New password
   * @returns {Promise} - Reset password response
   */
  resetPassword: async (token, newPassword) => {
    return await apiRequest('/api/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    });
  },
};

// User Service Functions
export const userService = {
  /**
   * Get user profile
   * @returns {Promise} - User profile data
   */
  getUserProfile: async () => {
    return await apiRequest('/api/users/profile');
  },

  /**
   * Update user basic information
   * @param {Object} basicInfo - Basic user information
   * @returns {Promise} - Update response
   */
  updateUserBasicInfo: async (basicInfo) => {
    return await apiRequest('/api/users/settings/basic', {
      method: 'PUT',
      body: JSON.stringify(basicInfo),
    });
  },

  /**
   * Setup user profile for new users
   * @param {Object} profileData - Profile setup data
   * @returns {Promise} - Setup response
   */
  setupProfile: async (profileData) => {
    return await apiRequest('/api/users/profile/setup', {
      method: 'POST',
      body: JSON.stringify(profileData),
    });
  },

  /**
   * Update user profile information
   * @param {Object} profileData - Profile data to update
   * @returns {Promise} - Update response
   */
  updateUserProfile: async (profileData) => {
    return await apiRequest('/api/users/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },

  /**
   * Get all available allergens
   * @returns {Promise} - List of allergens
   */
  getAllergens: async () => {
    return await apiRequest('/api/allergens');
  },

  /**
   * Get available allergens (alias for getAllergens)
   * @returns {Promise} - List of allergens
   */
  getAvailableAllergens: async () => {
    return await apiRequest('/api/allergens');
  },

  /**
   * Get user's allergens
   * @returns {Promise} - User's allergens
   */
  getUserAllergens: async () => {
    return await apiRequest('/api/users/allergens');
  },

  /**
   * Add allergen to user profile
   * @param {Object} allergenData - Allergen data (can be ID or custom allergen object)
   * @returns {Promise} - Add allergen response
   */
  addAllergen: async (allergenData) => {
    return await apiRequest('/api/users/allergens', {
      method: 'POST',
      body: JSON.stringify(allergenData),
    });
  },

  /**
   * Remove allergen from user profile
   * @param {number} allergenId - Allergen ID
   * @returns {Promise} - Remove allergen response
   */
  removeAllergen: async (allergenId) => {
    return await apiRequest(`/api/users/allergens/${allergenId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Update user language preference
   * @param {string} language - Language code (tr, en)
   * @returns {Promise} - Update response
   */
  updateLanguagePreference: async (language) => {
    return await apiRequest('/api/users/language', {
      method: 'PUT',
      body: JSON.stringify({ language }),
    });
  },
};

// User API (alias for userService for backward compatibility)
export const userAPI = userService;

const apiExports = {
  apiRequest,
  analyzeImage,
  getHealthCheck,
  searchProducts,
  getAppStats,
  contactSupport,
  getServerStatus,
  authService,
  userService,
  userAPI,
};

export default apiExports;
