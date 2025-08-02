import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { userService } from "../services/api";
import { toast } from "react-hot-toast";
import LoadingSpinner from "../components/LoadingSpinner";

const allergiesList = [
  { id: 1, name: 'Gluten' },
  { id: 2, name: 'Laktoz' },
  { id: 3, name: 'Yer fıstığı' },
  { id: 4, name: 'Deniz ürünleri' },
  { id: 5, name: 'Yumurta' },
  { id: 6, name: 'Soya' },
  { id: 7, name: 'Diğer' }
];

export default function UserProfilePage({ onComplete, onSkip }) {
  const { user } = useAuth();
  const [form, setForm] = useState({
    height: "",
    weight: "",
    age: "",
    gender: "",
    activity_level: "",
    allergen_ids: [],
    kvkk_approval: false,
  });
  const [loading, setLoading] = useState(false);
  const [availableAllergens, setAvailableAllergens] = useState([]);

  useEffect(() => {
    loadAvailableAllergens();
  }, []);

  const loadAvailableAllergens = async () => {
    try {
      const response = await userService.getAvailableAllergens();
      if (response.success) {
        setAvailableAllergens(response.allergens);
      } else {
        // Fallback to hardcoded list
        setAvailableAllergens(allergiesList);
      }
    } catch (error) {
      console.error('Failed to load allergens:', error);
      setAvailableAllergens(allergiesList);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === "checkbox") {
      setForm({ ...form, [name]: checked });
    } else if (name === "allergen_ids") {
      const allergenId = parseInt(value);
      if (allergenId && !form.allergen_ids.includes(allergenId)) {
        setForm({ 
          ...form, 
          allergen_ids: [...form.allergen_ids, allergenId] 
        });
      }
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const removeAllergen = (allergenId) => {
    setForm({
      ...form,
      allergen_ids: form.allergen_ids.filter(id => id !== allergenId)
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!form.kvkk_approval) {
      toast.error('KVKK onayı gereklidir');
      return;
    }

    setLoading(true);
    
    try {
      // Setup user profile
      const profileData = {
        height: form.height ? parseFloat(form.height) : null,
        weight: form.weight ? parseFloat(form.weight) : null,
        age: form.age ? parseInt(form.age) : null,
        gender: form.gender,
        activity_level: form.activity_level,
        kvkk_approval: form.kvkk_approval
      };

      const profileResponse = await userService.setupUserProfile(profileData);
      
      if (profileResponse.success) {
        // Add selected allergens
        for (const allergenId of form.allergen_ids) {
          try {
            await userService.addAllergen({
              allergen_id: allergenId,
              severity: 'moderate'
            });
          } catch (error) {
            console.warn('Failed to add allergen:', error);
          }
        }

        toast.success('Profil başarıyla oluşturuldu!');
        
        if (onComplete) {
          onComplete(profileResponse.profile);
        }
      } else {
        toast.error(profileResponse.error || 'Profil oluşturulamadı');
      }
    } catch (error) {
      console.error('Profile setup error:', error);
      toast.error('Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const selectedAllergenNames = form.allergen_ids.map(id => {
    const allergen = availableAllergens.find(a => a.id === id);
    return allergen ? allergen.name : '';
  }).filter(Boolean);

  return (
    <div className="profile-setup-container">
      <div className="profile-setup-modal">
        <div className="profile-setup-header">
          <h2>Sizi daha iyi tanıyalım!</h2>
          <p>Kişiselleştirilmiş öneriler için bilgilerinizi giriniz</p>
        </div>

        <form onSubmit={handleSubmit} className="profile-setup-form">
          <div className="form-row">
            <div className="form-group">
              <label>Boy (cm)</label>
              <input
                type="number"
                name="height"
                value={form.height}
                onChange={handleChange}
                placeholder="Boyunuzu girin"
              />
            </div>
            <div className="form-group">
              <label>Kilo (kg)</label>
              <input
                type="number"
                name="weight"
                value={form.weight}
                onChange={handleChange}
                placeholder="Kilonuzu girin"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Yaş</label>
              <input
                type="number"
                name="age"
                value={form.age}
                onChange={handleChange}
                placeholder="Yaşınızı girin"
              />
            </div>
            <div className="form-group">
              <label>Cinsiyet</label>
              <select
                name="gender"
                value={form.gender}
                onChange={handleChange}
              >
                <option value="">Cinsiyet seçin</option>
                <option value="male">Erkek</option>
                <option value="female">Kadın</option>
                <option value="other">Diğer</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Aktivite Seviyesi</label>
            <select
              name="activity_level"
              value={form.activity_level}
              onChange={handleChange}
            >
              <option value="">Aktivite seviyesi seçin</option>
              <option value="sedentary">Hareketsiz</option>
              <option value="lightly_active">Az Hareketli</option>
              <option value="moderately_active">Orta Hareketli</option>
              <option value="very_active">Çok Hareketli</option>
              <option value="extremely_active">Aşırı Hareketli</option>
            </select>
          </div>

          <div className="form-group">
            <label>Alerjiler</label>
            <select
              name="allergen_ids"
              onChange={handleChange}
              value=""
            >
              <option value="">Alerji seçin</option>
              {availableAllergens
                .filter(allergen => !form.allergen_ids.includes(allergen.id))
                .map(allergen => (
                  <option key={allergen.id} value={allergen.id}>
                    {allergen.name}
                  </option>
                ))
              }
            </select>
            
            {selectedAllergenNames.length > 0 && (
              <div className="selected-allergens">
                <p>Seçilen alerjiler:</p>
                <div className="allergen-tags">
                  {form.allergen_ids.map(id => {
                    const allergen = availableAllergens.find(a => a.id === id);
                    return allergen ? (
                      <span key={id} className="allergen-tag">
                        {allergen.name}
                        <button 
                          type="button" 
                          onClick={() => removeAllergen(id)}
                          className="remove-tag"
                        >
                          ×
                        </button>
                      </span>
                    ) : null;
                  })}
                </div>
              </div>
            )}
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="kvkk_approval"
                checked={form.kvkk_approval}
                onChange={handleChange}
              />
              KVKK'yı onaylıyorum
            </label>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={onSkip}
              className="skip-button"
              disabled={loading}
            >
              Atla
            </button>
            <button
              type="submit"
              className="submit-button"
              disabled={loading || !form.kvkk_approval}
            >
              {loading ? <LoadingSpinner size="small" /> : 'Tamamla'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
