/**
 * Holdings table component with performance data
 */

import React from 'react';
import { useHoldingsPerformance } from '../../hooks/useAgent';

const HoldingsTable = () => {
  const { data, isLoading, error } = useHoldingsPerformance(true); // Use mock for now

  if (isLoading) {
    return (
      <div className="holdings-table loading">
        <h3>Holdings</h3>
        <p>Loading holdings...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="holdings-table error">
        <h3>Holdings</h3>
        <p className="error-message">Failed to load holdings: {error.message}</p>
      </div>
    );
  }

  const holdings = data?.holdings || [];

  if (holdings.length === 0) {
    return (
      <div className="holdings-table empty">
        <h3>Holdings</h3>
        <p className="no-data">No holdings data available.</p>
      </div>
    );
  }

  const formatCurrency = (value) => {
    if (value == null) return 'N/A';
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatPercent = (value) => {
    if (value == null) return 'N/A';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  return (
    <div className="holdings-table">
      <div className="table-header">
        <h3>Holdings</h3>
        <span className="holdings-count">{holdings.length} positions</span>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th>Shares</th>
              <th>Price</th>
              <th>Change</th>
              <th>Value</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((holding) => (
              <tr
                key={holding.symbol}
                className={holding.is_high_fluctuation ? 'high-fluctuation' : ''}
              >
                <td className="symbol">{holding.symbol}</td>
                <td className="name">{holding.name || '-'}</td>
                <td className="shares">{holding.shares}</td>
                <td className="price">{formatCurrency(holding.current_price)}</td>
                <td className={`change ${holding.change_percent >= 0 ? 'positive' : 'negative'}`}>
                  {formatPercent(holding.change_percent)}
                </td>
                <td className="value">{formatCurrency(holding.market_value)}</td>
                <td className="status">
                  {holding.is_high_fluctuation && (
                    <span className="alert-badge">Alert</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data?.total_value && (
        <div className="table-footer">
          <span>Total Value: {formatCurrency(data.total_value)}</span>
        </div>
      )}
    </div>
  );
};

export default HoldingsTable;
