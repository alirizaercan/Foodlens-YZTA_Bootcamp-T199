/**
 * API Service for FoodLens Application
 * Handles all API requests to the backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

/**
 * Generic API request function
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Request options
 * @returns {Promise} - Response data
 */
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  // Remove Content-Type header for FormData
  if (options.body instanceof FormData) {
    delete defaultOptions.headers['Content-Type'];
  }

  const config = { ...defaultOptions, ...options };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Request Error:', error);
    throw error;
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

export default {
  apiRequest,
  analyzeImage,
  getHealthCheck,
  searchProducts,
};
