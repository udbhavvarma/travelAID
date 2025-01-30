import React, { useState } from "react";
import { CITY_OPTIONS, FLIGHT_STOPS, FLIGHT_CLASSES } from "../constants";

const FlightsForm = ({ setFlightsParams }) => {
  const [departure, setDeparture] = useState("");
  const [arrival, setArrival] = useState("");
  const [date, setDate] = useState("");
  const [stops, setStops] = useState("");
  const [flightClass, setFlightClass] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  const startDate = new Date('2024-11-28'); 
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

  const handleSubmit = () => {
    setFlightsParams({
      type: "flights",
      departure,
      arrival,
      date,
      stops,
      class: flightClass,
      min_price: minPrice,
      max_price: maxPrice,
    });
  };

  return (
    <div className="form-section">
      <h3>Flights</h3>
      <label>Departure City</label>
      <select value={departure} onChange={(e) => setDeparture(e.target.value)}>
        <option value="">Select</option>
        {CITY_OPTIONS.map((city) => (
          <option key={city} value={city}>
            {city}
          </option>
        ))}
      </select>
      <label>Arrival City</label>
      <select value={arrival} onChange={(e) => setArrival(e.target.value)}>
        <option value="">Select</option>
        {CITY_OPTIONS.map((city) => (
          <option key={city} value={city}>
            {city}
          </option>
        ))}
      </select>
      <label>Travel Date</label>
      <input
            type="date"
            value={date}
            onChange={handleChange}
            disabled={selectedDate && (selectedDate < startDate || selectedDate > endDate)}
        />
      <label>Stops</label>
      <select value={stops} onChange={(e) => setStops(e.target.value)}>
        <option value="">Select</option>
        {FLIGHT_STOPS.map((stop) => (
          <option key={stop} value={stop}>
            {stop}
          </option>
        ))}
      </select>
      <label>Class</label>
      <select value={flightClass} onChange={(e) => setFlightClass(e.target.value)}>
        <option value="">Select</option>
        {FLIGHT_CLASSES.map((cls) => (
          <option key={cls} value={cls}>
            {cls}
          </option>
        ))}
      </select>
      <label>Price Range</label>
      <div>
        <input
          className="price-input"
          type="number"
          placeholder="Min Price"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
        />
        <input
          className="price-input"
          type="number"
          placeholder="Max Price"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />
      </div>
      <button onClick={handleSubmit}>Set Flights</button>
    </div>
  );
};

export default FlightsForm;
