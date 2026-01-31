"""FastAPI application with AI Investment Agent."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import stocks_router, holdings_router, agent_router, scheduler_router
from .scheduler import get_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    settings = get_settings()

    # Start scheduler if enabled
    if settings.scheduler_enabled:
        scheduler = get_scheduler()
        scheduler.start()
        print(f"[Startup] Scheduler started with cron: {settings.scheduler_cron}")

    yield

    # Shutdown scheduler
    if settings.scheduler_enabled:
        scheduler = get_scheduler()
        scheduler.stop()
        print("[Shutdown] Scheduler stopped")


app = FastAPI(
    title="Stock Check API",
    description="AI-powered investment portfolio analysis",
    version="0.2.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stocks_router)
app.include_router(holdings_router)
app.include_router(agent_router)
app.include_router(scheduler_router)


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Stock Check API",
        "version": "0.2.0",
        "docs": "/docs",
        "endpoints": {
            "stocks": "/api/stock/{ticker}",
            "history": "/api/history/{ticker}",
            "compare": "/api/compare",
            "holdings": "/api/holdings",
            "holdings_performance": "/api/holdings/performance",
            "agent_analyze": "/api/agent/analyze",
            "agent_summary": "/api/agent/summary",
            "scheduler_status": "/api/scheduler/status"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    settings = get_settings()
    scheduler = get_scheduler()

    return {
        "status": "healthy",
        "scheduler_enabled": settings.scheduler_enabled,
        "scheduler_running": scheduler.is_running(),
        "llm_provider": settings.llm_provider,
        "llm_configured": bool(
            settings.openai_api_key or
            settings.anthropic_api_key or
            settings.local_llm_url
        )
    }
