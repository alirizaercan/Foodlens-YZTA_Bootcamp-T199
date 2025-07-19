/**
 * Services Index
 * Central export point for all FoodLens services
 */

// Core API service
export { default as api } from './api';
export * from './api';

// Authentication service
export { default as authService } from './authService';
export * from './authService';

// User service
export { default as userService } from './userService';
export * from './userService';

// Product service
export { default as productService } from './productService';
export * from './productService';

// Recommendation service
export { default as recommendationService } from './recommendationService';
export * from './recommendationService';

// Analytics service
export { default as analyticsService } from './analyticsService';
export * from './analyticsService';

// Utils service
export { default as utilsService } from './utilsService';
export * from './utilsService';

// Service collections for convenient importing
export const services = {
  api: require('./api').default,
  auth: require('./authService').default,
  user: require('./userService').default,
  product: require('./productService').default,
  recommendation: require('./recommendationService').default,
  analytics: require('./analyticsService').default,
  utils: require('./utilsService').default,
};

// Common service functions
export const initializeServices = () => {
  console.log('FoodLens Services initialized');
  
  // You can add any global service initialization here
  // such as setting up interceptors, default headers, etc.
};

export default services;
