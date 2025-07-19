/**
 * User Profile Setup Component
 * Based on the UI mockup showing user onboarding form
 */

import React, { useState, useEffect } from 'react';
import { userAPI } from '../services/api';
import toast from 'react-hot-toast';
import './ProfileSetupForm.css';

const ProfileSetupForm = ({ onComplete }) => {
  const [formData, setFormData] = useState({
    height: '', // Length field from mockup
    weight: '', // Weight field from mockup
    age: '',    // Age field from mockup
    allergies: [], // Allergies dropdown from mockup
    kvkk_approval: false, // "I approve KVKK" checkbox from mockup
    gender: '',
    activity_level: 'moderate'
  });

  const [availableAllergens, setAvailableAllergens] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // Load available allergens
  useEffect(() => {
    const loadAllergens = async () => {
      try {
        const response = await userAPI.getAvailableAllergens();
        if (response.success) {
          setAvailableAllergens(response.allergens);
        }
      } catch (error) {
        console.error('Failed to load allergens:', error);
      }
    };
    
    loadAllergens();
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleAllergenChange = (e) => {
    const allergenId = parseInt(e.target.value);
    if (allergenId && !formData.allergies.includes(allergenId)) {
      setFormData(prev => ({
        ...prev,
        allergies: [...prev.allergies, allergenId]
      }));
    }
  };

  const removeAllergen = (allergenId) => {
    setFormData(prev => ({
      ...prev,
      allergies: prev.allergies.filter(id => id !== allergenId)
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    // Height validation (Length field)
    if (!formData.height) {
      newErrors.height = 'Height is required';
    } else if (formData.height < 50 || formData.height > 300) {
      newErrors.height = 'Height must be between 50-300 cm';
    }

    // Weight validation
    if (!formData.weight) {
      newErrors.weight = 'Weight is required';
    } else if (formData.weight < 20 || formData.weight > 500) {
      newErrors.weight = 'Weight must be between 20-500 kg';
    }

    // Age validation
    if (!formData.age) {
      newErrors.age = 'Age is required';
    } else if (formData.age < 13 || formData.age > 120) {
      newErrors.age = 'Age must be between 13-120 years';
    }

    // KVKK approval validation (required by law)
    if (!formData.kvkk_approval) {
      newErrors.kvkk_approval = 'KVKK approval is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the errors in the form');
      return;
    }

    setLoading(true);

    try {
      // Setup profile
      const profileData = {
        height: parseFloat(formData.height),
        weight: parseFloat(formData.weight),
        age: parseInt(formData.age),
        gender: formData.gender,
        activity_level: formData.activity_level,
        kvkk_approval: formData.kvkk_approval
      };

      const profileResponse = await userAPI.setupProfile(profileData);

      if (profileResponse.success) {
        // Add allergens if any selected
        for (const allergenId of formData.allergies) {
          try {
            await userAPI.addAllergen({
              allergen_id: allergenId,
              severity: 'moderate'
            });
          } catch (error) {
            console.warn('Failed to add allergen:', error);
          }
        }

        toast.success('Profile setup completed successfully!');
        
        if (onComplete) {
          onComplete(profileResponse.profile);
        }
      } else {
        toast.error(profileResponse.error || 'Failed to setup profile');
      }
    } catch (error) {
      console.error('Profile setup error:', error);
      toast.error('An error occurred during profile setup');
    } finally {
      setLoading(false);
    }
  };

  const getSelectedAllergenNames = () => {
    return formData.allergies.map(id => {
      const allergen = availableAllergens.find(a => a.id === id);
      return allergen ? allergen.name : '';
    }).filter(Boolean);
  };

  return (
    <div className="profile-setup-container">
      <div className="profile-setup-header">
        <div className="foodlens-logo">
          <span className="logo-text">FoodLens</span>
        </div>
        <div className="dark-mode-toggle">
          <span>Dark Mode</span>
        </div>
      </div>

      <div className="profile-setup-content">
        <h1 className="setup-title">Let's get to know you better!</h1>

        <form onSubmit={handleSubmit} className="profile-setup-form">
          {/* Height Field (Length in mockup) */}
          <div className="form-group">
            <label htmlFor="height">Length (Height in cm)</label>
            <input
              type="number"
              id="height"
              name="height"
              value={formData.height}
              onChange={handleInputChange}
              placeholder="Enter your height in cm"
              className={errors.height ? 'error' : ''}
            />
            {errors.height && <span className="error-message">{errors.height}</span>}
          </div>

          {/* Weight Field */}
          <div className="form-group">
            <label htmlFor="weight">Weight (kg)</label>
            <input
              type="number"
              id="weight"
              name="weight"
              value={formData.weight}
              onChange={handleInputChange}
              placeholder="Enter your weight in kg"
              className={errors.weight ? 'error' : ''}
            />
            {errors.weight && <span className="error-message">{errors.weight}</span>}
          </div>

          {/* Age Field */}
          <div className="form-group">
            <label htmlFor="age">Age</label>
            <input
              type="number"
              id="age"
              name="age"
              value={formData.age}
              onChange={handleInputChange}
              placeholder="Enter your age"
              className={errors.age ? 'error' : ''}
            />
            {errors.age && <span className="error-message">{errors.age}</span>}
          </div>

          {/* Gender Field */}
          <div className="form-group">
            <label htmlFor="gender">Gender</label>
            <select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleInputChange}
            >
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
              <option value="prefer_not_to_say">Prefer not to say</option>
            </select>
          </div>

          {/* Activity Level */}
          <div className="form-group">
            <label htmlFor="activity_level">Activity Level</label>
            <select
              id="activity_level"
              name="activity_level"
              value={formData.activity_level}
              onChange={handleInputChange}
            >
              <option value="sedentary">Sedentary</option>
              <option value="light">Light Activity</option>
              <option value="moderate">Moderate Activity</option>
              <option value="active">Active</option>
              <option value="very_active">Very Active</option>
            </select>
          </div>

          {/* Allergies Dropdown (as shown in mockup) */}
          <div className="form-group">
            <label htmlFor="allergies">Allergies</label>
            <select
              id="allergies"
              onChange={handleAllergenChange}
              defaultValue=""
            >
              <option value="">Select an allergy to add</option>
              {availableAllergens.map(allergen => (
                <option 
                  key={allergen.id} 
                  value={allergen.id}
                  disabled={formData.allergies.includes(allergen.id)}
                >
                  {allergen.name}
                </option>
              ))}
            </select>
            
            {/* Selected Allergies Display */}
            {formData.allergies.length > 0 && (
              <div className="selected-allergies">
                <p>Selected allergies:</p>
                <div className="allergen-tags">
                  {getSelectedAllergenNames().map(name => (
                    <span key={name} className="allergen-tag">
                      {name}
                      <button
                        type="button"
                        onClick={() => {
                          const allergenId = availableAllergens.find(a => a.name === name)?.id;
                          if (allergenId) removeAllergen(allergenId);
                        }}
                        className="remove-allergen"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* KVKK Approval Checkbox (as shown in mockup) */}
          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="kvkk_approval"
                checked={formData.kvkk_approval}
                onChange={handleInputChange}
                className={errors.kvkk_approval ? 'error' : ''}
              />
              <span className="checkmark"></span>
              I approve KVKK
            </label>
            {errors.kvkk_approval && (
              <span className="error-message">{errors.kvkk_approval}</span>
            )}
          </div>

          {/* Submit Button */}
          <button 
            type="submit" 
            className="submit-button"
            disabled={loading}
          >
            {loading ? 'Setting up...' : 'Done'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ProfileSetupForm;
