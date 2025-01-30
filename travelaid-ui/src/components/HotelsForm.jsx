import React, { useState } from "react";
import { CITY_OPTIONS, HOTEL_AMENITIES } from "../constants";

const HotelsForm = ({ setHotelsParams }) => {
  const [city, setCity] = useState("");
  const [siteReviewRating, setSiteReviewRating] = useState("");
  const [date, setDate] = useState("");
  const [amenities, setAmenities] = useState({});

  const handleCheckboxChange = (e) => {
    setAmenities({ ...amenities, [e.target.name]: e.target.checked });
  };

  const handleSubmit = () => {
    setHotelsParams({
      type: "hotels",
      city,
      date,
      site_review_rating: siteReviewRating,
      amenities,
    });
  };

  const startDate = new Date('2024-11-28'); // Replace with your desired start date
  const endDate = new Date('2025-01-31');
  const selectedDate = useState(null);

  const handleChange = (e) => {
    const selectedDate = new Date(e.target.value);
    if (selectedDate >= startDate && selectedDate <= endDate) {
      setDate(e.target.value);
    } else {
      // Handle invalid date selection (optional)
      console.warn('Date outside allowed range');
    }
  };


  return (
    <div className="form-section">
      <h3>Hotels</h3>
      <label>City</label>
      <select value={city} onChange={(e) => setCity(e.target.value)}>
        <option value="">Select</option>
        {CITY_OPTIONS.map((city) => (
          <option key={city} value={city}>
            {city}
          </option>
        ))}
      </select>

      <label>Date</label>
      <input
            type="date"
            value={date}
            onChange={handleChange}
            disabled={selectedDate && (selectedDate < startDate || selectedDate > endDate)}
        />

      <label>Site Review Rating</label>
      <input
        type="number"
        placeholder="Rating"
        value={siteReviewRating}
        onChange={(e) => setSiteReviewRating(e.target.value)}
      />
      <label>Amenities</label>
      {HOTEL_AMENITIES.map((amenity) => (
        <div key={amenity} className="amenities">
          <input
            className="amenity-checkbox"
            type="checkbox"
            name={amenity}
            checked={!!amenities[amenity]}
            onChange={handleCheckboxChange}
          />
          <label>{amenity.replace("_", " ")}</label>
        </div>
      ))}
      <button onClick={handleSubmit}>Set Hotels</button>
    </div>
  );
};

export default HotelsForm;
