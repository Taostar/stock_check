/**
 * Custom hook for polling/auto-refresh functionality
 */

import { useEffect, useRef, useCallback } from 'react';

/**
 * Hook to poll a function at regular intervals
 *
 * @param {Function} callback - Function to call on each interval
 * @param {number} interval - Interval in milliseconds
 * @param {boolean} enabled - Whether polling is enabled
 */
export function usePolling(callback, interval, enabled = true) {
  const savedCallback = useRef(callback);

  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) return;

    const tick = () => {
      savedCallback.current();
    };

    // Call immediately
    tick();

    // Then set up interval
    const id = setInterval(tick, interval);

    return () => clearInterval(id);
  }, [interval, enabled]);
}

/**
 * Hook for auto-refresh with manual refresh capability
 *
 * @param {Function} fetchFn - Function to fetch data
 * @param {number} interval - Refresh interval in milliseconds
 * @param {boolean} autoRefresh - Whether to auto-refresh
 */
export function useAutoRefresh(fetchFn, interval = 30000, autoRefresh = true) {
  const refresh = useCallback(() => {
    fetchFn();
  }, [fetchFn]);

  usePolling(refresh, interval, autoRefresh);

  return { refresh };
}

export default usePolling;
