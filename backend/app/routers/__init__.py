"""API routers for the application."""

from .stocks import router as stocks_router
from .holdings import router as holdings_router
from .agent import router as agent_router
from .scheduler import router as scheduler_router

__all__ = [
    "stocks_router",
    "holdings_router",
    "agent_router",
    "scheduler_router",
]
