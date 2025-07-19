/**
 * Product Service for FoodLens Application
 * Handles all product analysis and OCR API calls
 */

import { apiRequest } from './api';
import { getAuthHeaders } from './authService';

/**
 * Analyze product image with OCR and nutrition analysis
 * @param {File} imageFile - Product image file
 * @param {Object} options - Analysis options
 * @param {string} options.language - Language code (tr/en)
 * @param {string} options.productName - Optional product name
 * @param {string} options.brand - Optional brand name
 * @returns {Promise} - Analysis results with OCR data and nutrition info
 */
export const analyzeProductImage = async (imageFile, options = {}) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('language', options.language || 'tr');
  
  if (options.productName) {
    formData.append('product_name', options.productName);
  }
  
  if (options.brand) {
    formData.append('brand', options.brand);
  }

  return await apiRequest('/api/analysis/analyze', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: formData,
  });
};

/**
 * Advanced nutrition analysis with detailed breakdown
 * @param {File} imageFile - Product image file
 * @param {Object} options - Analysis options
 * @returns {Promise} - Detailed nutrition analysis
 */
export const advancedNutritionAnalysis = async (imageFile, options = {}) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  if (options.language) {
    formData.append('language', options.language);
  }
  
  if (options.analysisType) {
    formData.append('analysis_type', options.analysisType);
  }

  return await apiRequest('/api/nutrition-analysis/analyze', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: formData,
  });
};

/**
 * Debug OCR functionality (development only)
 * @param {File} imageFile - Image file for OCR testing
 * @returns {Promise} - OCR debug information
 */
export const debugOCR = async (imageFile) => {
  const formData = new FormData();
  formData.append('image', imageFile);

  return await apiRequest('/api/nutrition-analysis/debug-ocr', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: formData,
  });
};

/**
 * Search products by name or barcode
 * @param {string} query - Search query (product name or barcode)
 * @param {Object} options - Search options
 * @param {number} options.limit - Maximum number of results (default: 10)
 * @param {string} options.category - Product category filter
 * @param {string} options.brand - Brand filter
 * @returns {Promise} - Search results
 */
export const searchProducts = async (query, options = {}) => {
  const params = new URLSearchParams({
    q: query,
    limit: options.limit || 10,
  });
  
  if (options.category) {
    params.append('category', options.category);
  }
  
  if (options.brand) {
    params.append('brand', options.brand);
  }

  return await apiRequest(`/api/products/search?${params.toString()}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get product by barcode
 * @param {string} barcode - Product barcode
 * @returns {Promise} - Product information
 */
export const getProductByBarcode = async (barcode) => {
  return await apiRequest(`/api/products/barcode/${barcode}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get product details by ID
 * @param {string} productId - Product ID
 * @returns {Promise} - Product details
 */
export const getProductById = async (productId) => {
  return await apiRequest(`/api/products/${productId}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Save analyzed product to user's history
 * @param {Object} productData - Product analysis data
 * @returns {Promise} - Save response
 */
export const saveProductAnalysis = async (productData) => {
  return await apiRequest('/api/products/save-analysis', {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(productData),
  });
};

/**
 * Get user's product analysis history
 * @param {Object} options - Query options
 * @param {number} options.page - Page number (default: 1)
 * @param {number} options.limit - Items per page (default: 20)
 * @param {string} options.sortBy - Sort field (date, rating, name)
 * @param {string} options.order - Sort order (asc, desc)
 * @returns {Promise} - Analysis history
 */
export const getAnalysisHistory = async (options = {}) => {
  const params = new URLSearchParams({
    page: options.page || 1,
    limit: options.limit || 20,
    sort_by: options.sortBy || 'date',
    order: options.order || 'desc',
  });

  return await apiRequest(`/api/products/history?${params.toString()}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Get product categories
 * @returns {Promise} - Available product categories
 */
export const getProductCategories = async () => {
  return await apiRequest('/api/products/categories', {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
    },
  });
};

/**
 * Report incorrect product information
 * @param {string} productId - Product ID
 * @param {Object} reportData - Report details
 * @param {string} reportData.issue_type - Type of issue
 * @param {string} reportData.description - Issue description
 * @returns {Promise} - Report response
 */
export const reportProductIssue = async (productId, reportData) => {
  return await apiRequest(`/api/products/${productId}/report`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(reportData),
  });
};

export default {
  analyzeProductImage,
  advancedNutritionAnalysis,
  debugOCR,
  searchProducts,
  getProductByBarcode,
  getProductById,
  saveProductAnalysis,
  getAnalysisHistory,
  getProductCategories,
  reportProductIssue,
};
