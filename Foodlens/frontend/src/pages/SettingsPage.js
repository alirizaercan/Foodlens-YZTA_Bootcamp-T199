import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Save, Eye, EyeOff, User, Shield, Bell, Trash2, Plus, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { userService } from '../services/api';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/SettingsPage.css';

const SettingsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, updateUser, changePassword } = useAuth();

  // Get language from URL params
  const [language, setLanguage] = useState(() => {
    const urlParams = new URLSearchParams(location.search);
    return urlParams.get('lang') || 'tr';
  });

  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState({
    current: false,
    new: false,
    confirm: false
  });

  // Profile form data
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    height: '',
    weight: '',
    age: '',
    gender: '',
    activity_level: ''
  });

  // Password form data
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: ''
  });

  // Allergen data
  const [userAllergens, setUserAllergens] = useState([]);
  const [availableAllergens, setAvailableAllergens] = useState([]);
  const [selectedAllergen, setSelectedAllergen] = useState('');

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (user) {
      loadUserData();
      loadAllergens();
    }
  }, [user]);

  // Update language when URL changes
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const urlLang = urlParams.get('lang');
    if (urlLang && urlLang !== language) {
      setLanguage(urlLang);
    }
  }, [location.search, language]);

  const loadUserData = async () => {
    try {
      const response = await userService.getUserProfile();
      console.log('User profile response:', response);
      
      if (response.success) {
        const userData = response.user;
        const profileData = response.profile || {};
        
        setProfileForm({
          first_name: userData.first_name || '',
          last_name: userData.last_name || '',
          username: userData.username || '',
          height: profileData.height || '',
          weight: profileData.weight || '',
          age: profileData.age || '',
          gender: profileData.gender || '',
          activity_level: profileData.activity_level || ''
        });
      } else if (response.status === 401) {
        console.error('Authentication failed - redirecting to login');
        toast.error(language === 'tr' ? 'Oturum süreniz doldu. Lütfen tekrar giriş yapın.' : 'Session expired. Please login again.');
        navigate('/auth');
        return;
      } else {
        console.error('Failed to load user profile:', response);
        toast.error(language === 'tr' ? 'Kullanıcı verileri yüklenemedi' : 'Failed to load user data');
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
      toast.error(language === 'tr' ? 'Kullanıcı verileri yüklenemedi' : 'Failed to load user data');
    }
  };

  const loadAllergens = async () => {
    try {
      const [userAllergensResponse, availableAllergensResponse] = await Promise.all([
        userService.getUserAllergens(),
        userService.getAvailableAllergens()
      ]);

      console.log('User allergens response:', userAllergensResponse);
      console.log('Available allergens response:', availableAllergensResponse);

      if (userAllergensResponse.success) {
        setUserAllergens(userAllergensResponse.allergens || []);
      } else if (userAllergensResponse.status === 401) {
        console.error('Authentication failed - redirecting to login');
        toast.error(language === 'tr' ? 'Oturum süreniz doldu. Lütfen tekrar giriş yapın.' : 'Session expired. Please login again.');
        navigate('/auth');
        return;
      } else {
        console.error('Failed to load user allergens:', userAllergensResponse);
        setUserAllergens([]);
      }

      if (availableAllergensResponse.success) {
        setAvailableAllergens(availableAllergensResponse.allergens || []);
      } else {
        console.error('Failed to load available allergens:', availableAllergensResponse);
        setAvailableAllergens([]);
        toast.error(language === 'tr' ? 'Alerjen verileri yüklenemedi' : 'Failed to load allergen data');
      }
    } catch (error) {
      console.error('Failed to load allergens:', error);
      setUserAllergens([]);
      setAvailableAllergens([]);
      toast.error(language === 'tr' ? 'Alerjen verileri yüklenemedi' : 'Failed to load allergen data');
    }
  };

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordForm(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateProfileForm = () => {
    const newErrors = {};
    
    if (!profileForm.username.trim()) {
      newErrors.username = language === 'tr' ? 'Kullanıcı adı gerekli' : 'Username is required';
    } else if (profileForm.username.length < 3) {
      newErrors.username = language === 'tr' ? 'Kullanıcı adı en az 3 karakter olmalı' : 'Username must be at least 3 characters';
    }

    if (profileForm.height && (isNaN(profileForm.height) || profileForm.height <= 0)) {
      newErrors.height = language === 'tr' ? 'Boy geçerli bir pozitif sayı olmalı' : 'Height must be a valid positive number';
    }

    if (profileForm.weight && (isNaN(profileForm.weight) || profileForm.weight <= 0)) {
      newErrors.weight = language === 'tr' ? 'Kilo geçerli bir pozitif sayı olmalı' : 'Weight must be a valid positive number';
    }

    if (profileForm.age && (isNaN(profileForm.age) || profileForm.age < 13 || profileForm.age > 120)) {
      newErrors.age = language === 'tr' ? 'Yaş 13 ile 120 arasında olmalı' : 'Age must be between 13 and 120';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validatePasswordForm = () => {
    const newErrors = {};
    
    if (!passwordForm.old_password) {
      newErrors.old_password = language === 'tr' ? 'Mevcut şifre gerekli' : 'Current password is required';
    }
    
    if (!passwordForm.new_password) {
      newErrors.new_password = language === 'tr' ? 'Yeni şifre gerekli' : 'New password is required';
    } else if (passwordForm.new_password.length < 6) {
      newErrors.new_password = language === 'tr' ? 'Yeni şifre en az 6 karakter olmalı' : 'New password must be at least 6 characters';
    }
    
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      newErrors.confirm_password = language === 'tr' ? 'Şifreler eşleşmiyor' : 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSaveProfile = async () => {
    if (!validateProfileForm()) return;
    
    setLoading(true);
    
    try {
      // Update basic user info first
      const basicInfoResult = await userService.updateUserBasicInfo({
        first_name: profileForm.first_name,
        last_name: profileForm.last_name,
        username: profileForm.username
      });

      console.log('Basic info update result:', basicInfoResult);

      if (!basicInfoResult.success) {
        toast.error(language === 'tr' 
          ? (basicInfoResult.error || 'Temel bilgiler güncellenemedi') 
          : (basicInfoResult.error || 'Failed to update basic information')
        );
        setLoading(false);
        return;
      }

      // Update profile info
      const profileData = {
        height: profileForm.height ? parseFloat(profileForm.height) : null,
        weight: profileForm.weight ? parseFloat(profileForm.weight) : null,
        age: profileForm.age ? parseInt(profileForm.age) : null,
        gender: profileForm.gender || null,
        activity_level: profileForm.activity_level || null
      };

      console.log('Updating profile with data:', profileData);
      const profileResult = await userService.updateUserProfile(profileData);
      console.log('Profile update result:', profileResult);

      if (profileResult.success) {
        toast.success(language === 'tr' ? 'Profil başarıyla güncellendi!' : 'Profile updated successfully!');
        // Reload user data to reflect changes
        await loadUserData();
      } else {
        toast.error(language === 'tr' 
          ? (profileResult.error || 'Profil güncellenemedi') 
          : (profileResult.error || 'Failed to update profile')
        );
      }
    } catch (error) {
      console.error('Profile update error:', error);
      toast.error(language === 'tr' 
        ? 'Profil güncellenirken bir hata oluştu' 
        : 'An error occurred while updating profile'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (!validatePasswordForm()) return;
    
    setLoading(true);
    
    try {
      const result = await changePassword({
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      });
      console.log('Password change result:', result);

      if (result.success) {
        toast.success(language === 'tr' ? 'Şifre başarıyla değiştirildi!' : 'Password changed successfully!');
        setPasswordForm({
          old_password: '',
          new_password: '',
          confirm_password: ''
        });
      } else {
        toast.error(language === 'tr' 
          ? (result.error || 'Şifre değiştirilemedi') 
          : (result.error || 'Failed to change password')
        );
      }
    } catch (error) {
      console.error('Password change error:', error);
      toast.error(language === 'tr' 
        ? 'Şifre değiştirilirken bir hata oluştu' 
        : 'An error occurred while changing password'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAddAllergen = async () => {
    if (!selectedAllergen) {
      toast.error(language === 'tr' ? 'Lütfen bir alerjen seçin' : 'Please select an allergen');
      return;
    }

    setLoading(true);

    try {
      const result = await userService.addAllergen({
        allergen_id: parseInt(selectedAllergen),
        severity: 'moderate'
      });

      if (result.success) {
        toast.success(language === 'tr' ? 'Alerjen başarıyla eklendi!' : 'Allergen added successfully!');
        setSelectedAllergen('');
        loadAllergens(); // Reload allergen data
      } else {
        toast.error(language === 'tr' 
          ? (result.error || 'Alerjen eklenemedi') 
          : (result.error || 'Failed to add allergen')
        );
      }
    } catch (error) {
      console.error('Add allergen error:', error);
      toast.error(language === 'tr' 
        ? 'Alerjen eklenirken bir hata oluştu' 
        : 'An error occurred while adding allergen'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAllergen = async (allergenId) => {
    setLoading(true);

    try {
      const result = await userService.removeAllergen(allergenId);

      if (result.success) {
        toast.success(language === 'tr' ? 'Alerjen başarıyla kaldırıldı!' : 'Allergen removed successfully!');
        loadAllergens(); // Reload allergen data
      } else {
        toast.error(language === 'tr' 
          ? (result.error || 'Alerjen kaldırılamadı') 
          : (result.error || 'Failed to remove allergen')
        );
      }
    } catch (error) {
      console.error('Remove allergen error:', error);
      toast.error(language === 'tr' 
        ? 'Alerjen kaldırılırken bir hata oluştu' 
        : 'An error occurred while removing allergen'
      );
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = (field) => {
    setShowPassword(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const availableAllergensToAdd = availableAllergens.filter(allergen => 
    !userAllergens.some(ua => ua.allergen_id === allergen.id)
  );

  return (
    <div className="settings-container">
      <div className="settings-modal">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="settings-close" onClick={() => navigate('/home')}>
            <X size={20} />
          </button>
        </div>

        <div className="settings-content">
          <div className="settings-tabs">
            <button
              className={`tab ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              <User size={20} />
              Profile
            </button>
            <button
              className={`tab ${activeTab === 'security' ? 'active' : ''}`}
              onClick={() => setActiveTab('security')}
            >
              <Shield size={20} />
              Security
            </button>
            <button
              className={`tab ${activeTab === 'allergens' ? 'active' : ''}`}
              onClick={() => setActiveTab('allergens')}
            >
              <Bell size={20} />
              Allergens
            </button>
          </div>

          <div className="settings-panel">
            {activeTab === 'profile' && (
              <div className="profile-settings">
                <h3>Profile Information</h3>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>First Name</label>
                    <input
                      type="text"
                      name="first_name"
                      value={profileForm.first_name}
                      onChange={handleProfileChange}
                      placeholder="First name"
                    />
                  </div>
                  <div className="form-group">
                    <label>Last Name</label>
                    <input
                      type="text"
                      name="last_name"
                      value={profileForm.last_name}
                      onChange={handleProfileChange}
                      placeholder="Last name"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    name="username"
                    value={profileForm.username}
                    onChange={handleProfileChange}
                    className={errors.username ? 'error' : ''}
                    placeholder="Username"
                  />
                  {errors.username && (
                    <span className="error-message">{errors.username}</span>
                  )}
                </div>

                <h3>Health Information</h3>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Height (cm)</label>
                    <input
                      type="number"
                      name="height"
                      value={profileForm.height}
                      onChange={handleProfileChange}
                      className={errors.height ? 'error' : ''}
                      placeholder="Height in cm"
                    />
                    {errors.height && (
                      <span className="error-message">{errors.height}</span>
                    )}
                  </div>
                  <div className="form-group">
                    <label>Weight (kg)</label>
                    <input
                      type="number"
                      name="weight"
                      value={profileForm.weight}
                      onChange={handleProfileChange}
                      className={errors.weight ? 'error' : ''}
                      placeholder="Weight in kg"
                    />
                    {errors.weight && (
                      <span className="error-message">{errors.weight}</span>
                    )}
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Age</label>
                    <input
                      type="number"
                      name="age"
                      value={profileForm.age}
                      onChange={handleProfileChange}
                      className={errors.age ? 'error' : ''}
                      placeholder="Age"
                    />
                    {errors.age && (
                      <span className="error-message">{errors.age}</span>
                    )}
                  </div>
                  <div className="form-group">
                    <label>Gender</label>
                    <select
                      name="gender"
                      value={profileForm.gender}
                      onChange={handleProfileChange}
                    >
                      <option value="">Select gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Activity Level</label>
                  <select
                    name="activity_level"
                    value={profileForm.activity_level}
                    onChange={handleProfileChange}
                  >
                    <option value="">Select activity level</option>
                    <option value="sedentary">Sedentary</option>
                    <option value="lightly_active">Lightly Active</option>
                    <option value="moderately_active">Moderately Active</option>
                    <option value="very_active">Very Active</option>
                    <option value="extremely_active">Extremely Active</option>
                  </select>
                </div>

                <button
                  onClick={handleSaveProfile}
                  disabled={loading}
                  className="settings-button primary"
                >
                  {loading ? <LoadingSpinner size="small" /> : <Save size={20} />}
                  Save Profile
                </button>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="security-settings">
                <h3>Change Password</h3>
                
                <div className="form-group">
                  <label>Current Password</label>
                  <div className="password-field">
                    <input
                      type={showPassword.current ? 'text' : 'password'}
                      name="old_password"
                      value={passwordForm.old_password}
                      onChange={handlePasswordChange}
                      className={errors.old_password ? 'error' : ''}
                      placeholder="Current password"
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => togglePasswordVisibility('current')}
                    >
                      {showPassword.current ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                  {errors.old_password && (
                    <span className="error-message">{errors.old_password}</span>
                  )}
                </div>

                <div className="form-group">
                  <label>New Password</label>
                  <div className="password-field">
                    <input
                      type={showPassword.new ? 'text' : 'password'}
                      name="new_password"
                      value={passwordForm.new_password}
                      onChange={handlePasswordChange}
                      className={errors.new_password ? 'error' : ''}
                      placeholder="New password"
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => togglePasswordVisibility('new')}
                    >
                      {showPassword.new ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                  {errors.new_password && (
                    <span className="error-message">{errors.new_password}</span>
                  )}
                </div>

                <div className="form-group">
                  <label>Confirm New Password</label>
                  <div className="password-field">
                    <input
                      type={showPassword.confirm ? 'text' : 'password'}
                      name="confirm_password"
                      value={passwordForm.confirm_password}
                      onChange={handlePasswordChange}
                      className={errors.confirm_password ? 'error' : ''}
                      placeholder="Confirm new password"
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => togglePasswordVisibility('confirm')}
                    >
                      {showPassword.confirm ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                  {errors.confirm_password && (
                    <span className="error-message">{errors.confirm_password}</span>
                  )}
                </div>

                <button
                  onClick={handleChangePassword}
                  disabled={loading}
                  className="settings-button primary"
                >
                  {loading ? <LoadingSpinner size="small" /> : <Shield size={20} />}
                  Change Password
                </button>
              </div>
            )}

            {activeTab === 'allergens' && (
              <div className="allergen-settings">
                <h3>Manage Allergens</h3>
                
                {availableAllergensToAdd.length > 0 && (
                  <div className="add-allergen">
                    <div className="form-group">
                      <label>Add New Allergen</label>
                      <div className="allergen-add-row">
                        <select
                          value={selectedAllergen}
                          onChange={(e) => setSelectedAllergen(e.target.value)}
                        >
                          <option value="">Select an allergen</option>
                          {availableAllergensToAdd.map(allergen => (
                            <option key={allergen.id} value={allergen.id}>
                              {allergen.name}
                            </option>
                          ))}
                        </select>
                        <button
                          onClick={handleAddAllergen}
                          disabled={loading || !selectedAllergen}
                          className="settings-button secondary"
                        >
                          {loading ? <LoadingSpinner size="small" /> : <Plus size={20} />}
                          Add
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                <div className="current-allergens">
                  <h4>Your Allergens</h4>
                  {userAllergens.length === 0 ? (
                    <p className="no-allergens">No allergens added yet.</p>
                  ) : (
                    <div className="allergen-list">
                      {userAllergens.map((userAllergen) => (
                        <div key={userAllergen.id} className="allergen-item">
                          <div className="allergen-info">
                            <span className="allergen-name">
                              {userAllergen.allergen_name}
                            </span>
                            <span className="allergen-severity">
                              Severity: {userAllergen.severity}
                            </span>
                          </div>
                          <button
                            onClick={() => handleRemoveAllergen(userAllergen.id)}
                            disabled={loading}
                            className="remove-allergen-button"
                            title="Remove allergen"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
