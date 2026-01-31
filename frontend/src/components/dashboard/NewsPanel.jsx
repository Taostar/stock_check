/**
 * News panel component
 */

import React from 'react';
import { useNews } from '../../hooks/useAgent';
import { format, parseISO, formatDistanceToNow } from 'date-fns';

const NewsPanel = () => {
  const { data, isLoading, error } = useNews();

  if (isLoading) {
    return (
      <div className="news-panel loading">
        <h3>Recent News</h3>
        <p>Loading news...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="news-panel error">
        <h3>Recent News</h3>
        <p className="error-message">Failed to load news</p>
      </div>
    );
  }

  const newsItems = data?.news || [];

  if (newsItems.length === 0) {
    return (
      <div className="news-panel empty">
        <h3>Recent News</h3>
        <p className="no-data">No recent news for flagged stocks</p>
      </div>
    );
  }

  const formatTime = (dateStr) => {
    if (!dateStr) return '';
    try {
      const date = parseISO(dateStr);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch {
      return '';
    }
  };

  return (
    <div className="news-panel">
      <div className="news-header">
        <h3>Recent News</h3>
        <span className="news-count">{newsItems.length} articles</span>
      </div>

      <div className="news-list">
        {newsItems.slice(0, 10).map((news, idx) => (
          <a
            key={`${news.symbol}-${idx}`}
            href={news.link}
            target="_blank"
            rel="noopener noreferrer"
            className="news-item"
          >
            <div className="news-meta">
              <span className="symbol-badge">{news.symbol}</span>
              <span className="publisher">{news.publisher}</span>
              <span className="time">{formatTime(news.published_at)}</span>
            </div>
            <div className="news-title">{news.title}</div>
          </a>
        ))}
      </div>
    </div>
  );
};

export default NewsPanel;
