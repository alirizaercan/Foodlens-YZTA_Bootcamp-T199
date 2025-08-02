/**
 * User authentication context for managing user state across the application
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService, userService } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      const response = await authService.verifyToken();
      if (response.success) {
        setUser(response.user);
        setIsAuthenticated(true);
      } else {
        // Token is invalid, remove it
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      console.log('AuthContext login called with:', credentials);
      const response = await authService.login(credentials.email_or_username, credentials.password);
      console.log('AuthService login response:', response);
      
      if (response.success) {
        localStorage.setItem('auth_token', response.access_token);
        localStorage.setItem('user_data', JSON.stringify(response.user));
        setUser(response.user);
        setIsAuthenticated(true);
        return { success: true, user: response.user, isNewUser: response.is_new_user };
      }
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: 'Login failed' };
    }
  };

  const register = async (userData) => {
    try {
      console.log('AuthContext register called with:', userData);
      const response = await authService.register(userData);
      console.log('AuthService register response:', response);
      
      if (response.success) {
        localStorage.setItem('auth_token', response.access_token);
        localStorage.setItem('user_data', JSON.stringify(response.user));
        setUser(response.user);
        setIsAuthenticated(true);
        return { success: true, user: response.user, isNewUser: true };
      }
      
      // Return the error response with details
      return {
        success: false,
        error: response.error || 'Registration failed',
        details: response.details || []
      };
    } catch (error) {
      console.error('Registration failed:', error);
      return { 
        success: false, 
        error: 'Registration failed',
        details: [error.message || 'Unknown error occurred']
      };
    }
  };

  const googleLogin = async (googleToken) => {
    try {
      const response = await authService.googleAuth(googleToken);
      if (response.success) {
        localStorage.setItem('auth_token', response.access_token);
        localStorage.setItem('user_data', JSON.stringify(response.user));
        setUser(response.user);
        setIsAuthenticated(true);
        return { success: true, user: response.user, isNewUser: response.is_new_user };
      }
      return response;
    } catch (error) {
      console.error('Google login failed:', error);
      return { success: false, error: 'Google login failed' };
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const updateUser = async (userData) => {
    try {
      const response = await userService.updateUserBasicInfo(userData);
      if (response.success) {
        setUser(response.user);
        localStorage.setItem('user_data', JSON.stringify(response.user));
      }
      return response;
    } catch (error) {
      console.error('Update user failed:', error);
      return { success: false, error: 'Update failed' };
    }
  };

  const changePassword = async (passwords) => {
    try {
      return await authService.changePassword(passwords);
    } catch (error) {
      console.error('Change password failed:', error);
      return { success: false, error: 'Password change failed' };
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    googleLogin,
    logout,
    updateUser,
    changePassword,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
