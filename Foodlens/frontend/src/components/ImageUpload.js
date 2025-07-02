import React, { useState } from 'react';

const ImageUpload = ({ onAnalysisComplete }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    
    setIsAnalyzing(true);
    
    // Simulate OCR analysis process
    setTimeout(() => {
      const mockAnalysisData = {
        productName: "Sample Product",
        ingredients: "Water, Sugar, Salt, Natural Flavors",
        nutriScore: "B",
        healthScore: "7/10",
        calories: "45",
        recommendations: "This product has moderate nutritional value. Consider checking sodium content."
      };
      
      setIsAnalyzing(false);
      onAnalysisComplete(mockAnalysisData);
    }, 2000);
  };

  return (
    <div className="image-upload">
      <div className="upload-area">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="file-input"
          id="file-input"
        />
        <label htmlFor="file-input" className="upload-label">
          {selectedFile ? selectedFile.name : "Choose Image or Take Photo"}
        </label>
      </div>
      
      {selectedFile && (
        <div className="preview-section">
          <img 
            src={URL.createObjectURL(selectedFile)} 
            alt="Selected product" 
            className="image-preview"
          />
          <button 
            onClick={handleAnalyze} 
            disabled={isAnalyzing}
            className="btn btn-primary"
          >
            {isAnalyzing ? "Analyzing..." : "Analyze Product"}
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
