/**
 * API client for the Stock Check backend
 */

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Holdings API
export const holdingsApi = {
  /**
   * Fetch holdings from the configured endpoint
   */
  getHoldings: (useMock = false) =>
    fetchApi(`/holdings${useMock ? '?use_mock=true' : ''}`),

  /**
   * Fetch holdings with performance data
   */
  getPerformance: (useMock = false) =>
    fetchApi(`/holdings/performance${useMock ? '?use_mock=true' : ''}`),

  /**
   * Get high-fluctuation stocks
   */
  getFluctuations: (useMock = false) =>
    fetchApi(`/holdings/fluctuations${useMock ? '?use_mock=true' : ''}`),
};

// Agent API
export const agentApi = {
  /**
   * Trigger a full portfolio analysis
   */
  analyze: (options = {}) =>
    fetchApi('/agent/analyze', {
      method: 'POST',
      body: JSON.stringify({
        force_refresh: options.forceRefresh || false,
        include_news: options.includeNews !== false,
        include_earnings: options.includeEarnings !== false,
      }),
    }),

  /**
   * Get the latest AI summary
   */
  getSummary: () => fetchApi('/agent/summary'),

  /**
   * Get fluctuation alerts from last analysis
   */
  getFluctuations: () => fetchApi('/agent/fluctuations'),

  /**
   * Get earnings from last analysis
   */
  getEarnings: () => fetchApi('/agent/earnings'),

  /**
   * Get news from last analysis
   */
  getNews: () => fetchApi('/agent/news'),

  /**
   * Get analysis status
   */
  getStatus: () => fetchApi('/agent/status'),
};

// Scheduler API
export const schedulerApi = {
  /**
   * Get scheduler status
   */
  getStatus: () => fetchApi('/scheduler/status'),

  /**
   * Start the scheduler
   */
  start: () => fetchApi('/scheduler/start', { method: 'POST' }),

  /**
   * Stop the scheduler
   */
  stop: () => fetchApi('/scheduler/stop', { method: 'POST' }),

  /**
   * Trigger immediate analysis
   */
  trigger: () => fetchApi('/scheduler/trigger', { method: 'POST' }),
};

// Stocks API (existing)
export const stocksApi = {
  /**
   * Get stock info
   */
  getStock: (ticker) => fetchApi(`/stock/${ticker}`),

  /**
   * Get stock history
   */
  getHistory: (ticker, period = '1mo') =>
    fetchApi(`/history/${ticker}?period=${period}`),

  /**
   * Compare multiple stocks
   */
  compare: (tickers, period = '1mo') =>
    fetchApi('/compare', {
      method: 'POST',
      body: JSON.stringify({ tickers, period }),
    }),
};

export default {
  holdings: holdingsApi,
  agent: agentApi,
  scheduler: schedulerApi,
  stocks: stocksApi,
};
