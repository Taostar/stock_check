"""Pydantic models for analysis data."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FluctuationAlert(BaseModel):
    """Alert for high-fluctuation stocks."""

    symbol: str
    name: str
    change_percent: float
    change_amount: Optional[float] = None
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    direction: str = Field(description="up or down")
    volume: Optional[int] = None


class EarningsEvent(BaseModel):
    """Upcoming earnings event."""

    symbol: str
    name: str
    earnings_date: datetime
    time_of_day: Optional[str] = Field(default=None, description="before market, after market, etc.")
    eps_estimate: Optional[float] = None
    revenue_estimate: Optional[float] = None
    days_until: int = Field(description="Days until earnings")


class NewsItem(BaseModel):
    """News article item."""

    symbol: str
    title: str
    publisher: str
    link: str
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    thumbnail_url: Optional[str] = None


class AnalysisResult(BaseModel):
    """Complete analysis result."""

    fluctuation_alerts: list[FluctuationAlert] = Field(default_factory=list)
    upcoming_earnings: list[EarningsEvent] = Field(default_factory=list)
    news_items: list[NewsItem] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    holdings_count: int = 0
    high_fluctuation_count: int = 0
