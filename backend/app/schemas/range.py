from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class PriceZone(BaseModel):
    low: Decimal
    high: Decimal


class TouchCounts(BaseModel):
    support: int
    resistance: int


class SetupSummary(BaseModel):
    direction: str
    status: str
    entry_zone_low: Decimal
    entry_zone_high: Decimal
    stop_price: Decimal
    target_1: Decimal
    target_2: Decimal
    rejection_signal: str | None = None


class RangeListItem(BaseModel):
    ticker: str
    name: str
    as_of_date: date
    range_score: Decimal
    range_validity_score: Decimal
    tradeability_score: Decimal
    opportunity_score: Decimal
    upper_bound: Decimal
    lower_bound: Decimal
    midline: Decimal
    support_zone: PriceZone
    resistance_zone: PriceZone
    touch_counts: TouchCounts
    containment_ratio: Decimal
    atr_14: Decimal | None
    adx_14: Decimal | None
    latest_close: Decimal
    active_setup: SetupSummary | None


class IndicatorPayload(BaseModel):
    adx_14: Decimal | None
    atr_14: Decimal | None
    rsi_14: Decimal | None
    sma_20: Decimal | None
    sma_20_slope: Decimal | None
    avg_dollar_volume_20: Decimal | None = None


class ScoreComponents(BaseModel):
    touch_quality: Decimal
    trend_weakness: Decimal
    containment_quality: Decimal
    range_width: Decimal
    liquidity: Decimal
    current_opportunity_location: Decimal


class ScorePayload(BaseModel):
    range_score: Decimal
    range_validity_score: Decimal
    tradeability_score: Decimal
    opportunity_score: Decimal
    components: ScoreComponents


class RangePayload(BaseModel):
    qualified: bool
    lookback_days: int
    upper_bound: Decimal
    lower_bound: Decimal
    midline: Decimal
    width: Decimal
    width_atr_multiple: Decimal
    support_zone: PriceZone
    resistance_zone: PriceZone
    touch_counts: TouchCounts
    containment_ratio: Decimal


class CandlePayload(BaseModel):
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


class RangeDetailResponse(BaseModel):
    ticker: str
    name: str
    as_of_date: date
    latest_close: Decimal
    range: RangePayload
    indicators: IndicatorPayload
    scores: ScorePayload
    setup: SetupSummary | None
    recent_candles: list[CandlePayload]


class OpportunityListItem(BaseModel):
    ticker: str
    as_of_date: date
    direction: str
    opportunity_score: Decimal
    latest_close: Decimal
    entry_zone_low: Decimal
    entry_zone_high: Decimal
    stop_price: Decimal
    target_1: Decimal
    target_2: Decimal


class AlertListItem(BaseModel):
    id: int
    ticker: str
    created_at: datetime
    alert_type: str
    direction: str | None
    message: str
    related_range_score: Decimal | None
