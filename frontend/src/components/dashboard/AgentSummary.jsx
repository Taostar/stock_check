/**
 * AI-generated summary component
 */

import React, { useState } from 'react';
import { useSummary } from '../../hooks/useAgent';

const AgentSummary = () => {
  const [isExpanded, setIsExpanded] = useState(true);
  const { data: summary, isLoading, error } = useSummary();

  if (isLoading) {
    return (
      <div className="agent-summary loading">
        <div className="summary-header">
          <h3>AI Summary</h3>
        </div>
        <div className="summary-content">
          <p>Loading summary...</p>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="agent-summary empty">
        <div className="summary-header">
          <h3>AI Summary</h3>
        </div>
        <div className="summary-content">
          <p className="no-data">No analysis available. Click "Analyze Now" to generate insights.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`agent-summary ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div
        className="summary-header"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{ cursor: 'pointer' }}
      >
        <h3>AI Summary</h3>
        <span className="toggle">{isExpanded ? '-' : '+'}</span>
      </div>

      {isExpanded && (
        <div className="summary-content">
          <p className="main-summary">{summary.summary}</p>

          {summary.key_insights && summary.key_insights.length > 0 && (
            <div className="insights-section">
              <h4>Key Insights</h4>
              <ul>
                {summary.key_insights.map((insight, idx) => (
                  <li key={idx}>{insight}</li>
                ))}
              </ul>
            </div>
          )}

          {summary.recommendations && summary.recommendations.length > 0 && (
            <div className="recommendations-section">
              <h4>Recommendations</h4>
              <ul>
                {summary.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {summary.risk_factors && summary.risk_factors.length > 0 && (
            <div className="risks-section">
              <h4>Risk Factors</h4>
              <ul>
                {summary.risk_factors.map((risk, idx) => (
                  <li key={idx}>{risk}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="summary-meta">
            <span>Model: {summary.model_used || 'N/A'}</span>
            <span>Generated: {summary.generated_at ? new Date(summary.generated_at).toLocaleString() : 'N/A'}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentSummary;
