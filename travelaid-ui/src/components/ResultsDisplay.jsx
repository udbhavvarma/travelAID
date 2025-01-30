import React from "react";

const ResultsDisplay = ({ results }) => {


  if (!results) return <p>Enter a query for results.</p>;

  if (results.out_of_scope_response) {
    console.log(results.out_of_scope_response);
    return (
      <div className="out-of-scope-section">
        <h2>travelAID AI Assistant:</h2>
        <text>{results.out_of_scope_response}</text>
      </div>
    );
  }

  const truncateResults = (items, limit = 50) => {
    if (!items || !Array.isArray(items)) return [];
    return items.slice(0, limit);
  };

  const truncateFacilities = (facilities, limit = 7) => {
    if (!facilities || facilities.length <= limit) {
      return facilities.join(", ");
    }
    return facilities.slice(0, limit).join(", ") + ", ...";
  };

  const binaryToYesNo = (value) => (value ? "Yes" : "No");

  return (
    <div className="results-section">
      <h2>Results</h2>

      {/* Flights Section */}
      <div>
        <h3>Flights</h3>
        {results.flights && results.flights.length > 0 ? (
          <ul>
            {truncateResults(results.flights).map((flight, index) => (
              <li key={index}>
                <strong>{flight.airline}</strong> | {flight.flight_date} | {flight.departure} ➝ {flight.arrival} | {flight.duration} | {flight.class} | Stops: {flight.stops} | ₹{flight.price} | Site : <strong>{flight.sitename}</strong> 
              </li>
            ))}
          </ul>
        ) : (
          <p>No flights found.</p>
        )}
      </div>

      {/* Hotels Section */}
      <div>
        <h3>Hotels</h3>
        {results.hotels && results.hotels.length > 0 ? (
          <ul>
            {truncateResults(results.hotels).map((hotel, index) => (
              <li key={index}>
                <strong>{hotel.property_name}</strong> | {hotel.city} | {hotel.address} | Hotel Star Rating: {hotel.hotel_star_rating} | Rating: {hotel.site_review_rating} | ₹{hotel.price} | <strong>{hotel.sitename}</strong> |
            
              </li>
            ))}
          </ul>
        ) : (
          <p>No hotels found.</p>
        )}
      </div>

      {/* Tourist Spots Section */}
      <div>
        <h3>Tourist Spots / Restaurants</h3>
        {results.tourist_spots && results.tourist_spots.length > 0 ? (
          <ul>
            {truncateResults(results.tourist_spots).map((spot, index) => (
              <li key={index}>
                <strong>{spot.name}</strong> | {spot.type} | {spot.location.city} | Locality: {spot.location.locality} | Description: {spot.description} | Price Level: {spot.pricing.price_level} | Category: {spot.category}| Wheelchair Accessibility: {binaryToYesNo(spot.accessibility.wheelchair_accessible)} | Braille Menu: {binaryToYesNo(spot.accessibility.braille_menu)} | Site : <strong>{spot.site}</strong> 
              </li>
            ))}
          </ul>
        ) : (
          <p>No tourist spots found.</p>
        )}
      </div>
    </div>
  );
};

export default ResultsDisplay;
