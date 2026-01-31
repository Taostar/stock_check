/**
 * Fluctuation alerts component
 */

import React from 'react';
import { useFluctuations } from '../../hooks/useAgent';

const FluctuationAlerts = () => {
  const { data, isLoading, error } = useFluctuations();

  if (isLoading) {
    return (
      <div className="fluctuation-alerts loading">
        <h3>High Fluctuations</h3>
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fluctuation-alerts error">
        <h3>High Fluctuations</h3>
        <p className="error-message">Failed to load</p>
      </div>
    );
  }

  const fluctuations = data?.fluctuations || [];

  if (fluctuations.length === 0) {
    return (
      <div className="fluctuation-alerts empty">
        <h3>High Fluctuations</h3>
        <p className="no-data">No significant movements</p>
      </div>
    );
  }

  return (
    <div className="fluctuation-alerts">
      <div className="alerts-header">
        <h3>High Fluctuations</h3>
        <span className="alert-count">{fluctuations.length}</span>
      </div>

      <div className="alerts-list">
        {fluctuations.map((alert) => (
          <div
            key={alert.symbol}
            className={`alert-item ${alert.direction}`}
          >
            <div className="alert-main">
              <span className="symbol">{alert.symbol}</span>
              <span className={`change ${alert.direction === 'up' ? 'positive' : 'negative'}`}>
                {alert.direction === 'up' ? '+' : ''}
                {alert.change_percent?.toFixed(2)}%
                <span className="arrow">{alert.direction === 'up' ? ' ^' : ' v'}</span>
              </span>
            </div>
            <div className="alert-details">
              <span className="name">{alert.name}</span>
              {alert.current_price && (
                <span className="price">${alert.current_price.toFixed(2)}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FluctuationAlerts;
