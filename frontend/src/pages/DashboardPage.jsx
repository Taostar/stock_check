/**
 * AI Investment Dashboard page
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useAnalysis } from '../hooks/useAgent';
import AgentSummary from '../components/dashboard/AgentSummary';
import HoldingsTable from '../components/dashboard/HoldingsTable';
import FluctuationAlerts from '../components/dashboard/FluctuationAlerts';
import EarningsCalendar from '../components/dashboard/EarningsCalendar';
import NewsPanel from '../components/dashboard/NewsPanel';
import SchedulerControl from '../components/dashboard/SchedulerControl';

function DashboardPage() {
  const { analyze, isAnalyzing, status, error } = useAnalysis();

  const handleAnalyze = () => {
    analyze({ forceRefresh: true });
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>AI Investment Dashboard</h1>
          <nav className="main-nav">
            <Link to="/" className="nav-link">Stock Compare</Link>
          </nav>
        </div>
        <div className="header-actions">
          <button
            className="btn-primary analyze-btn"
            onClick={handleAnalyze}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? 'Analyzing...' : 'Analyze Now'}
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          Analysis failed: {error.message}
        </div>
      )}

      <main className="dashboard-main">
        {/* AI Summary Section */}
        <section className="dashboard-section summary-section">
          <AgentSummary />
        </section>

        {/* Alerts Row */}
        <section className="dashboard-section alerts-row">
          <div className="alerts-col">
            <FluctuationAlerts />
          </div>
          <div className="alerts-col">
            <EarningsCalendar />
          </div>
        </section>

        {/* Holdings Table */}
        <section className="dashboard-section holdings-section">
          <HoldingsTable />
        </section>

        {/* News Panel */}
        <section className="dashboard-section news-section">
          <NewsPanel />
        </section>

        {/* Scheduler Control */}
        <section className="dashboard-section scheduler-section">
          <SchedulerControl />
        </section>
      </main>

      <footer className="dashboard-footer">
        {status?.last_analyzed && (
          <span>Last analysis: {new Date(status.last_analyzed).toLocaleString()}</span>
        )}
        {status?.holdings_count > 0 && (
          <span>{status.holdings_count} holdings tracked</span>
        )}
      </footer>
    </div>
  );
}

export default DashboardPage;
