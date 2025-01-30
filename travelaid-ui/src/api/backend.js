const BACKEND_URL = "http://localhost:8000";
// const ALLOWED_FILTERS = {
//     flights: ["class", "price", "stops"],
//     hotels: ["wifi", "swimming_pool", "parking", "restaurant"],
//     tourist_spots: ["wheelchair_accessible", "live_music", "outdoor_seating"],
//   };
  

export const fetchFederatedSearch = async (query) => {
  try {
    const response = await fetch(`${BACKEND_URL}/federated_search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });
    return await response.json();
  } catch (error) {
    console.error("Error fetching federated search:", error);
    return null;
  }
};

export const fetchHardcodedQuery = async (hardcodedQuery) => {
  try {
    const response = await fetch(`${BACKEND_URL}/federated_search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ hardcoded_query: hardcodedQuery }),
    });
    return await response.json();
  } catch (error) {
    console.error("Error fetching hardcoded query:", error);
    return null;
  }
};
