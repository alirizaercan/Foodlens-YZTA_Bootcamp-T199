/**
 * Utility Service for FoodLens Application
 * Common utility functions and helpers
 */

/**
 * Format file size for display
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted file size
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Validate image file type and size
 * @param {File} file - Image file to validate
 * @param {Object} options - Validation options
 * @param {Array} options.allowedTypes - Allowed MIME types
 * @param {number} options.maxSize - Maximum file size in bytes
 * @returns {Object} - Validation result
 */
export const validateImageFile = (file, options = {}) => {
  const allowedTypes = options.allowedTypes || ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  const maxSize = options.maxSize || 10 * 1024 * 1024; // 10MB default
  
  const errors = [];
  
  if (!allowedTypes.includes(file.type)) {
    errors.push(`File type ${file.type} is not allowed. Allowed types: ${allowedTypes.join(', ')}`);
  }
  
  if (file.size > maxSize) {
    errors.push(`File size ${formatFileSize(file.size)} exceeds maximum of ${formatFileSize(maxSize)}`);
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Compress image file
 * @param {File} file - Image file to compress
 * @param {Object} options - Compression options
 * @param {number} options.quality - Compression quality (0-1)
 * @param {number} options.maxWidth - Maximum width
 * @param {number} options.maxHeight - Maximum height
 * @returns {Promise<File>} - Compressed image file
 */
export const compressImage = (file, options = {}) => {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
      const { maxWidth = 1920, maxHeight = 1080, quality = 0.8 } = options;
      
      // Calculate new dimensions
      let { width, height } = img;
      
      if (width > maxWidth || height > maxHeight) {
        const ratio = Math.min(maxWidth / width, maxHeight / height);
        width *= ratio;
        height *= ratio;
      }
      
      canvas.width = width;
      canvas.height = height;
      
      // Draw and compress
      ctx.drawImage(img, 0, 0, width, height);
      
      canvas.toBlob(
        (blob) => {
          const compressedFile = new File([blob], file.name, {
            type: file.type,
            lastModified: Date.now(),
          });
          resolve(compressedFile);
        },
        file.type,
        quality
      );
    };
    
    img.onerror = reject;
    img.src = URL.createObjectURL(file);
  });
};

/**
 * Calculate BMI
 * @param {number} weight - Weight in kg
 * @param {number} height - Height in cm
 * @returns {number} - BMI value
 */
export const calculateBMI = (weight, height) => {
  if (!weight || !height) return 0;
  const heightInMeters = height / 100;
  return Math.round((weight / (heightInMeters * heightInMeters)) * 10) / 10;
};

/**
 * Get BMI category
 * @param {number} bmi - BMI value
 * @returns {string} - BMI category
 */
export const getBMICategory = (bmi) => {
  if (bmi < 18.5) return 'Underweight';
  if (bmi < 25) return 'Normal weight';
  if (bmi < 30) return 'Overweight';
  return 'Obese';
};

/**
 * Calculate daily calorie needs (Harris-Benedict equation)
 * @param {Object} params - Calculation parameters
 * @param {number} params.weight - Weight in kg
 * @param {number} params.height - Height in cm
 * @param {number} params.age - Age in years
 * @param {string} params.gender - Gender (male/female)
 * @param {string} params.activityLevel - Activity level
 * @returns {number} - Daily calorie needs
 */
export const calculateDailyCalories = ({ weight, height, age, gender, activityLevel }) => {
  if (!weight || !height || !age || !gender) return 0;
  
  // BMR calculation
  let bmr;
  if (gender.toLowerCase() === 'male') {
    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
  } else {
    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
  }
  
  // Activity multipliers
  const activityMultipliers = {
    sedentary: 1.2,
    lightly_active: 1.375,
    moderately_active: 1.55,
    very_active: 1.725,
    extremely_active: 1.9,
  };
  
  const multiplier = activityMultipliers[activityLevel] || 1.2;
  return Math.round(bmr * multiplier);
};

/**
 * Format nutrition value for display
 * @param {number} value - Nutrition value
 * @param {string} unit - Unit (g, mg, kcal, etc.)
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted value
 */
export const formatNutritionValue = (value, unit = '', decimals = 1) => {
  if (value === null || value === undefined) return '-';
  
  const formattedValue = Number(value).toFixed(decimals);
  return `${formattedValue}${unit ? ' ' + unit : ''}`;
};

/**
 * Convert between date formats
 * @param {string|Date} date - Date to format
 * @param {string} format - Output format (iso, locale, short)
 * @returns {string} - Formatted date
 */
export const formatDate = (date, format = 'locale') => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (!dateObj || isNaN(dateObj.getTime())) return '';
  
  switch (format) {
    case 'iso':
      return dateObj.toISOString().split('T')[0];
    case 'short':
      return dateObj.toLocaleDateString('tr-TR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });
    case 'locale':
    default:
      return dateObj.toLocaleDateString('tr-TR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      });
  }
};

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} - Debounced function
 */
export const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};

/**
 * Generate color based on nutrition score
 * @param {number} score - Nutrition score (0-100)
 * @returns {string} - Color code
 */
export const getScoreColor = (score) => {
  if (score >= 80) return '#4CAF50'; // Green
  if (score >= 60) return '#8BC34A'; // Light Green
  if (score >= 40) return '#FFC107'; // Amber
  if (score >= 20) return '#FF9800'; // Orange
  return '#F44336'; // Red
};

/**
 * Local storage helpers with error handling
 */
export const storage = {
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return defaultValue;
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Error writing to localStorage:', error);
      return false;
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Error removing from localStorage:', error);
      return false;
    }
  },
};

export default {
  formatFileSize,
  validateImageFile,
  compressImage,
  calculateBMI,
  getBMICategory,
  calculateDailyCalories,
  formatNutritionValue,
  formatDate,
  debounce,
  getScoreColor,
  storage,
};
