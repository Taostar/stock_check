/**
 * Upcoming earnings calendar component
 */

import React from 'react';
import { useEarnings } from '../../hooks/useAgent';
import { format, parseISO } from 'date-fns';

const EarningsCalendar = () => {
  const { data, isLoading, error } = useEarnings();

  if (isLoading) {
    return (
      <div className="earnings-calendar loading">
        <h3>Upcoming Earnings</h3>
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="earnings-calendar error">
        <h3>Upcoming Earnings</h3>
        <p className="error-message">Failed to load</p>
      </div>
    );
  }

  const earnings = data?.earnings || [];

  if (earnings.length === 0) {
    return (
      <div className="earnings-calendar empty">
        <h3>Upcoming Earnings</h3>
        <p className="no-data">No upcoming earnings</p>
      </div>
    );
  }

  const formatDate = (dateStr) => {
    try {
      const date = parseISO(dateStr);
      return format(date, 'MMM d');
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="earnings-calendar">
      <div className="calendar-header">
        <h3>Upcoming Earnings</h3>
        <span className="earnings-count">{earnings.length}</span>
      </div>

      <div className="earnings-list">
        {earnings.slice(0, 5).map((event, idx) => (
          <div key={`${event.symbol}-${idx}`} className="earnings-item">
            <div className="earnings-date">
              <span className="date">{formatDate(event.earnings_date)}</span>
              <span className="days-until">
                {event.days_until === 0 ? 'Today' :
                 event.days_until === 1 ? 'Tomorrow' :
                 `${event.days_until}d`}
              </span>
            </div>
            <div className="earnings-details">
              <span className="symbol">{event.symbol}</span>
              <span className="name">{event.name}</span>
            </div>
            {event.eps_estimate && (
              <div className="earnings-estimate">
                <span>EPS Est: ${event.eps_estimate.toFixed(2)}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default EarningsCalendar;
