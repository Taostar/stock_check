"""Pydantic models for holdings data."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Holding(BaseModel):
    """Represents a single stock holding."""

    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(default="", description="Company name")
    shares: float = Field(default=0.0, description="Number of shares held")
    average_cost: Optional[float] = Field(default=None, description="Average cost basis per share")
    current_price: Optional[float] = Field(default=None, description="Current market price")
    market_value: Optional[float] = Field(default=None, description="Total market value of holding")
    sector: Optional[str] = Field(default=None, description="Stock sector")


class HoldingsResponse(BaseModel):
    """Response model for holdings endpoint."""

    holdings: list[Holding]
    total_value: Optional[float] = Field(default=None, description="Total portfolio value")
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(default="ngrok", description="Data source")


class HoldingPerformance(BaseModel):
    """Holding with performance metrics."""

    symbol: str
    name: str
    shares: float
    current_price: Optional[float]
    previous_close: Optional[float]
    change_amount: Optional[float] = Field(default=None, description="Dollar change")
    change_percent: Optional[float] = Field(default=None, description="Percentage change")
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    volume: Optional[int] = None
    market_value: Optional[float] = None
    is_high_fluctuation: bool = Field(default=False, description="Whether stock meets fluctuation threshold")


class PerformanceResponse(BaseModel):
    """Response model for holdings with performance data."""

    holdings: list[HoldingPerformance]
    high_fluctuation_count: int = Field(default=0)
    total_value: Optional[float] = None
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
