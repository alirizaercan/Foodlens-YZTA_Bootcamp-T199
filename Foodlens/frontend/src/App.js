import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import './styles/globals.css';

// Import pages
import HomePage from './pages/HomePage';
import AnalysisResultsPage from './pages/AnalysisResultsPage';
import AuthenticationPage from './pages/AuthenticationPage';
import UserProfilePage from './pages/UserProfilePage';
import ProductHistoryPage from './pages/ProductHistoryPage';
import RecommendationsPage from './pages/RecommendationsPage';
import ProductSearchPage from './pages/ProductSearchPage';

// Import components
import Header from './components/Header';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';

// Import context providers
import { AuthProvider } from './context/AuthContext';
import { AppProvider } from './context/AppContext';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppProvider>
          <Router
            future={{
              v7_startTransition: true,
              v7_relativeSplatPath: true
            }}
          >
            <div className="App">
              <Header />
              <main className="main-content">
                <Routes>
                  {/* Public routes */}
                  <Route path="/" element={<HomePage />} />
                  <Route path="/login" element={<AuthenticationPage />} />
                  <Route path="/register" element={<AuthenticationPage />} />
                  
                  {/* Analysis result page - can be accessed without login for basic functionality */}
                  <Route path="/analysis" element={<AnalysisResultsPage />} />
                  <Route path="/analysis/:id" element={<AnalysisResultsPage />} />
                  
                  {/* Product search - public access */}
                  <Route path="/search" element={<ProductSearchPage />} />
                  
                  {/* Protected routes - require authentication */}
                  <Route 
                    path="/profile" 
                    element={<ProtectedRoute element={<UserProfilePage />} />} 
                  />
                  <Route 
                    path="/history" 
                    element={<ProtectedRoute element={<ProductHistoryPage />} />} 
                  />
                  <Route 
                    path="/recommendations" 
                    element={<ProtectedRoute element={<RecommendationsPage />} />} 
                  />
                  
                  {/* Redirect unknown routes to home */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </main>
              <Footer />
            </div>
          </Router>
        </AppProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
