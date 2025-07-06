<<<<<<< HEAD
import React, { useState } from 'react';
import { Camera, Upload, X, AlertCircle, Loader2 } from 'lucide-react';
import { analyzeImage } from '../services/api';
import NutriScoreDisplay from '../components/NutriScoreDisplay';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/HomePage.css';
import foodlensLogo from '../assets/images/foodlens.png';

const HomePage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [language, setLanguage] = useState('tr');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  
  const fileInputRef = React.useRef(null);
  const cameraInputRef = React.useRef(null);

  const handleImageSelect = (file) => {
    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
    setError(null);
    setAnalysisResult(null);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setError(language === 'tr' ? 'Dosya boyutu 10MB\'dan küçük olmalıdır.' : 'File size must be less than 10MB.');
        return;
      }
      
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        setError(language === 'tr' ? 'Geçerli bir resim dosyası seçin.' : 'Please select a valid image file.');
        return;
      }
      
      handleImageSelect(file);
    }
  };

  const handleCameraCapture = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleImageSelect(file);
    }
  };

  const analyzeProduct = async () => {
    if (!selectedImage) {
      setError(language === 'tr' ? 'Lütfen bir resim seçin.' : 'Please select an image.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await analyzeImage(selectedImage, language);
      
      if (result.success) {
        setAnalysisResult(result);
      } else {
        setError(result.error || (language === 'tr' ? 'Analiz başarısız oldu.' : 'Analysis failed.'));
      }
    } catch (err) {
      setError(language === 'tr' ? 'Bağlantı hatası. Lütfen tekrar deneyin.' : 'Connection error. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setSelectedImage(null);
    setPreviewUrl(null);
    setAnalysisResult(null);
    setError(null);
    
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  const renderNutriScoreResults = () => {
    if (!analysisResult?.nutri_score) return null;

    const { nutri_score, recommendations, nutrition, data_quality, processing } = analysisResult;
    const currentLang = language === 'tr' ? 'tr' : 'en';

    return (
      <div className="results-container">
        <div className="nutri-score-card">
          <div className="card-header">
            <h3>{language === 'tr' ? 'Nutri-Score Analizi' : 'Nutri-Score Analysis'}</h3>
            <div className="score-display">
              <span className="score-label">
                {language === 'tr' ? 'Puan:' : 'Score:'}
              </span>
              <span className="score-value">{nutri_score.score}</span>
            </div>
          </div>

          <NutriScoreDisplay
            grade={nutri_score.grade}
            score={nutri_score.score}
            color={nutri_score.color}
            size="large"
          />

          <div className="points-grid">
            <div className="negative-points">
              <h4>{language === 'tr' ? 'Olumsuz Puanlar' : 'Negative Points'}</h4>
              <p className="points-value negative">{nutri_score.negative_points}</p>
            </div>
            <div className="positive-points">
              <h4>{language === 'tr' ? 'Olumlu Puanlar' : 'Positive Points'}</h4>
              <p className="points-value positive">{nutri_score.positive_points}</p>
            </div>
          </div>

          <div className="nutrition-breakdown">
            <h4>{language === 'tr' ? 'Besin Değerleri (100g başına)' : 'Nutritional Values (per 100g)'}</h4>
            <div className="nutrition-grid">
              <div className="nutrition-item">
                <div className="nutrition-label">
                  {language === 'tr' ? 'Enerji' : 'Energy'}
                </div>
                <div className="nutrition-value">
                  {nutrition?.energy_kj || nutri_score.nutrition_data?.energy_kj || 0} kJ / {nutrition?.energy_kcal || nutri_score.nutrition_data?.energy_kcal || 0} kcal
                </div>
              </div>
              <div className="nutrition-item">
                <div className="nutrition-label">
                  {language === 'tr' ? 'Yağ' : 'Fat'}
                </div>
                <div className="nutrition-value">
                  {nutrition?.fat || nutri_score.nutrition_data?.fat || 0}g
                </div>
              </div>
              <div className="nutrition-item">
                <div className="nutrition-label">
                  {language === 'tr' ? 'Doymuş Yağ' : 'Saturated Fat'}
                </div>
                <div className="nutrition-value">
                  {nutrition?.saturated_fat || nutri_score.nutrition_data?.saturated_fat || 0}g
                </div>
              </div>
              <div className="nutrition-item">
                <div className="nutrition-label">
                  {language === 'tr' ? 'Karbonhidrat' : 'Carbohydrates'}
                </div>
                <div className="nutrition-value">
                  {nutrition?.carbohydrates || nutri_score.nutrition_data?.carbohydrates || 0}g
                </div>
              </div>
              <div className="nutrition-item">
                <div className="nutrition-label">
                  {language === 'tr' ? 'Şeker' : 'Sugars'}
                </div>
                <div className="nutrition-value">
                  {nutrition?.sugars || nutri_score.nutrition_data?.sugars || 0}g
                </div>
              </div>
              <div className="nutrition-item">
                <div className="nutrition-label">
                  {language === 'tr' ? 'Lif' : 'Fiber'}
                </div>
                <div className="nutrition-value">
                  {nutrition?.fiber || nutri_score.nutrition_data?.fiber || 0}g
                </div>
              </div>
              <div className="nutrition-item">
                <div className="nutrition-label">
                  {language === 'tr' ? 'Protein' : 'Protein'}
                </div>
                <div className="nutrition-value">
                  {nutrition?.proteins || nutri_score.nutrition_data?.proteins || 0}g
                </div>
              </div>
              <div className="nutrition-item">
                <div className="nutrition-label">
                  {language === 'tr' ? 'Tuz' : 'Salt'}
                </div>
                <div className="nutrition-value">
                  {nutrition?.salt || nutri_score.nutrition_data?.salt || 0}g
                </div>
              </div>
            </div>
          </div>

          {/* Data quality information */}
          {(analysisResult.data_quality || data_quality) && (
            <div className="data-quality">
              <h4>{language === 'tr' ? 'Veri Kalitesi' : 'Data Quality'}</h4>
              <div className="quality-metrics">
                <div className="quality-item">
                  <span className="quality-label">{language === 'tr' ? 'Bütünlük' : 'Completeness'}</span>
                  <div className="quality-bar-container">
                    <div 
                      className="quality-bar" 
                      style={{
                        width: `${data_quality?.completeness || analysisResult.data_quality?.completeness || 0}%`, 
                        backgroundColor: (data_quality?.completeness || analysisResult.data_quality?.completeness || 0) > 70 ? '#4CAF50' : '#FFA726'
                      }}
                    ></div>
                    <span className="quality-value">{Math.round(data_quality?.completeness || analysisResult.data_quality?.completeness || 0)}%</span>
                  </div>
                </div>
                <div className="quality-item">
                  <span className="quality-label">{language === 'tr' ? 'Güven' : 'Confidence'}</span>
                  <div className="quality-bar-container">
                    <div 
                      className="quality-bar" 
                      style={{
                        width: `${data_quality?.confidence || analysisResult.data_quality?.confidence || 0}%`, 
                        backgroundColor: (data_quality?.confidence || analysisResult.data_quality?.confidence || 0) > 70 ? '#4CAF50' : '#FFA726'
                      }}
                    ></div>
                    <span className="quality-value">{Math.round(data_quality?.confidence || analysisResult.data_quality?.confidence || 0)}%</span>
                  </div>
                </div>
              </div>
              {(data_quality?.manual_review_needed || analysisResult.data_quality?.manual_review_needed) && (
                <div className="manual-review-warning">
                  <AlertCircle size={16} />
                  <span>{language === 'tr' ? 'Bazı besin değerleri eksik veya düşük güvenilirlikte.' : 
                    'Some nutrition values are missing or have low confidence.'}</span>
                </div>
              )}
              
              {/* Processing information */}
              {processing && (
                <div className="processing-info">
                  <h5>{language === 'tr' ? 'İşleme Bilgisi' : 'Processing Info'}</h5>
                  <div className="processing-details">
                    <div className="processing-item">
                      <span className="processing-label">{language === 'tr' ? 'Süre' : 'Time'}</span>
                      <span className="processing-value">{processing.time_seconds.toFixed(2)}s</span>
                    </div>
                    <div className="processing-item">
                      <span className="processing-label">{language === 'tr' ? 'OCR Güven' : 'OCR Confidence'}</span>
                      <span className="processing-value">{(processing.ocr_confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {recommendations && recommendations[currentLang] && (
            <div className="recommendations">
              <h4>{language === 'tr' ? 'Öneriler' : 'Recommendations'}</h4>
              <ul>
                {recommendations[currentLang].map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {(analysisResult.ocr_text || analysisResult.text) && (
            <div className="ocr-text">
              <h4>{language === 'tr' ? 'Tespit Edilen Metin' : 'Detected Text'}</h4>
              <p>{analysisResult.ocr_text || analysisResult.text}</p>
            </div>
          )}

          <button onClick={resetAnalysis} className="new-analysis-btn">
            {language === 'tr' ? 'Yeni Analiz' : 'New Analysis'}
          </button>
        </div>
      </div>
    );
  };

  // Main interface when no image is selected
  if (!selectedImage) {
    return (
      <div className="homepage">
        <div className="logo-container">
          <img src={foodlensLogo} alt="FoodLens Logo" className="foodlens-logo" />
        </div>
        <div className="main-card">
          <div className="header-section">
            <h2 className="main-title">
              {language === 'tr' ? 'Gıda Ürünü Analizi' : 'Food Product Analysis'}
            </h2>
            <p className="main-subtitle">
              {language === 'tr' 
                ? 'Ürün etiketinin fotoğrafını çekin veya yükleyin, OCR ile metin tanıma ve Nutri-Score analizi yapın.'
                : 'Take a photo or upload an image of the product label for OCR text recognition and Nutri-Score analysis.'
              }
            </p>
            
            <div className="language-selector">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="language-select"
              >
                <option value="tr">Türkçe</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>

          <div className="action-buttons">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden-input"
            />
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleCameraCapture}
              className="hidden-input"
            />
            
            <button
              onClick={() => cameraInputRef.current?.click()}
              className="action-btn camera-btn"
            >
              <Camera size={32} />
              <span>{language === 'tr' ? 'Fotoğraf Çek' : 'Take a Picture'}</span>
            </button>
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="action-btn upload-btn"
            >
              <Upload size={32} />
              <span>{language === 'tr' ? 'Dosya Yükle' : 'Upload from'}</span>
            </button>
          </div>

          {error && (
            <div className="error-message">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Interface when image is selected
  return (
    <div className="homepage">
      <div className="logo-container">
        <img src={foodlensLogo} alt="FoodLens Logo" className="foodlens-logo" />
      </div>
      <div className="main-card">
        <div className="header-section">
          <h2 className="main-title">
            {language === 'tr' ? 'Ürün Analizi' : 'Product Analysis'}
          </h2>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="language-select"
          >
            <option value="tr">Türkçe</option>
            <option value="en">English</option>
          </select>
        </div>

        <div className="image-preview">
          <div className="preview-container">
            <img
              src={previewUrl}
              alt="Preview"
              className="preview-image"
            />
            <button
              onClick={resetAnalysis}
              className="remove-btn"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {error && (
          <div className="error-message">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        <button
          onClick={analyzeProduct}
          disabled={isAnalyzing}
          className={`analyze-btn ${isAnalyzing ? 'analyzing' : ''}`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="spinning" size={20} />
              <span>{language === 'tr' ? 'Analiz Ediliyor...' : 'Analyzing...'}</span>
            </>
          ) : (
            <span>{language === 'tr' ? 'Analiz Et' : 'Analyze Product'}</span>
          )}
        </button>
      </div>

      {isAnalyzing && (
        <div className="loading-container">
          <LoadingSpinner message={language === 'tr' ? 'Ürün analiz ediliyor...' : 'Analyzing product...'} />
        </div>
      )}

      {analysisResult && renderNutriScoreResults()}
=======
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
>>>>>>> fdd3cedf94404767e3a5728d43eb0c330c6b1ff6
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
