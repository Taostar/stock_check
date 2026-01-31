/**
 * Home page - original stock comparison functionality
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import StockChart from '../components/StockChart';

function HomePage() {
  const [data, setData] = useState([]);
  const [tickers, setTickers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async (selectedTickers) => {
    if (!selectedTickers || selectedTickers.length === 0) return;

    setLoading(true);
    setError(null);
    setTickers(selectedTickers);

    try {
      const response = await fetch('/api/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tickers: selectedTickers, period: "1mo" }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch data.');
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Stock Check & Compare</h1>
        <p>Real-time stock & ETF correlation analyzer</p>
        <nav className="main-nav">
          <Link to="/dashboard" className="nav-link">Go to AI Dashboard</Link>
        </nav>
      </header>

      <SearchBar onSearch={fetchData} />

      {loading && <div style={{ textAlign: 'center', marginTop: '2rem' }}>Loading...</div>}

      {error && <div style={{ textAlign: 'center', color: 'red', marginTop: '2rem' }}>{error}</div>}

      {!loading && !error && data.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <StockChart data={data} tickers={tickers} />
        </div>
      )}
    </div>
  );
}

export default HomePage;
