import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import './styles/globals.css';

// Import contexts
import { AuthProvider, useAuth } from './context/AuthContext';

// Import pages
import HomePage from './pages/HomePage';
import AuthenticationPage from './pages/AuthenticationPage';
import SettingsPage from './pages/SettingsPage';
import ProfileSetupPage from './pages/ProfileSetupPage';

// Import components
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="app-loading">
        <LoadingSpinner />
        <p>Loading FoodLens...</p>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/auth" replace />;
};

// Public Route Component (redirects to home if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="app-loading">
        <LoadingSpinner />
        <p>Loading FoodLens...</p>
      </div>
    );
  }
  
  return !isAuthenticated ? children : <Navigate to="/home" replace />;
};

// Main App Content Component
const AppContent = () => {
  return (
    <div className="App">
      <main className="min-h-screen">
        <Routes>
          {/* Public Routes */}
          <Route path="/auth" element={
            <PublicRoute>
              <AuthenticationPage />
            </PublicRoute>
          } />
          
          {/* Protected Routes */}
          <Route path="/home" element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          } />
          
          <Route path="/profile-setup" element={
            <ProtectedRoute>
              <ProfileSetupPage />
            </ProtectedRoute>
          } />
          
          <Route path="/settings" element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          } />
          
          {/* Default redirects */}
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </main>
      
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            theme: {
              primary: '#4aed88',
            },
          },
          error: {
            duration: 5000,
            theme: {
              primary: '#ff6b6b',
            },
          },
        }}
      />
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
