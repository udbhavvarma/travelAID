import React, { useState } from "react";
import { fetchFederatedSearch } from "../api/backend";

const SearchBar = ({ setResults }) => {
  const [query, setQuery] = useState("");

  const handleSearch = async () => {
    const results = await fetchFederatedSearch(query);
    setResults(results);
  };

  return (
    <div className="search-bar">
    <input
        type="text"
        className="search-input"
        placeholder="Enter your query..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onkeypress="this.style.minWidth = ((this.value.length + 1) * 7) + 'px';"
    />
    <button onClick={handleSearch}>Search</button>
    </div>

  );
};

export default SearchBar;
