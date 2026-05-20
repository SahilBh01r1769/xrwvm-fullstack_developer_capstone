import React, { useState, useEffect } from 'react';
import "./Dealers.css";
import "../assets/style.css";
import Header from '../Header/Header';
import review_icon from "../assets/reviewicon.png";

const Dealers = () => {
  const [dealersList, setDealersList] = useState([]);
  const [states, setStates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isLoggedIn = !!sessionStorage.getItem("username");

  // Fetch all dealers
  const get_dealers = async () => {
    try {
      setLoading(true);
      setError(null);

      const res = await fetch("/djangoapp/get_dealers", {
        method: "GET",
      });

      const retobj = await res.json();

      if (retobj.status === 200) {
        const allDealers = retobj.dealers || [];
        
        // Extract unique states
        const uniqueStates = [...new Set(allDealers.map(dealer => dealer.state))].sort();
        
        setDealersList(allDealers);
        setStates(uniqueStates);
      } else {
        setError("Failed to fetch dealers");
      }
    } catch (err) {
      console.error("Error fetching dealers:", err);
      setError("Unable to load dealers. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  // Filter dealers by state
 // Filter dealers by state
const filterDealers = async (selectedState) => {
    if (!selectedState || selectedState === "All") {
      get_dealers();
      return;
    }
  
    try {
      setLoading(true);
      setError(null);
  
      console.log(`Filtering by state: ${selectedState}`);   // ← Debug
  
      const res = await fetch(`/djangoapp/get_dealers/${selectedState}`, {
        method: "GET",
      });
  
      const retobj = await res.json();
      console.log("Filter response:", retobj);   // ← Debug
  
      if (retobj.status === 200) {
        setDealersList(retobj.dealers || []);
      } else {
        setError(retobj.message || "Failed to filter dealers");
      }
    } catch (err) {
      console.error("Error filtering dealers:", err);
      setError("Failed to filter dealers");
    } finally {
      setLoading(false);
    }
  };
  
  // Initial load
  useEffect(() => {
    get_dealers();
  }, []);

  if (loading && dealersList.length === 0) {
    return (
      <div>
        <Header />
        <div className="loading">Loading dealers...</div>
      </div>
    );
  }

  return (
    <div>
      <Header />

      {error && <div className="error-message">{error}</div>}

      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Dealer Name</th>
            <th>City</th>
            <th>Address</th>
            <th>Zip</th>
            <th>
              <select 
                name="state" 
                id="state" 
                onChange={(e) => filterDealers(e.target.value)}
                defaultValue=""
              >
                <option value="" disabled hidden>Select State</option>
                <option value="All">All States</option>
                {states.map(state => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </th>
            {isLoggedIn && <th>Review Dealer</th>}
          </tr>
        </thead>
        <tbody>
          {dealersList.map(dealer => (
            <tr key={dealer.id}>
              <td>{dealer.id}</td>
              <td>
                <a href={`/dealer/${dealer.id}`}>{dealer.full_name}</a>
              </td>
              <td>{dealer.city}</td>
              <td>{dealer.address}</td>
              <td>{dealer.zip}</td>
              <td>{dealer.state}</td>
              {isLoggedIn && (
                <td>
                  <a href={`/postreview/${dealer.id}`}>
                    <img 
                      src={review_icon} 
                      className="review_icon" 
                      alt="Post Review" 
                    />
                  </a>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {!loading && dealersList.length === 0 && (
        <p>No dealers found.</p>
      )}
    </div>
  );
};

export default Dealers;