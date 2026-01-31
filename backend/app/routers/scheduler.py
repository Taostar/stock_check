"""Scheduler control endpoints."""

from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime

from ..models.agent import SchedulerStatus
from ..scheduler import get_scheduler, AnalysisScheduler

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


def _get_scheduler() -> AnalysisScheduler:
    """Get the global scheduler instance."""
    return get_scheduler()


@router.get("/status", response_model=SchedulerStatus)
async def get_scheduler_status():
    """Get the current scheduler status."""
    scheduler = _get_scheduler()
    return scheduler.get_status()


@router.post("/start")
async def start_scheduler():
    """Start the scheduler if not already running."""
    scheduler = _get_scheduler()

    if scheduler.is_running():
        return {
            "status": "already_running",
            "message": "Scheduler is already running"
        }

    scheduler.start()

    return {
        "status": "started",
        "message": "Scheduler started successfully",
        "next_run": scheduler.get_next_run_time()
    }


@router.post("/stop")
async def stop_scheduler():
    """Stop the scheduler."""
    scheduler = _get_scheduler()

    if not scheduler.is_running():
        return {
            "status": "already_stopped",
            "message": "Scheduler is not running"
        }

    scheduler.stop()

    return {
        "status": "stopped",
        "message": "Scheduler stopped successfully"
    }


@router.post("/trigger")
async def trigger_analysis():
    """Trigger an immediate analysis run."""
    scheduler = _get_scheduler()

    try:
        await scheduler.run_analysis_now()
        return {
            "status": "triggered",
            "message": "Analysis triggered successfully",
            "triggered_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger analysis: {str(e)}"
        )


@router.put("/cron")
async def update_cron(cron_expression: str):
    """
    Update the scheduler cron expression.

    Note: This only affects the current session, not the .env configuration.
    """
    scheduler = _get_scheduler()

    try:
        scheduler.update_schedule(cron_expression)
        return {
            "status": "updated",
            "message": f"Cron expression updated to: {cron_expression}",
            "next_run": scheduler.get_next_run_time()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cron expression: {str(e)}"
        )
