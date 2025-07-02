import React from 'react';
import { useNavigate } from 'react-router-dom';
import ImageUpload from '../components/ImageUpload';

const HomePage = () => {
  const navigate = useNavigate();

  const handleAnalysisComplete = (analysisData) => {
    // Navigate to analysis results page with data
    navigate('/analysis', { state: { analysisData } });
  };

  return (
    <div className="homepage">
      <div className="container">
        <div className="hero-section">
          <h1 className="hero-title">FoodLens</h1>
          <p className="hero-subtitle">
            Smart Nutrition Analysis Platform
          </p>
          <p className="hero-description">
            Scan product labels, get instant nutritional analysis, and receive 
            personalized recommendations based on your health profile.
          </p>
        </div>

        <div className="upload-section">
          <h2>Analyze Your Product</h2>
          <p>Upload a photo of the product label to get started</p>
          <ImageUpload onAnalysisComplete={handleAnalysisComplete} />
        </div>

        <div className="features-section">
          <h2>Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <h3>OCR Text Recognition</h3>
              <p>Automatically extract ingredients from product labels</p>
            </div>
            <div className="feature-card">
              <h3>Smart Analysis</h3>
              <p>AI-powered nutritional analysis and health scoring</p>
            </div>
            <div className="feature-card">
              <h3>Personal Profiles</h3>
              <p>Customized recommendations based on your dietary needs</p>
            </div>
            <div className="feature-card">
              <h3>Alternative Suggestions</h3>
              <p>Find healthier alternatives to your products</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;

// Home page will be implemented here
// This component will handle:
// - Product scanning camera interface
// - Image upload functionality
// - Quick barcode scanning
// - Recent analysis history
// - Navigation to main features
// - User onboarding and guidance
