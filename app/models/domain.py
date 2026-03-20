"""Domain models shared across services and UI."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class UniverseMember:
    ticker: str
    name: str
    exchange: str | None
    sector: str | None
    industry: str | None
    source: str


@dataclass(frozen=True, slots=True)
class HistoricalBar:
    ticker: str
    timeframe: str
    bar_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    adjusted_close: float | None
    provider: str
    provider_timezone: str | None
    is_complete: bool = True


@dataclass(frozen=True, slots=True)
class LiveQuote:
    ticker: str
    quote_timestamp: datetime
    last_price: float
    bid: float | None
    ask: float | None
    provider: str


@dataclass(frozen=True, slots=True)
class RangeDetectionResult:
    qualifies: bool
    rejection_reason: str | None
    scan_date: date
    lookback_bars: int
    upper_bound: float
    lower_bound: float
    support_zone_low: float
    support_zone_high: float
    resistance_zone_low: float
    resistance_zone_high: float
    midline: float
    range_width: float
    atr_14: float
    latest_close: float
    touch_count_support: int
    touch_count_resistance: int
    containment_ratio: float
    drift_to_range_ratio: float
    has_recent_breakout: bool
    normalized_sma_20_slope: float
    adx_14: float
    rsi_14: float | None


@dataclass(frozen=True, slots=True)
class ScoreBreakdown:
    range_score: float
    range_validity_score: float
    tradeability_score: float
    opportunity_score: float
    touch_quality_score: float
    trend_weakness_score: float
    containment_quality_score: float
    width_vs_atr_score: float
    liquidity_score: float
    opportunity_location_score: float


@dataclass(frozen=True, slots=True)
class SetupResult:
    setup_direction: str
    setup_status: str
    trigger_bar_date: date
    entry_low: float
    entry_high: float
    stop_price: float
    target_1_price: float
    target_2_price: float
    rsi_14: float | None
    rejection_signal: str | None
    notes: str | None


@dataclass(frozen=True, slots=True)
class ScanSummary:
    timeframe: str
    scan_started_at: datetime
    scan_completed_at: datetime
    scan_bar_date: date
    stocks_processed: int
    candles_ingested: int
    indicators_computed: int
    ranges_detected: int
    scores_generated: int
    setups_generated: int
