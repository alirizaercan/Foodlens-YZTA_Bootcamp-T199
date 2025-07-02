import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const AnalysisResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const analysisData = location.state?.analysisData;

  if (!analysisData) {
    return (
      <div className="analysis-results">
        <div className="container">
          <h2>No Analysis Data Found</h2>
          <p>Please scan a product first.</p>
          <button onClick={() => navigate('/')} className="btn btn-primary">
            Go Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="analysis-results">
      <div className="container">
        <h1>Product Analysis Results</h1>
        
        <div className="card">
          <h2>Product Information</h2>
          <p><strong>Product Name:</strong> {analysisData.productName || 'Unknown Product'}</p>
          <p><strong>Ingredients:</strong> {analysisData.ingredients || 'No ingredients detected'}</p>
        </div>

        <div className="card">
          <h2>Nutritional Analysis</h2>
          <p><strong>Nutri-Score:</strong> {analysisData.nutriScore || 'Calculating...'}</p>
          <p><strong>Health Score:</strong> {analysisData.healthScore || 'Analyzing...'}</p>
          <p><strong>Calories:</strong> {analysisData.calories || 'N/A'} per 100g</p>
        </div>

        <div className="card">
          <h2>Recommendations</h2>
          <p>{analysisData.recommendations || 'This product appears to be moderately healthy. Consider checking the ingredients for any allergens.'}</p>
        </div>

        <div className="actions">
          <button onClick={() => navigate('/')} className="btn btn-secondary">
            Scan Another Product
          </button>
          <button onClick={() => navigate('/recommendations')} className="btn btn-primary">
            View Alternatives
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalysisResultsPage;

// Analysis results page will be implemented here
// This component will handle:
// - Health score and Nutri-Score display
// - Nutritional information breakdown
// - Allergen warnings and dietary compatibility
// - AI-generated health insights
// - Alternative product recommendations
// - Save and bookmark functionality
