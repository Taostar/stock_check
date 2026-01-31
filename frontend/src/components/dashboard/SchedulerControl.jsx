/**
 * Scheduler control component
 */

import React from 'react';
import { useScheduler } from '../../hooks/useAgent';
import { format, parseISO } from 'date-fns';

const SchedulerControl = () => {
  const { status, isLoading, start, stop, trigger, isTriggering } = useScheduler();

  if (isLoading || !status) {
    return (
      <div className="scheduler-control loading">
        <span>Loading scheduler status...</span>
      </div>
    );
  }

  const formatNextRun = (dateStr) => {
    if (!dateStr) return 'Not scheduled';
    try {
      const date = parseISO(dateStr);
      return format(date, 'h:mm a');
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="scheduler-control">
      <div className="scheduler-status">
        <span className={`status-indicator ${status.running ? 'active' : 'inactive'}`}>
          {status.running ? 'ON' : 'OFF'}
        </span>
        <span className="status-label">Scheduler</span>
      </div>

      <div className="scheduler-info">
        {status.running && status.next_run && (
          <span className="next-run">
            Next: {formatNextRun(status.next_run)}
          </span>
        )}
        {status.last_run && (
          <span className="last-run">
            Last: {formatNextRun(status.last_run)}
          </span>
        )}
      </div>

      <div className="scheduler-actions">
        {status.running ? (
          <button
            className="btn-secondary"
            onClick={() => stop()}
          >
            Stop
          </button>
        ) : (
          <button
            className="btn-secondary"
            onClick={() => start()}
          >
            Start
          </button>
        )}

        <button
          className="btn-primary"
          onClick={() => trigger()}
          disabled={isTriggering}
        >
          {isTriggering ? 'Running...' : 'Run Now'}
        </button>
      </div>
    </div>
  );
};

export default SchedulerControl;
