from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class UniverseMember:
    ticker: str
    name: str
    exchange: str | None = None
    sector: str | None = None
    industry: str | None = None
    source: str = "local_seed"


@dataclass(slots=True)
class DailyBar:
    ticker: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float | None = None
    vwap: float | None = None
    data_source: str = "local_seed"
    is_adjusted_series: bool = False
