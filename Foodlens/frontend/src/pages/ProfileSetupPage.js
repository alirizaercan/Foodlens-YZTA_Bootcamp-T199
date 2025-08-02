import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { userService } from '../services/api';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/ProfileSetupPage.css';

const ProfileSetupPage = () => {
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [allergens, setAllergens] = useState([]);
  const [selectedAllergens, setSelectedAllergens] = useState([]);
  const [customAllergen, setCustomAllergen] = useState('');
  
  // Get language from URL params or default to 'tr'
  const [language, setLanguage] = useState(() => {
    const params = new URLSearchParams(location.search);
    return params.get('lang') || 'tr';
  });

  const [profileData, setProfileData] = useState({
    age: '',
    height: '',
    weight: '',
    gender: '',
    activity_level: '',
    dietary_preferences: '',
    health_goals: ''
  });

  // Predefined allergens list
  const commonAllergens = [
    { id: 1, name: 'Gluten', turkish_name: 'Gluten' },
    { id: 2, name: 'Dairy', turkish_name: 'Süt Ürünleri' },
    { id: 3, name: 'Eggs', turkish_name: 'Yumurta' },
    { id: 4, name: 'Nuts', turkish_name: 'Fındık/Fıstık' },
    { id: 5, name: 'Peanuts', turkish_name: 'Yer Fıstığı' },
    { id: 6, name: 'Shellfish', turkish_name: 'Kabuklu Deniz Ürünleri' },
    { id: 7, name: 'Fish', turkish_name: 'Balık' },
    { id: 8, name: 'Soy', turkish_name: 'Soya' },
    { id: 9, name: 'Sesame', turkish_name: 'Susam' },
    { id: 10, name: 'Sulfites', turkish_name: 'Sülfitler' }
  ];

  useEffect(() => {
    setAllergens(commonAllergens);
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAllergenToggle = (allergenId) => {
    setSelectedAllergens(prev => {
      if (prev.includes(allergenId)) {
        return prev.filter(id => id !== allergenId);
      } else {
        return [...prev, allergenId];
      }
    });
  };

  const handleAddCustomAllergen = () => {
    if (customAllergen.trim()) {
      const customId = Date.now(); // Temporary ID for custom allergen
      const newAllergen = {
        id: customId,
        name: customAllergen.trim(),
        turkish_name: customAllergen.trim(),
        is_custom: true
      };
      
      setAllergens(prev => [...prev, newAllergen]);
      setSelectedAllergens(prev => [...prev, customId]);
      setCustomAllergen('');
      toast.success('Özel alerjen eklendi');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Prepare profile data
      const profilePayload = {
        ...profileData,
        age: profileData.age ? parseInt(profileData.age) : null,
        height: profileData.height ? parseFloat(profileData.height) : null,
        weight: profileData.weight ? parseFloat(profileData.weight) : null
      };

      // Update user profile
      const profileResult = await userService.setupProfile(profilePayload);
      
      if (profileResult.success) {
        // Add selected allergens
        for (const allergenId of selectedAllergens) {
          const allergen = allergens.find(a => a.id === allergenId);
          if (allergen) {
            await userService.addAllergen({
              name: allergen.name,
              turkish_name: allergen.turkish_name,
              is_custom: allergen.is_custom || false
            });
          }
        }

        toast.success(language === 'tr' ? 'Profil bilgileri başarıyla kaydedildi!' : 'Profile information saved successfully!');
        navigate(`/home?lang=${language}`);
      } else {
        toast.error(profileResult.error || (language === 'tr' ? 'Profil güncellenirken hata oluştu' : 'Error occurred while updating profile'));
      }
    } catch (error) {
      console.error('Profile setup error:', error);
      toast.error(language === 'tr' ? 'Bir hata oluştu, lütfen tekrar deneyin' : 'An error occurred, please try again');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    navigate(`/home?lang=${language}`);
  };

  if (loading) {
    return (
      <div className="profile-setup-loading">
        <LoadingSpinner />
        <p>{language === 'tr' ? 'Profil bilgileri kaydediliyor...' : 'Saving profile information...'}</p>
      </div>
    );
  }

  return (
    <div className="profile-setup-page">
      <div className="profile-setup-container">
        <div className="profile-setup-header">
          <h1>{language === 'tr' ? 'Seni Daha İyi Tanıyalım!' : 'Let\'s Get to Know You Better!'}</h1>
          <p>
            {language === 'tr' 
              ? 'Kişiselleştirilmiş beslenme önerileri için profil bilgilerini tamamla' 
              : 'Complete your profile information for personalized nutrition recommendations'
            }
          </p>
        </div>

        <form onSubmit={handleSubmit} className="profile-setup-form">
          {/* Basic Information */}
          <div className="form-section">
            <h3>{language === 'tr' ? 'Temel Bilgiler' : 'Basic Information'}</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>{language === 'tr' ? 'Yaş' : 'Age'}</label>
                <input
                  type="number"
                  name="age"
                  value={profileData.age}
                  onChange={handleInputChange}
                  placeholder={language === 'tr' ? 'Yaşınızı girin' : 'Enter your age'}
                  min="13"
                  max="120"
                />
              </div>

              <div className="form-group">
                <label>{language === 'tr' ? 'Cinsiyet' : 'Gender'}</label>
                <select
                  name="gender"
                  value={profileData.gender}
                  onChange={handleInputChange}
                >
                  <option value="">{language === 'tr' ? 'Seçiniz' : 'Select'}</option>
                  <option value="male">{language === 'tr' ? 'Erkek' : 'Male'}</option>
                  <option value="female">{language === 'tr' ? 'Kadın' : 'Female'}</option>
                  <option value="other">{language === 'tr' ? 'Diğer' : 'Other'}</option>
                  <option value="prefer_not_to_say">{language === 'tr' ? 'Belirtmek İstemiyorum' : 'Prefer not to say'}</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>{language === 'tr' ? 'Boy (cm)' : 'Height (cm)'}</label>
                <input
                  type="number"
                  name="height"
                  value={profileData.height}
                  onChange={handleInputChange}
                  placeholder={language === 'tr' ? 'Boyunuzu cm cinsinden girin' : 'Enter your height in cm'}
                  min="50"
                  max="300"
                />
              </div>

              <div className="form-group">
                <label>{language === 'tr' ? 'Kilo (kg)' : 'Weight (kg)'}</label>
                <input
                  type="number"
                  name="weight"
                  value={profileData.weight}
                  onChange={handleInputChange}
                  placeholder={language === 'tr' ? 'Kilonuzu kg cinsinden girin' : 'Enter your weight in kg'}
                  min="20"
                  max="500"
                  step="0.1"
                />
              </div>
            </div>
          </div>

          {/* Activity Level */}
          <div className="form-section">
            <h3>{language === 'tr' ? 'Aktivite Seviyesi' : 'Activity Level'}</h3>
            <div className="activity-options">
              {[
                { 
                  value: 'sedentary', 
                  label: language === 'tr' ? 'Hareketsiz' : 'Sedentary', 
                  desc: language === 'tr' ? 'Çoğunlukla oturarak çalışıyorum' : 'Mostly sitting work' 
                },
                { 
                  value: 'light', 
                  label: language === 'tr' ? 'Az Aktif' : 'Lightly Active', 
                  desc: language === 'tr' ? 'Haftada 1-3 gün hafif egzersiz' : '1-3 days light exercise per week' 
                },
                { 
                  value: 'moderate', 
                  label: language === 'tr' ? 'Orta Aktif' : 'Moderately Active', 
                  desc: language === 'tr' ? 'Haftada 3-5 gün orta egzersiz' : '3-5 days moderate exercise per week' 
                },
                { 
                  value: 'active', 
                  label: language === 'tr' ? 'Aktif' : 'Active', 
                  desc: language === 'tr' ? 'Haftada 6-7 gün yoğun egzersiz' : '6-7 days intense exercise per week' 
                },
                { 
                  value: 'very_active', 
                  label: language === 'tr' ? 'Çok Aktif' : 'Very Active', 
                  desc: language === 'tr' ? 'Günde 2 kez egzersiz veya çok yoğun antrenman' : '2x daily exercise or very intense training' 
                }
              ].map((option) => (
                <label key={option.value} className="activity-option">
                  <input
                    type="radio"
                    name="activity_level"
                    value={option.value}
                    checked={profileData.activity_level === option.value}
                    onChange={handleInputChange}
                  />
                  <div className="activity-info">
                    <span className="activity-label">{option.label}</span>
                    <span className="activity-desc">{option.desc}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Health Goals */}
          <div className="form-section">
            <h3>{language === 'tr' ? 'Sağlık Hedefleri' : 'Health Goals'}</h3>
            <div className="health-goals">
              {[
                { 
                  value: 'lose_weight', 
                  label: language === 'tr' ? 'Kilo Vermek' : 'Lose Weight' 
                },
                { 
                  value: 'gain_weight', 
                  label: language === 'tr' ? 'Kilo Almak' : 'Gain Weight' 
                },
                { 
                  value: 'maintain_weight', 
                  label: language === 'tr' ? 'Kiloyu Korumak' : 'Maintain Weight' 
                },
                { 
                  value: 'build_muscle', 
                  label: language === 'tr' ? 'Kas Yapmak' : 'Build Muscle' 
                },
                { 
                  value: 'improve_health', 
                  label: language === 'tr' ? 'Sağlığı İyileştirmek' : 'Improve Health' 
                },
                { 
                  value: 'manage_condition', 
                  label: language === 'tr' ? 'Sağlık Durumunu Yönetmek' : 'Manage Health Condition' 
                }
              ].map((goal) => (
                <label key={goal.value} className="health-goal-option">
                  <input
                    type="radio"
                    name="health_goals"
                    value={goal.value}
                    checked={profileData.health_goals === goal.value}
                    onChange={handleInputChange}
                  />
                  <span>{goal.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Dietary Preferences */}
          <div className="form-section">
            <h3>{language === 'tr' ? 'Diyet Tercihleri' : 'Dietary Preferences'}</h3>
            <select
              name="dietary_preferences"
              value={profileData.dietary_preferences}
              onChange={handleInputChange}
              className="dietary-select"
            >
              <option value="">{language === 'tr' ? 'Seçiniz' : 'Select'}</option>
              <option value="omnivore">{language === 'tr' ? 'Karma Beslenme' : 'Omnivore'}</option>
              <option value="vegetarian">{language === 'tr' ? 'Vejetaryen' : 'Vegetarian'}</option>
              <option value="vegan">{language === 'tr' ? 'Vegan' : 'Vegan'}</option>
              <option value="pescatarian">{language === 'tr' ? 'Pesketaryen' : 'Pescatarian'}</option>
              <option value="keto">{language === 'tr' ? 'Ketojenik' : 'Ketogenic'}</option>
              <option value="paleo">{language === 'tr' ? 'Paleo' : 'Paleo'}</option>
              <option value="mediterranean">{language === 'tr' ? 'Akdeniz Diyeti' : 'Mediterranean'}</option>
              <option value="low_carb">{language === 'tr' ? 'Düşük Karbonhidrat' : 'Low Carb'}</option>
              <option value="gluten_free">{language === 'tr' ? 'Glutensiz' : 'Gluten Free'}</option>
            </select>
          </div>

          {/* Allergens */}
          <div className="form-section">
            <h3>{language === 'tr' ? 'Alerji ve Gıda İntoleransları' : 'Allergies and Food Intolerances'}</h3>
            <p className="section-desc">
              {language === 'tr' 
                ? 'Sahip olduğunuz alerji ve intoleransları seçin' 
                : 'Select your allergies and intolerances'
              }
            </p>
            
            <div className="allergens-grid">
              {allergens.map((allergen) => (
                <label key={allergen.id} className="allergen-option">
                  <input
                    type="checkbox"
                    checked={selectedAllergens.includes(allergen.id)}
                    onChange={() => handleAllergenToggle(allergen.id)}
                  />
                  <span className="allergen-name">
                    {language === 'tr' ? allergen.turkish_name : allergen.name}
                    {allergen.is_custom && (
                      <span className="custom-tag">
                        {language === 'tr' ? 'Özel' : 'Custom'}
                      </span>
                    )}
                  </span>
                </label>
              ))}
            </div>

            <div className="custom-allergen">
              <div className="custom-allergen-input">
                <input
                  type="text"
                  value={customAllergen}
                  onChange={(e) => setCustomAllergen(e.target.value)}
                  placeholder={language === 'tr' 
                    ? 'Listede olmayan bir alerji ekle...' 
                    : 'Add a custom allergen not in the list...'
                  }
                  maxLength="50"
                />
                <button
                  type="button"
                  onClick={handleAddCustomAllergen}
                  disabled={!customAllergen.trim()}
                  className="add-allergen-btn"
                >
                  {language === 'tr' ? 'Ekle' : 'Add'}
                </button>
              </div>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="form-actions">
            <button
              type="button"
              onClick={handleSkip}
              className="skip-btn"
            >
              {language === 'tr' ? 'Şimdilik Atla' : 'Skip for Now'}
            </button>
            <button
              type="submit"
              disabled={loading}
              className="submit-btn"
            >
              {loading 
                ? (language === 'tr' ? 'Kaydediliyor...' : 'Saving...') 
                : (language === 'tr' ? 'Profili Tamamla' : 'Complete Profile')
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileSetupPage;
