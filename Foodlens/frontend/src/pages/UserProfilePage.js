import React, { useState } from "react";

const allergiesList = [
  "Gluten",
  "Laktoz",
  "Yer fıstığı",
  "Deniz ürünleri",
  "Yumurta",
  "Soya",
  "Diğer"
];

export default function UserProfilePage() {
  const [form, setForm] = useState({
    boy: "",
    kilo: "",
    yas: "",
    cinsiyet: "",
    alerjiler: [],
    kvkk: false,
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === "checkbox") {
      setForm({ ...form, [name]: checked });
    } else if (name === "alerjiler") {
      const options = Array.from(e.target.selectedOptions, (option) => option.value);
      setForm({ ...form, alerjiler: options });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch("/api/user-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (response.ok) {
        alert("Bilgiler başarıyla kaydedildi!");
      } else {
        alert("Bir hata oluştu. Lütfen tekrar deneyin.");
      }
    } catch (err) {
      alert("Sunucuya bağlanılamadı.");
    }
    setLoading(false);
  };

  return (
    <div style={{
      maxWidth: 400,
      margin: "40px auto",
      padding: 24,
      borderRadius: 16,
      background: "#fff",
      boxShadow: "0 2px 12px #0001",
      fontFamily: "sans-serif"
    }}>
      <h2 style={{ textAlign: "center" }}>Sizi daha yakından tanıyalım!</h2>
      <form onSubmit={handleSubmit}>
        <label>Boy (cm)</label>
        <input
          type="number"
          name="boy"
          value={form.boy}
          onChange={handleChange}
          style={{ width: "100%", marginBottom: 12, padding: 8, background: "#e6e6fa", border: "1px solid #ccc", borderRadius: 6 }}
          placeholder="Boyunuzu giriniz"
          required
        />

        <label>Kilo (kg)</label>
        <input
          type="number"
          name="kilo"
          value={form.kilo}
          onChange={handleChange}
          style={{ width: "100%", marginBottom: 12, padding: 8, background: "#e6e6fa", border: "1px solid #ccc", borderRadius: 6 }}
          placeholder="Kilonuzu giriniz"
          required
        />

        <label>Alerjiler</label>
        <select
          name="alerjiler"
          multiple
          value={form.alerjiler}
          onChange={handleChange}
          style={{ width: "100%", marginBottom: 12, padding: 8, background: "#e6e6fa", border: "1px solid #ccc", borderRadius: 6 }}
        >
          {allergiesList.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>

        <label>Yaş</label>
        <input
          type="number"
          name="yas"
          value={form.yas}
          onChange={handleChange}
          style={{ width: "100%", marginBottom: 12, padding: 8, background: "#e6e6fa", border: "1px solid #ccc", borderRadius: 6 }}
          placeholder="Yaşınızı giriniz"
          required
        />

        <label>Cinsiyet</label>
        <div style={{ marginBottom: 12 }}>
          <label>
            <input
              type="radio"
              name="cinsiyet"
              value="erkek"
              checked={form.cinsiyet === "erkek"}
              onChange={handleChange}
              style={{ marginRight: 6 }}
            />
            Erkek
          </label>
          <label style={{ marginLeft: 16 }}>
            <input
              type="radio"
              name="cinsiyet"
              value="kadın"
              checked={form.cinsiyet === "kadın"}
              onChange={handleChange}
              style={{ marginRight: 6 }}
            />
            Kadın
          </label>
        </div>

        <label>
          <input
            type="checkbox"
            name="kvkk"
            checked={form.kvkk}
            onChange={handleChange}
            style={{ marginRight: 8 }}
            required
          />
          KVKK'yı onaylıyorum
        </label>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            marginTop: 24,
            padding: 12,
            background: "#2563eb",
            color: "#fff",
            fontSize: 20,
            border: "none",
            borderRadius: 12,
            cursor: loading ? "not-allowed" : "pointer"
          }}
        >
          {loading ? "Kaydediliyor..." : "Kaydet"}
        </button>
      </form>
    </div>
  );
}
