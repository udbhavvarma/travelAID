import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import FlightsForm from "./components/FlightsForm";
import HotelsForm from "./components/HotelsForm";
import TouristSpotsForm from "./components/TouristSpotsForm";
import ResultsDisplay from "./components/ResultsDisplay";
import { fetchHardcodedQuery } from "./api/backend";
import "./App.css";

const App = () => {
  const [results, setResults] = useState(null);
  const [flightsParams, setFlightsParams] = useState({});
  const [hotelsParams, setHotelsParams] = useState({});
  const [touristSpotsParams, setTouristSpotsParams] = useState({});

  const handleHardcodedSearch = async () => {
    const hardcodedQuery = {
      flights: flightsParams || {}, // Send empty object if no flights parameters
      hotels: hotelsParams || {},  // Send empty object if no hotels parameters
      tourist_spots: touristSpotsParams || {}, // Send empty object if no tourist spots parameters
    };
    
    const results = await fetchHardcodedQuery(hardcodedQuery);
    console.log(results);
    setResults(results);
  };

  return (
    <div className="app-container">
      <div className="top-section">
        <div className="app-name">
          <style>
              @import url('https://fonts.googleapis.com/css2?family=Faustina:ital,wght@0,300..800;1,300..800&display=swap');
          </style>
          <h1>travelAID</h1>
        </div> 
      </div>

      <div className="mid-section>">
        <SearchBar setResults={setResults} />
        {/* <FlightsForm setFlightsParams={setFlightsParams} />
        <HotelsForm setHotelsParams={setHotelsParams} />
        <TouristSpotsForm setTouristSpotsParams={setTouristSpotsParams} />
        <button className="blue-button" onClick={handleHardcodedSearch}>Search with Parameters</button> */}
        {/* </div> */}
        {/* <div className="right-column"> */}
      </div>
      <div className="bottom-section">
      <ResultsDisplay results={results} />
      </div>
    </div>
    // </div>
  );
};

export default App;
