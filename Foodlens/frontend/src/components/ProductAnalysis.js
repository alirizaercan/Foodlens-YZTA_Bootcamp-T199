<<<<<<< HEAD
import React, { useState, useRef, useCallback } from 'react';
import { Camera, Upload, X, CheckCircle, AlertCircle, Loader2, Eye, EyeOff } from 'lucide-react';
import { useImageUpload } from '../hooks/useImageUpload';
import { useApi } from '../hooks/useApi';
import NutriScoreDisplay from './NutriScoreDisplay';
import IngredientsList from './IngredientsList';
import LoadingSpinner from './LoadingSpinner';

const ProductAnalysis = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [language, setLanguage] = useState('tr');
  const [productName, setProductName] = useState('');
  const [brand, setBrand] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showOCRDetails, setShowOCRDetails] = useState(false);
  const [error, setError] = useState(null);
  
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);
  const { callApi } = useApi();
  const { uploadImage } = useImageUpload();

  const handleImageSelect = useCallback((file) => {
    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
    setError(null);
    setAnalysisResult(null);
  }, []);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setError('Dosya boyutu 10MB\'dan küçük olmalıdır.');
        return;
      }
      
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        setError('Geçerli bir resim dosyası seçin (JPEG, PNG, GIF, BMP, WebP).');
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
      setError('Lütfen bir resim seçin.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedImage);
      formData.append('language', language);
      formData.append('product_name', productName);
      formData.append('brand', brand);

      const response = await callApi('/api/analysis/analyze', {
        method: 'POST',
        body: formData,
      });

      if (response.success) {
        setAnalysisResult(response);
      } else {
        setError(response.error || 'Analiz sırasında hata oluştu.');
      }
    } catch (err) {
      setError('Bağlantı hatası. Lütfen tekrar deneyin.');
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
    setProductName('');
    setBrand('');
    setShowOCRDetails(false);
    
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  const renderNutriScoreCard = () => {
    if (!analysisResult?.nutri_score) return null;

    const { nutri_score, recommendations } = analysisResult;
    const currentLang = language === 'tr' ? 'tr' : 'en';

    return (
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-800">
            {language === 'tr' ? 'Nutri-Score Analizi' : 'Nutri-Score Analysis'}
          </h3>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">
              {language === 'tr' ? 'Puan:' : 'Score:'}
            </span>
            <span className="font-bold text-lg">{nutri_score.score}</span>
          </div>
        </div>

        <NutriScoreDisplay
          grade={nutri_score.grade}
          score={nutri_score.score}
          color={nutri_score.color}
          size="large"
        />

        <div className="grid grid-cols-2 gap-4 mt-6">
          <div className="bg-red-50 p-4 rounded-lg">
            <h4 className="font-semibold text-red-800 mb-2">
              {language === 'tr' ? 'Olumsuz Puanlar' : 'Negative Points'}
            </h4>
            <p className="text-2xl font-bold text-red-600">{nutri_score.negative_points}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-semibold text-green-800 mb-2">
              {language === 'tr' ? 'Olumlu Puanlar' : 'Positive Points'}
            </h4>
            <p className="text-2xl font-bold text-green-600">{nutri_score.positive_points}</p>
          </div>
        </div>

        {/* Nutrition Breakdown */}
        <div className="mt-6">
          <h4 className="font-semibold text-gray-800 mb-3">
            {language === 'tr' ? 'Besin Değerleri (100g başına)' : 'Nutritional Values (per 100g)'}
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-gray-50 p-3 rounded">
              <div className="text-sm text-gray-600">
                {language === 'tr' ? 'Enerji' : 'Energy'}
              </div>
              <div className="font-semibold">
                {nutri_score.nutrition_breakdown.energy_kj} kJ
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <div className="text-sm text-gray-600">
                {language === 'tr' ? 'Yağ' : 'Fat'}
              </div>
              <div className="font-semibold">
                {nutri_score.nutrition_breakdown.fat}g
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <div className="text-sm text-gray-600">
                {language === 'tr' ? 'Şeker' : 'Sugars'}
              </div>
              <div className="font-semibold">
                {nutri_score.nutrition_breakdown.sugars}g
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <div className="text-sm text-gray-600">
                {language === 'tr' ? 'Protein' : 'Protein'}
              </div>
              <div className="font-semibold">
                {nutri_score.nutrition_breakdown.proteins}g
              </div>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        {recommendations && recommendations[currentLang] && (
          <div className="mt-6 bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-2">
              {language === 'tr' ? 'Öneriler' : 'Recommendations'}
            </h4>
            <ul className="space-y-2">
              {recommendations[currentLang].map((rec, index) => (
                <li key={index} className="text-blue-700 text-sm">
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {language === 'tr' ? 'Ürün Analizi' : 'Product Analysis'}
          </h2>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="tr">Türkçe</option>
            <option value="en">English</option>
          </select>
        </div>

        {/* Image Upload Section */}
        <div className="mb-6">
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden"
            />
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleCameraCapture}
              className="hidden"
            />
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center justify-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Upload size={20} />
              <span>{language === 'tr' ? 'Dosya Seç' : 'Choose File'}</span>
            </button>
            
            <button
              onClick={() => cameraInputRef.current?.click()}
              className="flex items-center justify-center space-x-2 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
            >
              <Camera size={20} />
              <span>{language === 'tr' ? 'Kamera' : 'Camera'}</span>
            </button>
          </div>

          {/* Product Info Inputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <input
              type="text"
              placeholder={language === 'tr' ? 'Ürün adı (opsiyonel)' : 'Product name (optional)'}
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder={language === 'tr' ? 'Marka (opsiyonel)' : 'Brand (optional)'}
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Preview */}
          {previewUrl && (
            <div className="relative inline-block">
              <img
                src={previewUrl}
                alt="Preview"
                className="max-w-full h-auto max-h-64 rounded-lg shadow-md"
              />
              <button
                onClick={resetAnalysis}
                className="absolute top-2 right-2 bg-red-600 text-white rounded-full p-2 hover:bg-red-700 transition-colors"
              >
                <X size={16} />
              </button>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
            <AlertCircle className="text-red-600" size={20} />
            <span className="text-red-800">{error}</span>
          </div>
        )}

        {/* Analyze Button */}
        <button
          onClick={analyzeProduct}
          disabled={!selectedImage || isAnalyzing}
          className={`w-full flex items-center justify-center space-x-2 px-6 py-3 rounded-lg font-semibold transition-colors ${
            !selectedImage || isAnalyzing
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              <span>{language === 'tr' ? 'Analiz Ediliyor...' : 'Analyzing...'}</span>
            </>
          ) : (
            <>
              <CheckCircle size={20} />
              <span>{language === 'tr' ? 'Analiz Et' : 'Analyze'}</span>
            </>
          )}
        </button>
      </div>

      {/* Analysis Results */}
      {isAnalyzing && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <LoadingSpinner message={language === 'tr' ? 'Ürün analiz ediliyor...' : 'Analyzing product...'} />
        </div>
      )}

      {analysisResult && (
        <div className="space-y-6">
          {renderNutriScoreCard()}
        </div>
      )}
    </div>
  );
};

export default ProductAnalysis;
=======
/**
 * Component for displaying product analysis results and nutritional information
 */
>>>>>>> fdd3cedf94404767e3a5728d43eb0c330c6b1ff6
