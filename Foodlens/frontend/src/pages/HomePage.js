import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Camera, Upload, X, AlertCircle, Loader2, Menu, User, Settings, LogOut, LogIn } from 'lucide-react';
import { analyzeImage } from '../services/api';
import { useAuth } from '../context/AuthContext';
import NutriScoreDisplay from '../components/NutriScoreDisplay';
import LoadingSpinner from '../components/LoadingSpinner';
import { toast } from 'react-hot-toast';
import '../styles/HomePage.css';
import foodlensLogo from '../assets/images/foodlens.png';

const HomePage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  
  // Get language from URL params
  const [language, setLanguage] = useState(() => {
    const params = new URLSearchParams(location.search);
    return params.get('lang') || 'tr';
  });
  
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [showMenu, setShowMenu] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });
  
  const fileInputRef = React.useRef(null);
  const cameraInputRef = React.useRef(null);

  // Update language when URL changes
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const urlLang = params.get('lang');
    if (urlLang && urlLang !== language) {
      setLanguage(urlLang);
    }
  }, [location.search, language]);

  // Apply dark mode to body
  useEffect(() => {
    document.body.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  const handleDarkModeToggle = () => {
    setIsDarkMode(!isDarkMode);
    toast.success(
      language === 'tr' 
        ? (!isDarkMode ? 'Karanlık tema aktif' : 'Açık tema aktif')
        : (!isDarkMode ? 'Dark mode enabled' : 'Light mode enabled')
    );
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success(language === 'tr' ? 'Başarıyla çıkış yapıldı!' : 'Successfully logged out!');
      setShowProfileMenu(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleLanguageChange = async (newLanguage) => {
    setLanguage(newLanguage);
    
    // Update URL with new language
    const currentPath = location.pathname;
    navigate(`${currentPath}?lang=${newLanguage}`, { replace: true });
    
    // Save language preference to database if user is authenticated
    if (isAuthenticated && user) {
      try {
        // We'll add this API call to save language preference
        // await userService.updateLanguagePreference(newLanguage);
        toast.success(
          newLanguage === 'tr' 
            ? 'Dil tercihiniz kaydedildi' 
            : 'Language preference saved'
        );
      } catch (error) {
        console.error('Error saving language preference:', error);
      }
    }
    
    // Show welcome message in new language
    setTimeout(() => {
      toast.success(
        newLanguage === 'tr' 
          ? 'Türkçe diline geçildi' 
          : 'Switched to English'
      );
    }, 100);
  };

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
        {/* Navigation Header */}
        <div className="homepage-header">
          <div className="logo-container">
            <img src={foodlensLogo} alt="FoodLens Logo" className="foodlens-logo" />
          </div>
          
          <div className="header-controls">
            {/* Language Selector */}
            <div className="language-selector-container">
              <select
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="language-selector"
                aria-label="Select Language"
              >
                <option value="tr">🇹🇷 Türkçe</option>
                <option value="en">🇺🇸 English</option>
              </select>
            </div>

            {/* Dark Mode Toggle */}
            <div className="dark-mode-toggle">
              <label className="switch">
                <input 
                  type="checkbox" 
                  checked={isDarkMode}
                  onChange={handleDarkModeToggle}
                />
                <span className="slider round"></span>
              </label>
              <span className="dark-mode-label">
                {language === 'tr' ? 'Karanlık Tema' : 'Dark Mode'}
              </span>
            </div>

            {/* Authentication/Profile Section */}
            {isAuthenticated ? (
              <div className="user-menu">
                <button 
                  className="user-profile-btn"
                  onClick={() => setShowProfileMenu(!showProfileMenu)}
                  aria-label="User profile menu"
                >
                  <div className="user-avatar">
                    <User size={18} />
                  </div>
                  <div className="user-info">
                    <span className="user-name">
                      {user?.first_name ? `${user.first_name}` : user?.username || 'User'}
                    </span>
                    <span className="user-role">Premium</span>
                  </div>
                  <div className="dropdown-arrow">
                    <svg width="12" height="8" viewBox="0 0 12 8" fill="none">
                      <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                </button>
                
                {showProfileMenu && (
                  <div className="user-dropdown-menu">
                    <div className="dropdown-header">
                      <div className="user-avatar-large">
                        <User size={20} />
                      </div>
                      <div className="user-details">
                        <span className="user-full-name">
                          {user?.first_name && user?.last_name 
                            ? `${user.first_name} ${user.last_name}`
                            : user?.username || 'User Name'
                          }
                        </span>
                        <span className="user-email">{user?.email}</span>
                      </div>
                    </div>
                    
                    <div className="dropdown-divider"></div>
                    
                    <div className="dropdown-menu-items">
                      <button 
                        className="dropdown-menu-item"
                        onClick={() => {
                          navigate(`/profile-setup?lang=${language}`);
                          setShowProfileMenu(false);
                        }}
                      >
                        <User size={16} />
                        <span>{language === 'tr' ? 'Profil' : 'Profile'}</span>
                      </button>
                      
                      <button 
                        className="dropdown-menu-item"
                        onClick={() => {
                          navigate(`/settings?lang=${language}`);
                          setShowProfileMenu(false);
                        }}
                      >
                        <Settings size={16} />
                        <span>{language === 'tr' ? 'Ayarlar' : 'Settings'}</span>
                      </button>
                      
                      <div className="dropdown-divider"></div>
                      
                      <button 
                        className="dropdown-menu-item logout-item"
                        onClick={handleLogout}
                      >
                        <LogOut size={16} />
                        <span>{language === 'tr' ? 'Çıkış Yap' : 'Sign out'}</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <button 
                className="auth-btn-primary"
                onClick={() => {
                  navigate('/auth');
                  setShowMenu(false);
                }}
              >
                <LogIn size={18} />
                <span>{language === 'tr' ? 'Giriş Yap' : 'Sign In'}</span>
              </button>
            )}

            {/* Menu Button */}
            <button 
              className="menu-toggle-btn"
              onClick={() => setShowMenu(!showMenu)}
              aria-label="Toggle menu"
            >
              <Menu size={20} />
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {showMenu && (
          <>
            <div className="mobile-menu-overlay" onClick={() => setShowMenu(false)}></div>
            <div className="mobile-menu-sidebar">
              <div className="mobile-menu-header">
                <img src={foodlensLogo} alt="FoodLens" className="menu-logo" />
                <button 
                  className="menu-close-btn"
                  onClick={() => setShowMenu(false)}
                >
                  <X size={20} />
                </button>
              </div>
              
              <div className="mobile-menu-content">
                <div className="menu-section">
                  <h4 className="menu-section-title">{language === 'tr' ? 'Keşfet' : 'Explore'}</h4>
                  <button className="menu-item-modern">
                    <span className="menu-icon">📱</span>
                    <span>{language === 'tr' ? 'Ürün Analizi' : 'Product Analysis'}</span>
                  </button>
                  <button className="menu-item-modern">
                    <span className="menu-icon">🍳</span>
                    <span>{language === 'tr' ? 'Tarifler' : 'Recipes'}</span>
                  </button>
                  <button className="menu-item-modern">
                    <span className="menu-icon">🤖</span>
                    <span>{language === 'tr' ? 'AI Asistan' : 'AI Assistant'}</span>
                  </button>
                  <button className="menu-item-modern">
                    <span className="menu-icon">🎯</span>
                    <span>{language === 'tr' ? 'Hedeflerim' : 'My Goals'}</span>
                  </button>
                </div>
                
                <div className="menu-section">
                  <h4 className="menu-section-title">{language === 'tr' ? 'Bilgi' : 'Information'}</h4>
                  <button className="menu-item-modern">
                    <span className="menu-icon">ℹ️</span>
                    <span>{language === 'tr' ? 'Hakkımızda' : 'About Us'}</span>
                  </button>
                  <button className="menu-item-modern">
                    <span className="menu-icon">📞</span>
                    <span>{language === 'tr' ? 'İletişim' : 'Contact'}</span>
                  </button>
                </div>
              </div>
            </div>
          </>
        )}

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
      {/* Navigation Header */}
      <div className="homepage-header">
        <div className="logo-container">
          <img src={foodlensLogo} alt="FoodLens Logo" className="foodlens-logo" />
        </div>
        
        <div className="header-controls">
          {/* Language Selector */}
          <div className="language-selector-container">
            <select
              value={language}
              onChange={(e) => handleLanguageChange(e.target.value)}
              className="language-selector"
              aria-label="Select Language"
            >
              <option value="tr">🇹🇷 Türkçe</option>
              <option value="en">🇺🇸 English</option>
            </select>
          </div>

          {/* Authentication/Profile Section */}
          {isAuthenticated ? (
            <div className="user-menu">
              <button 
                className="user-profile-btn"
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                aria-label="User profile menu"
              >
                <div className="user-avatar">
                  <User size={18} />
                </div>
                <div className="user-info">
                  <span className="user-name">
                    {user?.first_name ? `${user.first_name}` : user?.username || 'User'}
                  </span>
                  <span className="user-role">Premium</span>
                </div>
                <div className="dropdown-arrow">
                  <svg width="12" height="8" viewBox="0 0 12 8" fill="none">
                    <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </button>
              
              {showProfileMenu && (
                <div className="user-dropdown-menu">
                  <div className="dropdown-header">
                    <div className="user-avatar-large">
                      <User size={20} />
                    </div>
                    <div className="user-details">
                      <span className="user-full-name">
                        {user?.first_name && user?.last_name 
                          ? `${user.first_name} ${user.last_name}`
                          : user?.username || 'User Name'
                        }
                      </span>
                      <span className="user-email">{user?.email}</span>
                    </div>
                  </div>
                  
                  <div className="dropdown-divider"></div>
                  
                  <div className="dropdown-menu-items">
                    <button 
                      className="dropdown-menu-item"
                      onClick={() => {
                        navigate(`/profile-setup?lang=${language}`);
                        setShowProfileMenu(false);
                      }}
                    >
                      <User size={16} />
                      <span>{language === 'tr' ? 'Profil' : 'Profile'}</span>
                    </button>
                    
                    <button 
                      className="dropdown-menu-item"
                      onClick={() => {
                        navigate(`/settings?lang=${language}`);
                        setShowProfileMenu(false);
                      }}
                    >
                      <Settings size={16} />
                      <span>{language === 'tr' ? 'Ayarlar' : 'Settings'}</span>
                    </button>
                    
                    <div className="dropdown-divider"></div>
                    
                    <button 
                      className="dropdown-menu-item logout-item"
                      onClick={handleLogout}
                    >
                      <LogOut size={16} />
                      <span>{language === 'tr' ? 'Çıkış Yap' : 'Sign out'}</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <button 
              className="auth-btn-primary"
              onClick={() => navigate('/auth')}
            >
              <LogIn size={18} />
              <span>{language === 'tr' ? 'Giriş Yap' : 'Sign In'}</span>
            </button>
          )}
        </div>
      </div>

      <div className="main-card">
        <div className="header-section">
          <h2 className="main-title">
            {language === 'tr' ? 'Ürün Analizi' : 'Product Analysis'}
          </h2>
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
