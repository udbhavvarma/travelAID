import React, { useState } from "react";
import { CITY_OPTIONS } from "../constants";

const TouristSpotsForm = ({ setTouristSpotsParams }) => {
  const [city, setCity] = useState("");
  const [type, setType] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [locality, setLocality] = useState("");
  const [categories, setCategories] = useState("");

  const handleSubmit = () => {
    setTouristSpotsParams({
      type,
      city,
      cuisine: cuisine || undefined,
      locality: locality || undefined,
      categories: categories ? categories.split(",").map((cat) => cat.trim()) : undefined,
    });
  };

  return (
    <div className="form-section">
      <h3>Tourist Spots / Restaurants</h3>
      <label>City</label>
      <select value={city} onChange={(e) => setCity(e.target.value)}>
        <option value="">Select</option>
        {CITY_OPTIONS.map((city) => (
          <option key={city} value={city}>
            {city}
          </option>
        ))}
      </select>
      <label>Type</label>
      <select value={type} onChange={(e) => setType(e.target.value)}>
        <option value="">Select</option>
        <option value="restaurant">Restaurant</option>
        <option value="tourist_attraction">Tourist Attraction</option>
      </select>
      <label>Cuisine</label>
      <input
        type="text"
        placeholder="Cuisine"
        value={cuisine}
        onChange={(e) => setCuisine(e.target.value)}
      />
      <label>Locality</label>
      <input
        type="text"
        placeholder="Locality"
        value={locality}
        onChange={(e) => setLocality(e.target.value)}
      />
      <label>Categories</label>
      <input
        type="text"
        placeholder="Categories"
        value={categories}
        onChange={(e) => setCategories(e.target.value)}
      />
      <button onClick={handleSubmit}>Set Tourist Spots</button>
    </div>
  );
};

export default TouristSpotsForm;
